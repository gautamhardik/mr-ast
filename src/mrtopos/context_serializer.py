"""
Canonical Context Serializer with Strict Subword Budget Guard for MR-TopoS.

Serializes DualViewGraph nodes at selected resolution tiers into clean,
syntactically coherent Python source files with strict subword token budget enforcement.
Guarantees 100% zero token budget violations against the official Gemma 4 tokenizer.
"""

import ast
import textwrap
from typing import Callable, Dict, List, Optional, Set, Tuple
from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType


class ContextSerializer:
    """
    Serializes multi-resolution topology graphs into formatted agent context.
    
    Guarantees:
    1. Scope preservation: Child methods are wrapped with proper class indentation.
    2. File structure: Clear file boundary headers (# File: {path}).
    3. Strict Budget Guard: Measures exact subword tokens with Gemma 4 tokenizer.
       If formatting overhead causes tokens > budget, deterministically prunes
       lowest-utility STUB/SKELETON nodes until tokens <= budget.
    """

    def __init__(self, tokenizer_fn: Callable[[str], int]):
        """
        Args:
            tokenizer_fn: Function mapping text string to exact subword token count.
        """
        self.tokenizer_fn = tokenizer_fn

    def serialize(
        self,
        graph: DualViewGraph,
        selected_tiers: Dict[str, ResolutionTier],
        budget: int,
        utilities: Optional[Dict[str, float]] = None
    ) -> Tuple[str, Dict]:
        """
        Serialize graph nodes at their selected tiers into a unified context string.

        Args:
            graph: The DualViewGraph containing symbol and module definitions.
            selected_tiers: Mapping from symbol_id to ResolutionTier.
            budget: Maximum allowable subword tokens.
            utilities: Optional dictionary of symbol utilities for budget-trimming priority.

        Returns:
            Tuple of (serialized_context_text, metadata_dict).
        """
        utils = utilities or {}

        # Filter out EXCLUDED nodes
        active_tiers = {
            sid: tier for sid, tier in selected_tiers.items()
            if tier != ResolutionTier.EXCLUDED and sid in graph.nodes
        }

        # Initial serialization attempt
        context_str, included_sids = self._assemble_context(graph, active_tiers)
        raw_tokens = self.tokenizer_fn(context_str)

        trimmed_count = 0

        # Strict Multi-Stage Monotonic Budget Guard (Atomic Symbol Pruning)
        # Guarantees tokens <= budget while eliminating line truncation across syntax blocks
        while raw_tokens > budget:
            active_sids = [sid for sid, tier in active_tiers.items() if tier != ResolutionTier.EXCLUDED]
            if not active_sids:
                # Pathological boundary: Even 0 symbols exceed budget, fallback to clean line truncate
                context_str = self._line_truncate_to_budget(context_str, budget)
                raw_tokens = self.tokenizer_fn(context_str)
                break

            # Stage 1: Downgrade lowest-utility STUB -> EXCLUDED
            stubs = [sid for sid in active_sids if active_tiers[sid] == ResolutionTier.STUB]
            if stubs:
                target_sid = min(stubs, key=lambda sid: utils.get(sid, 0.0))
                active_tiers[target_sid] = ResolutionTier.EXCLUDED
                trimmed_count += 1
                context_str, included_sids = self._assemble_context(graph, active_tiers)
                raw_tokens = self.tokenizer_fn(context_str)
                continue

            # Stage 2: Downgrade lowest-utility SKELETON -> STUB
            skeletons = [sid for sid in active_sids if active_tiers[sid] == ResolutionTier.SKELETON]
            if skeletons:
                target_sid = min(skeletons, key=lambda sid: utils.get(sid, 0.0))
                active_tiers[target_sid] = ResolutionTier.STUB
                trimmed_count += 1
                context_str, included_sids = self._assemble_context(graph, active_tiers)
                raw_tokens = self.tokenizer_fn(context_str)
                continue

            # Stage 3: Downgrade lowest-utility FULL -> SKELETON
            fulls = [sid for sid in active_sids if active_tiers[sid] == ResolutionTier.FULL]
            if fulls:
                target_sid = min(fulls, key=lambda sid: utils.get(sid, 0.0))
                active_tiers[target_sid] = ResolutionTier.SKELETON
                trimmed_count += 1
                context_str, included_sids = self._assemble_context(graph, active_tiers)
                raw_tokens = self.tokenizer_fn(context_str)
                continue

        file_paths = sorted(list(set(
            graph.nodes[sid].file_path for sid in included_sids if sid in graph.nodes
        )))

        metadata = {
            "budget": budget,
            "raw_tokens": raw_tokens,
            "is_budget_compliant": (raw_tokens <= budget),
            "num_files": len(file_paths),
            "num_symbols": len(included_sids),
            "trimmed_nodes_count": trimmed_count,
            "file_paths": file_paths
        }

        return context_str, metadata

    def _assemble_context(
        self,
        graph: DualViewGraph,
        active_tiers: Dict[str, ResolutionTier]
    ) -> Tuple[str, Set[str]]:
        """Assemble context string from active symbol tiers grouped by file."""
        # Group active symbols by file_path
        files_map: Dict[str, List[SymbolNode]] = {}
        for sid, tier in active_tiers.items():
            if tier == ResolutionTier.EXCLUDED:
                continue
            node = graph.nodes.get(sid)
            if node:
                files_map.setdefault(node.file_path, []).append(node)

        file_sections: List[str] = []
        included_sids: Set[str] = set()

        for file_path in sorted(files_map.keys()):
            nodes_in_file = files_map[file_path]
            file_code, sids = self._serialize_file(graph, file_path, nodes_in_file, active_tiers)
            if file_code.strip():
                section = f"# File: {file_path}\n" + file_code
                file_sections.append(section)
                included_sids.update(sids)

        full_context = "\n\n".join(file_sections)
        return full_context, included_sids

    def _serialize_file(
        self,
        graph: DualViewGraph,
        file_path: str,
        nodes: List[SymbolNode],
        active_tiers: Dict[str, ResolutionTier]
    ) -> Tuple[str, Set[str]]:
        """Serialize selected symbols for a single file preserving class hierarchy."""
        included: Set[str] = set()
        rendered_parts: List[str] = []

        # Identify classes and their methods
        class_nodes: Dict[str, SymbolNode] = {}
        top_functions: List[SymbolNode] = []
        data_nodes: List[SymbolNode] = []
        method_nodes: Dict[str, List[SymbolNode]] = {}  # class_id -> list of methods

        for node in nodes:
            if node.symbol_type == SymbolType.CLASS:
                class_nodes[node.id] = node
            elif node.symbol_type == SymbolType.METHOD:
                if node.parent_id:
                    method_nodes.setdefault(node.parent_id, []).append(node)
            elif node.symbol_type == SymbolType.GLOBAL_DATA:
                data_nodes.append(node)
            elif node.symbol_type == SymbolType.FUNCTION:
                top_functions.append(node)

        # 1. Render Data Nodes (Constants, Lookup tables)
        for dnode in sorted(data_nodes, key=lambda n: n.line_start):
            tier = active_tiers[dnode.id]
            if tier == ResolutionTier.FULL:
                rendered_parts.append(dnode.raw_code.strip())
            elif tier in (ResolutionTier.SKELETON, ResolutionTier.STUB):
                rendered_parts.append(dnode.skeleton_code.strip() or dnode.stub_code.strip())
            included.add(dnode.id)

        # 2. Render Classes with Methods
        # Also check if any methods belong to classes not explicitly in class_nodes
        all_class_ids = set(class_nodes.keys()).union(method_nodes.keys())
        for cid in sorted(all_class_ids):
            cnode = class_nodes.get(cid) or graph.nodes.get(cid)
            c_tier = active_tiers.get(cid, ResolutionTier.STUB)
            c_methods = method_nodes.get(cid, [])

            if cnode and c_tier == ResolutionTier.FULL and not c_methods:
                # Class selected at full with no separately selected sub-methods
                rendered_parts.append(cnode.raw_code.strip())
                included.add(cid)
            else:
                # Reconstruct class definition with selected methods
                class_lines = []
                cname = cnode.name if cnode else cid.split(".")[-1]
                class_lines.append(f"class {cname}:")
                if cnode and c_tier == ResolutionTier.SKELETON and cnode.docstring_summary:
                    class_lines.append(f'    """{cnode.docstring_summary}"""')

                if c_methods:
                    for m in sorted(c_methods, key=lambda n: n.line_start):
                        m_tier = active_tiers[m.id]
                        m_code = ""
                        if m_tier == ResolutionTier.FULL:
                            m_code = m.raw_code.strip()
                        elif m_tier == ResolutionTier.SKELETON:
                            m_code = m.skeleton_code.strip()
                        elif m_tier == ResolutionTier.STUB:
                            m_code = m.stub_code.strip()

                        if m_code:
                            indented_m = textwrap.indent(m_code, "    ")
                            class_lines.append(indented_m)
                            included.add(m.id)
                else:
                    class_lines.append("    ...")

                if cnode:
                    included.add(cid)
                rendered_parts.append("\n".join(class_lines))

        # 3. Render Top-level Functions
        for fnode in sorted(top_functions, key=lambda n: n.line_start):
            f_tier = active_tiers[fnode.id]
            f_code = ""
            if f_tier == ResolutionTier.FULL:
                f_code = fnode.raw_code.strip()
            elif f_tier == ResolutionTier.SKELETON:
                f_code = fnode.skeleton_code.strip()
            elif f_tier == ResolutionTier.STUB:
                f_code = fnode.stub_code.strip()

            if f_code:
                rendered_parts.append(f_code)
                included.add(fnode.id)

        file_content = "\n\n".join(rendered_parts)
        return file_content, included

    def _line_truncate_to_budget(self, text: str, budget: int) -> str:
        """Deterministic line-by-line fallback to guarantee token <= budget."""
        lines = text.splitlines(keepends=True)
        low = 0
        high = len(lines)
        best_str = ""

        # Binary search for maximum line count that fits
        while low <= high:
            mid = (low + high) // 2
            candidate = "".join(lines[:mid])
            if mid < len(lines):
                candidate += "\n# [Context budget limit reached]\n"
            toks = self.tokenizer_fn(candidate)
            if toks <= budget:
                best_str = candidate
                low = mid + 1
            else:
                high = mid - 1

        return best_str

