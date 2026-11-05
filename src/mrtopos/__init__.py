"""
MR-TopoS: Multi-Resolution Dual-View Context Induction Engine.

Phase 1 Core Modules:
- models: Domain models, resolution tiers, and DualViewGraph.
- differential_pruner: AST transformer implementing Differential Typing Pruning.
- ast_builder: Direct snapshot AST parser and Dual-View Graph constructor.
"""

from src.mrtopos.models import (
    DualViewGraph,
    ModuleNode,
    ResolutionTier,
    SymbolNode,
    SymbolType,
)
from src.mrtopos.differential_pruner import (
    ASTDifferentialPruner,
    extract_docstring_summary,
    prune_source_to_tier,
)
from src.mrtopos.ast_builder import SnapshotASTBuilder

__all__ = [
    "DualViewGraph",
    "ModuleNode",
    "ResolutionTier",
    "SymbolNode",
    "SymbolType",
    "ASTDifferentialPruner",
    "extract_docstring_summary",
    "prune_source_to_tier",
    "SnapshotASTBuilder",
]

