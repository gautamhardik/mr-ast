import re
from typing import List, Dict, Any, Set
from rank_bm25 import BM25Okapi

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

def tokenize_code_text(text: str) -> List[str]:
    """Tokenizes code or query text, handling camelCase, snake_case, and punctuation."""
    if not text:
        return []
    # Split on snake_case and non-alphanumeric characters
    raw_tokens = re.findall(r'[A-Za-z0-9]+', text)
    tokens: List[str] = []
    for token in raw_tokens:
        # Split camelCase (e.g., HTTPConnection -> HTTP, Connection)
        sub_tokens = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)|\d+', token)
        if sub_tokens:
            for st in sub_tokens:
                st_lower = st.lower()
                if len(st_lower) > 1 and st_lower not in STOP_WORDS:
                    tokens.append(st_lower)
        else:
            token_lower = token.lower()
            if len(token_lower) > 1 and token_lower not in STOP_WORDS:
                tokens.append(token_lower)
    return tokens


def node_id_to_file_candidates(node_id: str) -> List[str]:
    """Infers potential relative file paths from dotted symbol ID, handling src/ layout."""
    parts = node_id.split('.')
    candidates = []
    # Direct relative path: e.g. fastapi/routing.py
    for i in range(1, len(parts)):
        path = "/".join(parts[:i]) + ".py"
        candidates.append(path)
        # Also support src/ layout common in modern python repos (requests, httpx)
        candidates.append("src/" + path)
    return candidates


class LexicalGraphIndex:
    """Offline BM25 index over code graph AST nodes."""
    
    def __init__(self, nodes: List[Dict[str, Any]]):
        self.nodes = nodes
        self.corpus: List[List[str]] = []
        
        for node in nodes:
            name_tokens = tokenize_code_text(node.get("name", ""))
            # Repeat name tokens to give higher term frequency / weight to exact symbol names
            weighted_name_tokens = name_tokens * 3
            body_text = node.get("text", "")[:1000] # Cap text per node to keep indexing efficient
            body_tokens = tokenize_code_text(body_text)
            doc_tokens = weighted_name_tokens + body_tokens
            if not doc_tokens:
                doc_tokens = ["empty"]
            self.corpus.append(doc_tokens)
            
        self.bm25 = BM25Okapi(self.corpus)

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Searches BM25 corpus and returns top-k ranked node objects with scores."""
        query_tokens = tokenize_code_text(query)
        if not query_tokens:
            return []
        
        scores = self.bm25.get_scores(query_tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0.0:
                continue
            node = self.nodes[idx]
            results.append({
                "id": node["id"],
                "name": node.get("name", ""),
                "score": score,
                "file_candidates": node_id_to_file_candidates(node["id"])
            })
        return results
