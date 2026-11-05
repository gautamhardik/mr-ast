"""
Causal Path Extraction for MR-TopoS.

Extracts causal execution subgraphs connecting symptom seeds to potential repair
targets, strictly distinguishing AST containment (E_hier), import dependencies (E_import),
and runtime call relationships (E_call).
"""

from collections import deque
from typing import Dict, List, Set, Tuple
from src.mrtopos.models import DualViewGraph, SymbolNode, SymbolType


class CausalPathExtractor:
    """
    Extracts causal execution subgraphs connecting symptom seeds.
    
    Guarantees:
    1. Distinguishes E_call, E_import, and E_hier:
       - E_call represents verified runtime function-to-function invocation.
       - E_import represents module-level dependency, NOT proof of a runtime call.
       - E_hier represents syntactic containment (Module -> Class -> Method) directed downward.
    2. Scope-Constrained Expansion:
       - Reached methods pull in their parent Class and Module containers strictly for
         lexical scoping (E_hier precedence), never expanding into uncalled sibling methods.
    3. No Mega-Hub Dilution:
       - Traversal through generic repo-wide roots is forbidden; cross-file paths only
         traverse explicit invocation or direct import edges.
    """

    def __init__(self, max_hops: int = 2, call_decay: float = 0.75, import_decay: float = 0.40):
        self.max_hops = max_hops
        self.call_decay = call_decay
        self.import_decay = import_decay

    def extract_causal_subgraph(
        self,
        graph: DualViewGraph,
        seed_symbol_ids: List[str]
    ) -> Dict[str, float]:
        """
        Extract candidate entities and compute their causal path topological weight.
        
        Args:
            graph: DualViewGraph containing nodes, call edges, imports, and hierarchy.
            seed_symbol_ids: Seed symbols identified by issue problem statement / stack traces.
            
        Returns:
            Dict mapping reached symbol_id to topological importance weight w_i in [0, 1].
        """
        topological_weights: Dict[str, float] = {}
        valid_seeds = [s for s in seed_symbol_ids if s in graph.nodes]

        if not valid_seeds:
            return topological_weights

        # BFS queue storing: (current_node_id, current_hop, path_weight, edge_type_used)
        queue = deque()
        for s in valid_seeds:
            topological_weights[s] = 1.0
            queue.append((s, 0, 1.0, "seed"))

        visited_edges: Set[Tuple[str, str, str]] = set()

        while queue:
            curr_id, hops, weight, edge_type = queue.popleft()

            # Ensure syntactic parent containers (Class, Module) are included for scoping
            ancestors = graph.get_ancestors(curr_id)
            for anc in ancestors:
                # Assign structural containment weight without expanding to sibling methods
                if anc.id not in topological_weights:
                    topological_weights[anc.id] = weight * 0.5

            if hops >= self.max_hops:
                continue

            # 1. Traverse E_call (Runtime Invocations) - Bidirectional
            # Downstream: functions called by curr_id
            for callee in graph.get_callees(curr_id):
                edge_key = (curr_id, callee.id, "call_out")
                if edge_key not in visited_edges:
                    visited_edges.add(edge_key)
                    next_weight = weight * self.call_decay
                    if next_weight > topological_weights.get(callee.id, 0.0):
                        topological_weights[callee.id] = next_weight
                        queue.append((callee.id, hops + 1, next_weight, "call"))

            # Upstream: functions that invoke curr_id
            for caller in graph.get_callers(curr_id):
                edge_key = (caller.id, curr_id, "call_in")
                if edge_key not in visited_edges:
                    visited_edges.add(edge_key)
                    next_weight = weight * self.call_decay
                    if next_weight > topological_weights.get(caller.id, 0.0):
                        topological_weights[caller.id] = next_weight
                        queue.append((caller.id, hops + 1, next_weight, "call"))

            # 2. Traverse E_import (Module Dependencies) - Distinct from calls
            # If current node is a module, or we check its enclosing module
            mod_node = graph.nodes.get(curr_id)
            module_id = mod_node.file_path.replace("/", ".").replace(".py", "") if mod_node else None
            
            if module_id and module_id in graph.module_imports:
                for imported_name in graph.module_imports[module_id]:
                    # Find if target module exists in graph
                    if imported_name in graph.modules:
                        target_mod_sym_id = imported_name
                        edge_key = (module_id, target_mod_sym_id, "import")
                        if edge_key not in visited_edges:
                            visited_edges.add(edge_key)
                            next_weight = weight * self.import_decay
                            if next_weight > topological_weights.get(target_mod_sym_id, 0.0):
                                topological_weights[target_mod_sym_id] = next_weight
                                queue.append((target_mod_sym_id, hops + 1, next_weight, "import"))

        return topological_weights

