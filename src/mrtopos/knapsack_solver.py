"""
Precedence-Constrained Multi-Choice Knapsack (PC-MCKP) Context Compiler for MR-TopoS.

Implements:
1. ExactMILPContextCompiler: Exact branch-and-cut optimization using scipy.optimize.milp / HiGHS.
2. GreedyContextCompiler: Heuristic baseline for optimality gap and constraint violation comparisons.
"""

import time
from typing import Dict, List, Optional, Set, Tuple
import numpy as np
from scipy.optimize import LinearConstraint, milp

from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType


class ExactMILPContextCompiler:
    """
    Exact PC-MCKP context compilation via Mixed Integer Linear Programming (HiGHS solver).
    
    Optimizes multi-resolution tier assignment under strict token budget B subject to
    AST containment precedence DAGs and soft causal callee contract preservation.
    """

    def __init__(
        self,
        tier_multipliers: Optional[Dict[ResolutionTier, float]] = None,
        lambda_topo: float = 0.5,
        gamma_slack: float = 5.0,
        enforce_ast_precedence: bool = True,
        enforce_soft_calls: bool = True
    ):
        self.tier_multipliers = tier_multipliers or {
            ResolutionTier.EXCLUDED: 0.0,
            ResolutionTier.STUB: 0.2,
            ResolutionTier.SKELETON: 0.6,
            ResolutionTier.FULL: 1.0,
        }
        self.lambda_topo = lambda_topo
        self.gamma_slack = gamma_slack
        self.enforce_ast_precedence = enforce_ast_precedence
        self.enforce_soft_calls = enforce_soft_calls

    def compile(
        self,
        candidates: List[SymbolNode],
        graph: DualViewGraph,
        budget: int,
        lexical_scores: Dict[str, float],
        topological_weights: Dict[str, float]
    ) -> Dict:
        """
        Solve exact PC-MCKP optimization.
        
        Returns:
            Dict containing solve metrics, selected tiers, objective value, and token total.
        """
        t0 = time.perf_counter()
        N = len(candidates)
        if N == 0:
            return {
                "status": 0,
                "status_message": "Empty candidate set",
                "solve_time_ms": 0.0,
                "objective_value": 0.0,
                "total_tokens": 0,
                "selected_tiers": {},
                "precedence_violations": 0
            }

        node_index = {node.id: idx for idx, node in enumerate(candidates)}
        num_x = N * 4

        # Identify internal call edges among candidates
        call_pairs: List[Tuple[int, int]] = []
        if self.enforce_soft_calls:
            for u_node in candidates:
                u_idx = node_index[u_node.id]
                for v_node in graph.get_callees(u_node.id):
                    if v_node.id in node_index:
                        v_idx = node_index[v_node.id]
                        call_pairs.append((u_idx, v_idx))

        num_slack = len(call_pairs)
        total_vars = num_x + num_slack

        # 1. Objective Vector c (minimize c^T y where y = [x, xi])
        c = np.zeros(total_vars, dtype=np.float64)
        for i, node in enumerate(candidates):
            s_i = lexical_scores.get(node.id, 0.0)
            w_i = topological_weights.get(node.id, 0.0)
            base_val = s_i + self.lambda_topo * w_i

            for j_tier in ResolutionTier:
                var_idx = i * 4 + int(j_tier)
                val_ij = self.tier_multipliers[j_tier] * base_val
                c[var_idx] = -val_ij  # Negative for maximization

        # Penalize slack variables in objective
        for k in range(num_slack):
            c[num_x + k] = self.gamma_slack

        # 2. Constraints Matrix A and Bounds
        constraints_list = []
        lhs_bounds = []
        rhs_bounds = []

        # Constraint 1: Budget Capacity sum(c_ij * x_ij) <= B
        budget_row = np.zeros(total_vars, dtype=np.float64)
        for i, node in enumerate(candidates):
            costs = {
                ResolutionTier.EXCLUDED: 0,
                ResolutionTier.STUB: max(1, node.stub_tokens),
                ResolutionTier.SKELETON: max(1, node.skeleton_tokens),
                ResolutionTier.FULL: max(1, node.raw_tokens),
            }
            for j_tier in ResolutionTier:
                budget_row[i * 4 + int(j_tier)] = costs[j_tier]

        constraints_list.append(budget_row)
        lhs_bounds.append(0.0)
        rhs_bounds.append(float(budget))

        # Constraint 2: Multiple-Choice Mutual Exclusivity sum_j(x_ij) == 1
        for i in range(N):
            mc_row = np.zeros(total_vars, dtype=np.float64)
            for j in range(4):
                mc_row[i * 4 + j] = 1.0
            constraints_list.append(mc_row)
            lhs_bounds.append(1.0)
            rhs_bounds.append(1.0)

        # Constraint 3: AST Syntactic Precedence (Child requires Parent)
        # sum_{j=1}^3 x_{child, j} <= sum_{k=1}^3 x_{parent, k}
        # => sum_{j=1}^3 x_{child, j} - sum_{k=1}^3 x_{parent, k} <= 0
        precedence_count = 0
        if self.enforce_ast_precedence:
            for i, child_node in enumerate(candidates):
                parent = graph.get_parent(child_node.id)
                if parent and parent.id in node_index:
                    p_idx = node_index[parent.id]
                    prec_row = np.zeros(total_vars, dtype=np.float64)
                    for j in [1, 2, 3]:
                        prec_row[i * 4 + j] = 1.0
                        prec_row[p_idx * 4 + j] = -1.0
                    constraints_list.append(prec_row)
                    lhs_bounds.append(-np.inf)
                    rhs_bounds.append(0.0)
                    precedence_count += 1

        # Constraint 4: Soft Causal Precedence for Calls
        # x_{u, 3} - (x_{v, 2} + x_{v, 3}) - xi_{uv} <= 0
        if self.enforce_soft_calls:
            for k, (u_idx, v_idx) in enumerate(call_pairs):
                call_row = np.zeros(total_vars, dtype=np.float64)
                call_row[u_idx * 4 + int(ResolutionTier.FULL)] = 1.0
                call_row[v_idx * 4 + int(ResolutionTier.SKELETON)] = -1.0
                call_row[v_idx * 4 + int(ResolutionTier.FULL)] = -1.0
                call_row[num_x + k] = -1.0  # slack variable
                constraints_list.append(call_row)
                lhs_bounds.append(-np.inf)
                rhs_bounds.append(0.0)

        A = np.array(constraints_list, dtype=np.float64)
        linear_constraint = LinearConstraint(A, lhs_bounds, rhs_bounds)

        # Variable Bounds & Integrality
        variable_bounds_l = np.zeros(total_vars, dtype=np.float64)
        variable_bounds_u = np.ones(total_vars, dtype=np.float64)
        integrality = np.zeros(total_vars, dtype=np.int32)
        integrality[:num_x] = 1  # x_ij are binary (1)
        integrality[num_x:] = 0  # slack variables are continuous (0)

        bounds = (variable_bounds_l, variable_bounds_u)

        # Solve via HiGHS
        res = milp(
            c=c,
            integrality=integrality,
            bounds=bounds,
            constraints=linear_constraint
        )

        solve_time_ms = (time.perf_counter() - t0) * 1000.0

        if not res.success:
            return {
                "status": int(res.status),
                "status_message": res.message,
                "solve_time_ms": round(solve_time_ms, 2),
                "objective_value": 0.0,
                "total_tokens": 0,
                "selected_tiers": {n.id: ResolutionTier.EXCLUDED for n in candidates},
                "precedence_violations": 0
            }

        # Extract Solution
        x_sol = res.x[:num_x].reshape((N, 4))
        selected_tiers = {}
        total_tokens = 0
        violations = 0

        for i, node in enumerate(candidates):
            tier_idx = int(np.argmax(x_sol[i]))
            chosen_tier = ResolutionTier(tier_idx)
            selected_tiers[node.id] = chosen_tier

            cost_map = {
                ResolutionTier.EXCLUDED: 0,
                ResolutionTier.STUB: max(1, node.stub_tokens),
                ResolutionTier.SKELETON: max(1, node.skeleton_tokens),
                ResolutionTier.FULL: max(1, node.raw_tokens),
            }
            total_tokens += cost_map[chosen_tier]

        # Verify syntactic precedence satisfaction
        for node in candidates:
            if selected_tiers[node.id] != ResolutionTier.EXCLUDED:
                parent = graph.get_parent(node.id)
                if parent and parent.id in selected_tiers:
                    if selected_tiers[parent.id] == ResolutionTier.EXCLUDED:
                        violations += 1

        return {
            "status": int(res.status),
            "status_message": res.message,
            "solve_time_ms": round(solve_time_ms, 2),
            "objective_value": round(-float(res.fun), 4),
            "total_tokens": total_tokens,
            "selected_tiers": selected_tiers,
            "precedence_violations": violations,
            "total_variables": total_vars,
            "total_constraints": len(lhs_bounds)
        }


class UnconstrainedGreedyContextCompiler:
    """
    Unconstrained value-density greedy heuristic baseline.
    Sorts candidate tier upgrades independently by marginal utility density (Delta v / Delta c)
    without enforcing hierarchical containment during selection.
    """

    def __init__(self, lambda_topo: float = 0.5):
        self.lambda_topo = lambda_topo
        self.tier_multipliers = {
            ResolutionTier.EXCLUDED: 0.0,
            ResolutionTier.STUB: 0.2,
            ResolutionTier.SKELETON: 0.6,
            ResolutionTier.FULL: 1.0,
        }

    def compile(
        self,
        candidates: List[SymbolNode],
        graph: DualViewGraph,
        budget: int,
        lexical_scores: Dict[str, float],
        topological_weights: Dict[str, float]
    ) -> Dict:
        """Execute unconstrained greedy budget allocation."""
        t0 = time.perf_counter()
        selected_tiers = {n.id: ResolutionTier.EXCLUDED for n in candidates}
        current_tokens = 0
        current_value = 0.0

        transitions = []
        for node in candidates:
            s_i = lexical_scores.get(node.id, 0.0)
            w_i = topological_weights.get(node.id, 0.0)
            base_val = s_i + self.lambda_topo * w_i

            costs = {
                ResolutionTier.EXCLUDED: 0,
                ResolutionTier.STUB: max(1, node.stub_tokens),
                ResolutionTier.SKELETON: max(1, node.skeleton_tokens),
                ResolutionTier.FULL: max(1, node.raw_tokens),
            }

            tiers = [ResolutionTier.STUB, ResolutionTier.SKELETON, ResolutionTier.FULL]
            prev_tier = ResolutionTier.EXCLUDED
            prev_cost = 0
            prev_val = 0.0

            for t in tiers:
                cost_t = costs[t]
                val_t = self.tier_multipliers[t] * base_val
                delta_c = max(1, cost_t - prev_cost)
                delta_v = max(0.0, val_t - prev_val)
                density = delta_v / delta_c
                transitions.append((node.id, prev_tier, t, delta_v, delta_c, density))
                prev_tier = t
                prev_cost = cost_t
                prev_val = val_t

        transitions.sort(key=lambda x: x[5], reverse=True)

        for nid, from_t, to_t, delta_v, delta_c, _ in transitions:
            if selected_tiers[nid] == from_t:
                if current_tokens + delta_c <= budget:
                    selected_tiers[nid] = to_t
                    current_tokens += delta_c
                    current_value += delta_v

        solve_time_ms = (time.perf_counter() - t0) * 1000.0

        violations = 0
        for node in candidates:
            if selected_tiers[node.id] != ResolutionTier.EXCLUDED:
                parent = graph.get_parent(node.id)
                if parent and parent.id in selected_tiers:
                    if selected_tiers[parent.id] == ResolutionTier.EXCLUDED:
                        violations += 1

        return {
            "status": 0,
            "solve_time_ms": round(solve_time_ms, 2),
            "objective_value": round(current_value, 4),
            "total_tokens": current_tokens,
            "selected_tiers": selected_tiers,
            "precedence_violations": violations
        }


# Alias for backwards compatibility
GreedyContextCompiler = UnconstrainedGreedyContextCompiler


class ConstraintAwareGreedyContextCompiler:
    """
    Constraint-Aware Greedy baseline for PC-MCKP context compilation.
    
    Guarantees:
    1. Precedence Preservation: When a child symbol is activated, all unselected
       ancestor containers (enclosing class, module) are bundled with it at minimum
       viable tier (STUB), bundling marginal cost and marginal value.
    2. Representation Exclusivity: Each candidate is assigned exactly one tier.
    3. Token Budget Adherence: Total bundle cost is strictly checked against budget.
    """

    def __init__(
        self,
        tier_multipliers: Optional[Dict[ResolutionTier, float]] = None,
        lambda_topo: float = 0.5
    ):
        self.tier_multipliers = tier_multipliers or {
            ResolutionTier.EXCLUDED: 0.0,
            ResolutionTier.STUB: 0.2,
            ResolutionTier.SKELETON: 0.6,
            ResolutionTier.FULL: 1.0,
        }
        self.lambda_topo = lambda_topo

    def compile(
        self,
        candidates: List[SymbolNode],
        graph: DualViewGraph,
        budget: int,
        lexical_scores: Dict[str, float],
        topological_weights: Dict[str, float]
    ) -> Dict:
        """Execute constraint-aware greedy bundle budget allocation."""
        t0 = time.perf_counter()
        selected_tiers = {n.id: ResolutionTier.EXCLUDED for n in candidates}
        current_tokens = 0
        current_value = 0.0
        cand_by_id = {n.id: n for n in candidates}

        def get_costs(node: SymbolNode) -> Dict[ResolutionTier, int]:
            return {
                ResolutionTier.EXCLUDED: 0,
                ResolutionTier.STUB: max(1, node.stub_tokens),
                ResolutionTier.SKELETON: max(1, node.skeleton_tokens),
                ResolutionTier.FULL: max(1, node.raw_tokens),
            }

        def get_node_val(nid: str, tier: ResolutionTier) -> float:
            s = lexical_scores.get(nid, 0.0)
            w = topological_weights.get(nid, 0.0)
            return self.tier_multipliers[tier] * (s + self.lambda_topo * w)

        # Iterative greedy bundle selection
        while True:
            best_bundle = None
            best_density = -1.0

            for node in candidates:
                curr_t = selected_tiers[node.id]
                if curr_t == ResolutionTier.FULL:
                    continue

                # Possible target tiers
                if curr_t == ResolutionTier.EXCLUDED:
                    next_tiers = [ResolutionTier.STUB, ResolutionTier.SKELETON, ResolutionTier.FULL]
                elif curr_t == ResolutionTier.STUB:
                    next_tiers = [ResolutionTier.SKELETON, ResolutionTier.FULL]
                elif curr_t == ResolutionTier.SKELETON:
                    next_tiers = [ResolutionTier.FULL]
                else:
                    next_tiers = []

                for target_t in next_tiers:
                    # Build required bundle: upgrade node, plus activate unselected ancestors to STUB
                    bundle_upgrades = {node.id: target_t}
                    curr_anc = graph.get_parent(node.id)
                    while curr_anc:
                        if curr_anc.id in selected_tiers and selected_tiers[curr_anc.id] == ResolutionTier.EXCLUDED:
                            bundle_upgrades[curr_anc.id] = ResolutionTier.STUB
                        curr_anc = graph.get_parent(curr_anc.id)

                    delta_c = 0
                    delta_v = 0.0
                    for bid, bt in bundle_upgrades.items():
                        if bid not in cand_by_id:
                            continue
                        bnode = cand_by_id[bid]
                        b_costs = get_costs(bnode)
                        b_curr_t = selected_tiers[bid]
                        delta_c += b_costs[bt] - b_costs[b_curr_t]
                        delta_v += get_node_val(bid, bt) - get_node_val(bid, b_curr_t)

                    if delta_c <= 0:
                        delta_c = 1

                    if current_tokens + delta_c <= budget:
                        density = delta_v / delta_c
                        if density > best_density:
                            best_density = density
                            best_bundle = (bundle_upgrades, delta_c, delta_v)

            if not best_bundle or best_density <= 0.0:
                break

            bundle_upgrades, delta_c, delta_v = best_bundle
            for bid, bt in bundle_upgrades.items():
                selected_tiers[bid] = bt
            current_tokens += delta_c
            current_value += delta_v

        solve_time_ms = (time.perf_counter() - t0) * 1000.0

        # Verify syntactic precedence satisfaction
        violations = 0
        for node in candidates:
            if selected_tiers[node.id] != ResolutionTier.EXCLUDED:
                parent = graph.get_parent(node.id)
                if parent and parent.id in selected_tiers:
                    if selected_tiers[parent.id] == ResolutionTier.EXCLUDED:
                        violations += 1

        return {
            "status": 0,
            "solve_time_ms": round(solve_time_ms, 2),
            "objective_value": round(current_value, 4),
            "total_tokens": current_tokens,
            "selected_tiers": selected_tiers,
            "precedence_violations": violations
        }

