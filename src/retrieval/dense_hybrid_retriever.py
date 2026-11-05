"""
Dense-Lexical Hybrid AST Retriever for MR-AST.

Fuses precomputed dense symbol embeddings (256-dim) with lexical BM25 rankings:
    u_i(lambda) = (1 - lambda) * s_norm_bm25(i) + lambda * s_norm_dense(i)

Provides candidate symbols with dense semantic coverage to the MCKP optimizer.
"""

import os
import glob
import numpy as np
from typing import Dict, List, Optional, Tuple
from rank_bm25 import BM25Okapi

from src.retrieval.lexical_index import tokenize_code_text


class DenseHybridRetriever:
    """
    Hybrid retriever combining lexical BM25 and precomputed dense embeddings.
    """

    def __init__(self, embeddings_dir: str = "DATA/embeddings"):
        self.embeddings_dir = os.path.abspath(embeddings_dir)
        self.embeddings_cache: Dict[str, Dict[str, np.ndarray]] = {}

    def load_embeddings_for_repo(self, repo: str, base_commit: str) -> Dict[str, np.ndarray]:
        """
        Load precomputed symbol embeddings for a specific repository and commit snapshot.
        """
        cache_key = f"{repo}_{base_commit}"
        if cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]

        repo_prefix = repo.split("/")[-1]
        pattern = os.path.join(self.embeddings_dir, f"{repo_prefix}_{base_commit}*.npz")
        matches = glob.glob(pattern)

        if not matches:
            # Fallback to any matching repo prefix
            pattern = os.path.join(self.embeddings_dir, f"{repo_prefix}_*.npz")
            matches = glob.glob(pattern)

        if not matches:
            return {}

        npz_path = matches[0]
        data = np.load(npz_path)
        embeddings = {k: data[k] for k in data.files}
        self.embeddings_cache[cache_key] = embeddings
        return embeddings

    def compute_dense_similarity(
        self, query_tokens: List[str], symbol_embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Compute dense semantic similarity between query pseudo-vector and symbol embeddings.
        """
        if not symbol_embeddings:
            return {}

        # Pseudo-query representation: aggregate top-matching symbol embeddings or uniform query vector
        # If query tokens match symbol names, use centroid; else use projected mean
        all_vecs = list(symbol_embeddings.values())
        dim = all_vecs[0].shape[0]

        matched_vecs = []
        for q in query_tokens:
            q_lower = q.lower()
            for name, vec in symbol_embeddings.items():
                if q_lower in name.lower():
                    matched_vecs.append(vec)
                    if len(matched_vecs) >= 10:
                        break

        if matched_vecs:
            query_vec = np.mean(matched_vecs, axis=0)
        else:
            query_vec = np.mean(all_vecs[:20], axis=0)

        # Normalize query vector
        norm_q = np.linalg.norm(query_vec)
        if norm_q > 0:
            query_vec = query_vec / norm_q

        # Cosine similarity for each symbol
        dense_scores = {}
        for name, vec in symbol_embeddings.items():
            norm_v = np.linalg.norm(vec)
            if norm_v > 0:
                score = float(np.dot(query_vec, vec) / norm_v)
            else:
                score = 0.0
            dense_scores[name] = max(0.0, score)

        return dense_scores

    def rank_hybrid(
        self,
        query: str,
        corpus_symbols: Dict[str, str],  # symbol_id -> code/doc text
        repo: str,
        base_commit: str,
        lambda_weight: float = 0.3,
        top_k: int = 100,
    ) -> List[Tuple[str, float]]:
        """
        Compute hybrid scores: (1 - lambda) * BM25 + lambda * Dense.
        """
        symbol_ids = list(corpus_symbols.keys())
        if not symbol_ids:
            return []

        # 1. Lexical BM25
        tokenized_corpus = [tokenize_code_text(corpus_symbols[sid]) for sid in symbol_ids]
        bm25 = BM25Okapi(tokenized_corpus)
        query_tokens = tokenize_code_text(query)
        bm25_raw_scores = bm25.get_scores(query_tokens)

        # Normalize BM25
        max_bm25 = float(np.max(bm25_raw_scores)) if len(bm25_raw_scores) > 0 and np.max(bm25_raw_scores) > 0 else 1.0
        norm_bm25 = {sid: float(score) / max_bm25 for sid, score in zip(symbol_ids, bm25_raw_scores)}

        # 2. Dense Embeddings
        symbol_embeddings = self.load_embeddings_for_repo(repo, base_commit)
        dense_raw_scores = self.compute_dense_similarity(query_tokens, symbol_embeddings)

        max_dense = float(max(dense_raw_scores.values())) if dense_raw_scores and max(dense_raw_scores.values()) > 0 else 1.0
        norm_dense = {sid: dense_raw_scores.get(sid, 0.0) / max_dense for sid in symbol_ids}

        # 3. Fuse scores
        hybrid_scores = []
        for sid in symbol_ids:
            s_lex = norm_bm25.get(sid, 0.0)
            s_dense = norm_dense.get(sid, 0.0)
            score = (1.0 - lambda_weight) * s_lex + lambda_weight * s_dense
            hybrid_scores.append((sid, score))

        # Sort descending by score
        hybrid_scores.sort(key=lambda x: x[1], reverse=True)
        return hybrid_scores[:top_k]

