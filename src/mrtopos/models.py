"""
Data structures and domain models for MR-TopoS.

Defines symbol representations, resolution tiers, and graph structures
for multi-resolution context induction.
"""

from enum import Enum, IntEnum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


class ResolutionTier(IntEnum):
    """Discrete resolution tiers for multi-choice knapsack optimization."""
    EXCLUDED = 0          # Node excluded from context
    STUB = 1              # Qualified name + minimal signature declaration
    SKELETON = 2          # Contract skeleton (pruned types + 1-line doc summary + elided body)
    FULL = 3              # Full implementation body + complete docstrings


class SymbolType(str, Enum):
    """Syntactic element classification."""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    GLOBAL_DATA = "data"   # Module-level data tables, constants, tuples


@dataclass
class SymbolNode:
    """Represents a discrete syntactic element in the repository AST."""
    id: str                                  # Fully qualified identifier (e.g. 'fastapi.applications.FastAPI')
    name: str                                # Short symbol identifier (e.g. 'FastAPI')
    file_path: str                           # Canonical relative repository file path
    symbol_type: SymbolType                  # Syntactic category
    parent_id: Optional[str] = None          # Qualified parent ID in AST containment tree
    line_start: int = 1                      # 1-indexed start line in original source
    line_end: int = 1                        # 1-indexed end line in original source
    raw_code: str = ""                       # Unmodified original source code
    raw_tokens: int = 0                      # Subword token count of raw code
    stub_code: str = ""                      # Tier 1 stub text
    stub_tokens: int = 0                     # Subword token count of Tier 1 stub
    skeleton_code: str = ""                  # Tier 2 contract skeleton text
    skeleton_tokens: int = 0                 # Subword token count of Tier 2 skeleton
    docstring: Optional[str] = None          # Full docstring if present
    docstring_summary: Optional[str] = None  # 1-line summary sentence of docstring
    is_data_only: bool = False               # True if file/symbol defines constant/table without functions


@dataclass
class ModuleNode:
    """Represents a Python source file module."""
    file_path: str                           # Canonical relative path (e.g. 'rich/_cell_widths.py')
    module_id: str                           # Qualified module path (e.g. 'rich._cell_widths')
    symbols: Dict[str, SymbolNode] = field(default_factory=dict)
    imports: Set[str] = field(default_factory=set)
    is_data_only: bool = False
    raw_code: str = ""
    raw_tokens: int = 0


@dataclass
class DualViewGraph:
    """
    Scope-constrained Dual-View Program Topology G = (V, E_hier ∪ E_call ∪ E_import).
    
    Guarantees:
    1. E_hier is strictly asymmetric and directed downward (Module -> Class -> Method).
    2. No artificial REPO_ROOT mega-hubs are introduced; modules are independent root scopes.
    3. Cross-file traversals can only proceed via explicit E_call or E_import edges.
    """
    nodes: Dict[str, SymbolNode] = field(default_factory=dict)
    modules: Dict[str, ModuleNode] = field(default_factory=dict)
    # Directed downward AST containment: parent_id -> list of child_ids
    hierarchy_children: Dict[str, List[str]] = field(default_factory=dict)
    # Directed downward AST containment: child_id -> parent_id
    hierarchy_parent: Dict[str, str] = field(default_factory=dict)
    # Directed invocation: caller_id -> list of callee_ids
    call_out: Dict[str, List[str]] = field(default_factory=dict)
    # Reverse invocation: callee_id -> list of caller_ids
    call_in: Dict[str, List[str]] = field(default_factory=dict)
    # Module dependencies: module_id -> imported module_names
    module_imports: Dict[str, Set[str]] = field(default_factory=dict)

    def add_node(self, node: SymbolNode) -> None:
        """Register a symbol node in the topology."""
        self.nodes[node.id] = node
        if node.parent_id:
            self.hierarchy_children.setdefault(node.parent_id, []).append(node.id)
            self.hierarchy_parent[node.id] = node.parent_id

    def add_containment_edge(self, parent_id: str, child_id: str) -> None:
        """Add directed containment edge (parent contains child)."""
        if child_id not in self.hierarchy_children.setdefault(parent_id, []):
            self.hierarchy_children[parent_id].append(child_id)
        self.hierarchy_parent[child_id] = parent_id

    @property
    def containment_edges(self) -> Dict[str, List[str]]:
        return self.hierarchy_children

    @property
    def call_edges(self) -> Dict[str, List[str]]:
        return self.call_out

    @property
    def import_edges(self) -> Dict[str, Set[str]]:
        return self.module_imports

    def get_parent_id(self, node_id: str) -> Optional[str]:
        return self.hierarchy_parent.get(node_id)

    def add_call_edge(self, caller_id: str, callee_id: str) -> None:
        """Add directed call invocation edge (caller calls callee)."""
        self.call_out.setdefault(caller_id, []).append(callee_id)
        self.call_in.setdefault(callee_id, []).append(caller_id)

    def add_import_edge(self, module_id: str, imported_target: str) -> None:
        """Add module import dependency edge."""
        self.module_imports.setdefault(module_id, set()).add(imported_target)

    def get_parent(self, node_id: str) -> Optional[SymbolNode]:
        """Return immediate AST parent (e.g. Class for Method, Module for Class)."""
        parent_id = self.hierarchy_parent.get(node_id)
        return self.nodes.get(parent_id) if parent_id else None

    def get_ancestors(self, node_id: str) -> List[SymbolNode]:
        """Return ordered list of AST ancestors from immediate parent up to Module."""
        ancestors = []
        curr = self.get_parent(node_id)
        while curr:
            ancestors.append(curr)
            curr = self.get_parent(curr.id)
        return ancestors

    def get_children(self, node_id: str) -> List[SymbolNode]:
        """Return direct AST children (e.g. Methods of a Class)."""
        child_ids = self.hierarchy_children.get(node_id, [])
        return [self.nodes[cid] for cid in child_ids if cid in self.nodes]

    def get_callees(self, node_id: str) -> List[SymbolNode]:
        """Return symbols directly invoked by node_id."""
        callee_ids = self.call_out.get(node_id, [])
        return [self.nodes[cid] for cid in callee_ids if cid in self.nodes]

    def get_callers(self, node_id: str) -> List[SymbolNode]:
        """Return symbols that invoke node_id."""
        caller_ids = self.call_in.get(node_id, [])
        return [self.nodes[cid] for cid in caller_ids if cid in self.nodes]

