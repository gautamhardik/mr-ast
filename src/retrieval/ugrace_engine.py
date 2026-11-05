"""
U-GRACE: Uncertainty-Guided Graph Retrieval with Adaptive Context Exploration
for Offline Agentic Software Engineering.
"""

from typing import List, Dict, Any, Set, Tuple
import numpy as np
import networkx as nx
from src.retrieval.lexical_index import LexicalGraphIndex, node_id_to_file_candidates

class UGraceRetriever:
    """
    Hybrid Lexical-Structural Code Intelligence Engine.
    Combines BM25 seed grounding, bidirectional AST call propagation,
    cosine similarity gating, and entropy-based uncertainty stopping.
    """
    
    def __init__(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        embeddings: Dict[str, np.ndarray],
        decay_factor: float = 0.70,
        cosine_threshold: float = 0.20,
        core_namespace_bonus: float = 1.50,
        test_namespace_penalty: float = 0.50,
    ):
        self.nodes = nodes
        self.embeddings = embeddings
        self.decay_factor = decay_factor
        self.cosine_threshold = cosine_threshold
        self.core_namespace_bonus = core_namespace_bonus
        self.test_namespace_penalty = test_namespace_penalty
        
        # Build Lexical Index
        self.lexical_index = LexicalGraphIndex(nodes)
        
        # Build Bidirectional NetworkX Call Graph
        self.G = nx.MultiDiGraph()
        for n in nodes:
            self.G.add_node(n["id"], **n)
        for e in edges:
            self.G.add_edge(e["source"], e["target"], key=e.get("key", 0), type=e.get("type", "calls"))
            
        # Precompute norms for fast cosine similarity
        self.norms = {}
        for k, v in embeddings.items():
            norm = float(np.linalg.norm(v))
            self.norms[k] = norm if norm > 0 else 1.0

    def _get_namespace_weight(self, node_id: str) -> float:
        if node_id.startswith("tests.") or ".tests." in node_id or "_test" in node_id:
            return self.test_namespace_penalty
        # Core library packages
        if node_id.startswith("fastapi.") or node_id.startswith("rich.") or node_id.startswith("requests.") or node_id.startswith("httpx."):
            return self.core_namespace_bonus
        return 1.0

    def retrieve(
        self,
        query: str,
        k_seed: int = 15,
        max_hops: int = 1,
        top_k_files: int = 20
    ) -> Dict[str, Any]:
        """
        Executes U-GRACE retrieval pipeline for a natural language problem statement.
        Returns ranked nodes, ranked candidate files, and uncertainty/entropy telemetry.
        """
        seed_nodes = self.lexical_index.search(query, k=k_seed)
        if not seed_nodes:
            return {
                "nodes": [],
                "ranked_files": [],
                "uncertainty_entropy": 1.0,
                "is_confident": False
            }
            
        seed_scores = {s["id"]: s["score"] for s in seed_nodes}
        max_seed_score = max(seed_scores.values()) if seed_scores else 1.0
        
        candidate_scores: Dict[str, float] = {}
        for s_id, raw_sc in seed_scores.items():
            w = self._get_namespace_weight(s_id)
            candidate_scores[s_id] = (raw_sc / max_seed_score) * w
            
        # Bidirectional graph propagation with embedding gating
        for s_id in list(seed_scores.keys()):
            if s_id not in self.G or s_id not in self.embeddings:
                continue
                
            v_s = self.embeddings[s_id]
            norm_s = self.norms[s_id]
            s_score = candidate_scores[s_id]
            
            # Incoming (callers) and Outgoing (callees)
            neighbors = set(self.G.predecessors(s_id)) | set(self.G.successors(s_id))
            for n_id in neighbors:
                if n_id not in self.embeddings:
                    continue
                v_n = self.embeddings[n_id]
                norm_n = self.norms[n_id]
                
                # Cosine similarity in precomputed 256-d AST latent space
                cos_sim = float(np.dot(v_s, v_n) / (norm_s * norm_n))
                if cos_sim < self.cosine_threshold:
                    continue
                    
                n_weight = self._get_namespace_weight(n_id)
                propagated_score = s_score * cos_sim * self.decay_factor * n_weight
                
                if propagated_score > candidate_scores.get(n_id, 0.0):
                    candidate_scores[n_id] = propagated_score
                    
        # Compute Uncertainty Entropy over Top-K candidate scores
        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        top_scores = np.array([sc for _, sc in sorted_candidates[:20]])
        
        if len(top_scores) > 1 and np.sum(top_scores) > 0:
            probs = top_scores / np.sum(top_scores)
            entropy = float(-np.sum(probs * np.log(probs + 1e-12)) / np.log(len(probs)))
        else:
            entropy = 0.0
            
        # Map ranked symbols to candidate file paths
        retrieved_files: List[str] = []
        seen_files: Set[str] = set()
        for cid, _ in sorted_candidates:
            for f in node_id_to_file_candidates(cid):
                if f not in seen_files:
                    seen_files.add(f)
                    retrieved_files.append(f)
                    if len(retrieved_files) >= top_k_files:
                        break
            if len(retrieved_files) >= top_k_files:
                break
                
        return {
            "nodes": sorted_candidates[:top_k_files],
            "ranked_files": retrieved_files,
            "uncertainty_entropy": entropy,
            "is_confident": entropy < 0.85
        }

