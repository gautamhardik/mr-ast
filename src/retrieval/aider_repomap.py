"""
Authentic Reproduction of Aider's Repository Map (RepoMap) Baseline for MR-TopoS.

Implements the official PageRank-based repository mapping algorithm from aider/repomap.py:
1. AST definition and reference extraction across all repository files.
2. Directed multi-graph construction (referencing file -> defining file).
3. Non-linear edge weighting with math.sqrt(num_refs) and 10x query identifier multiplier.
4. Personalized PageRank via networkx biased toward query-matching files and identifiers.
5. Rank distribution from file-level PageRank scores to individual symbol definitions.
6. Outline formatting and binary search budget packing against official Gemma 4 tokenizer.
"""

import ast
import math
import re
from collections import Counter, defaultdict
from typing import Callable, Dict, List, Optional, Set, Tuple

import networkx as nx

from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType


class AiderRepoMapBaseline:
    """
    Faithful reproduction of Aider's repository mapping algorithm.
    """

    def __init__(self, tokenizer_fn: Callable[[str], int]):
        self.tokenizer_fn = tokenizer_fn

    def compile(
        self,
        graph: DualViewGraph,
        query: str,
        budget: int
    ) -> Dict:
        """
        Build and format an Aider Repository Map for the given query and token budget.
        """
        # 1. Extract query identifiers
        query_idents = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", query))

        defines = defaultdict(set)
        references = defaultdict(list)
        definitions = defaultdict(list)

        # 2. Populate definitions and references across graph nodes
        for sid, node in graph.nodes.items():
            rel_fname = node.file_path
            ident = node.name

            if node.symbol_type in (SymbolType.CLASS, SymbolType.FUNCTION, SymbolType.METHOD):
                defines[ident].add(rel_fname)
                definitions[(rel_fname, ident)].append(node)

            # Extract identifier references from node raw code
            if node.raw_code:
                try:
                    tree = ast.parse(node.raw_code)
                    for ast_node in ast.walk(tree):
                        if isinstance(ast_node, ast.Name) and isinstance(ast_node.ctx, ast.Load):
                            references[ast_node.id].append(rel_fname)
                except SyntaxError:
                    # Fallback regex for reference extraction if snippet has local syntax quirks
                    words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", node.raw_code)
                    for w in words:
                        references[w].append(rel_fname)

        all_files = sorted(list(set(n.file_path for n in graph.nodes.values())))
        if not all_files:
            return {
                "context_str": "",
                "selected_files": set(),
                "retained_symbols_count": 0,
                "retained_full": 0,
                "retained_skel": 0,
                "retained_stub": 0,
                "actual_tokens": 0,
                "is_compliant": True,
                "syntactic_validity": 1
            }

        # 3. Build Directed Multi-Graph
        G = nx.MultiDiGraph()
        for fname in all_files:
            G.add_node(fname)

        # Self-loops for orphan definitions (Aider fault-tolerance)
        for ident in defines.keys():
            if ident not in references:
                for definer in defines[ident]:
                    G.add_edge(definer, definer, weight=0.1, ident=ident)

        # Edges from referencing files to defining files
        for ident, referencers in references.items():
            if ident not in defines:
                continue
            definers = defines[ident]
            mul = 10.0 if ident in query_idents else 1.0

            for referencer, num_refs in Counter(referencers).items():
                for definer in definers:
                    edge_weight = mul * math.sqrt(num_refs)
                    G.add_edge(referencer, definer, weight=edge_weight, ident=ident)

        # 4. Personalization Vector
        # Bias towards files that contain query keywords or match query identifiers
        personalization = {}
        query_words = set(w.lower() for w in query_idents)
        matching_files = set()
        for fname in all_files:
            fname_lower = fname.lower()
            if any(qw in fname_lower for qw in query_words):
                matching_files.add(fname)

        if matching_files:
            for node_name in G.nodes:
                personalization[node_name] = 1.0 / len(matching_files) if node_name in matching_files else 0.0

        pers_args = dict(personalization=personalization, dangling=personalization) if personalization else {}

        # 5. Execute PageRank via NetworkX
        try:
            ranked = nx.pagerank(G, weight="weight", **pers_args)
        except Exception:
            try:
                ranked = nx.pagerank(G, weight="weight")
            except Exception:
                ranked = {f: 1.0 / len(all_files) for f in all_files}

        # 6. Distribute file-level rank to individual symbol definitions
        ranked_definitions = defaultdict(float)
        for src in G.nodes:
            src_rank = ranked.get(src, 0.0)
            total_weight = sum(data["weight"] for _src, _dst, data in G.out_edges(src, data=True))
            if total_weight == 0:
                continue
            for _src, dst, data in G.out_edges(src, data=True):
                edge_rank = src_rank * data["weight"] / total_weight
                ranked_definitions[(dst, data["ident"])] += edge_rank

        # Fallback if no edge weights: use file rank directly for definitions
        if not ranked_definitions:
            for (fname, ident), nodes in definitions.items():
                ranked_definitions[(fname, ident)] = ranked.get(fname, 0.0)

        # Sort definitions by PageRank score descending
        sorted_defs = sorted(
            ranked_definitions.items(),
            reverse=True,
            key=lambda x: (x[1], x[0])
        )

        # 7. Binary search over top-M definitions to fit budget
        def render_map(top_m: int) -> Tuple[str, Set[str], int]:
            selected_defs = sorted_defs[:top_m]
            file_to_nodes = defaultdict(list)
            seen_sids = set()

            for (fname, ident), _score in selected_defs:
                for node in definitions.get((fname, ident), []):
                    if node.id not in seen_sids:
                        file_to_nodes[fname].append(node)
                        seen_sids.add(node.id)

            sections = []
            selected_fps = set()
            for fname in sorted(file_to_nodes.keys()):
                nodes = file_to_nodes[fname]
                lines = [f"# File: {fname}"]
                selected_fps.add(fname)
                # Render signature outlines
                for node in sorted(nodes, key=lambda n: n.line_start):
                    if node.symbol_type == SymbolType.CLASS:
                        lines.append(f"class {node.name}: ...")
                    elif node.symbol_type == SymbolType.METHOD:
                        lines.append(f"    def {node.name}(...): ...")
                    elif node.symbol_type == SymbolType.FUNCTION:
                        lines.append(f"def {node.name}(...): ...")
                sections.append("\n".join(lines))

            ctx = "\n\n".join(sections)
            return ctx, selected_fps, len(seen_sids)

        low = 1
        high = len(sorted_defs)
        best_ctx = ""
        best_files = set()
        best_sym_count = 0
        best_tokens = 0

        while low <= high:
            mid = (low + high) // 2
            candidate_ctx, fps, sym_count = render_map(mid)
            toks = self.tokenizer_fn(candidate_ctx)
            if toks <= budget:
                best_ctx = candidate_ctx
                best_files = fps
                best_sym_count = sym_count
                best_tokens = toks
                low = mid + 1
            else:
                high = mid - 1

        is_valid = 1
        try:
            if best_ctx.strip():
                ast.parse(best_ctx)
        except SyntaxError:
            is_valid = 0

        return {
            "context_str": best_ctx,
            "selected_files": best_files,
            "retained_symbols_count": best_sym_count,
            "retained_full": 0,  # Aider repo map emits signature outlines (skeletons/stubs), not full implementations
            "retained_skel": best_sym_count,
            "retained_stub": 0,
            "actual_tokens": best_tokens,
            "is_compliant": (best_tokens <= budget),
            "syntactic_validity": is_valid
        }

