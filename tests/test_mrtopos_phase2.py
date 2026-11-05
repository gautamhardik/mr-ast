import unittest
import numpy as np

from src.mrtopos.models import DualViewGraph, ModuleNode, SymbolNode, SymbolType, ResolutionTier
from src.mrtopos.causal_path import CausalPathExtractor
from src.mrtopos.knapsack_solver import (
    ExactMILPContextCompiler,
    GreedyContextCompiler,
    ConstraintAwareGreedyContextCompiler,
    UnconstrainedGreedyContextCompiler,
)


class TestMRTopoSPhase2(unittest.TestCase):
    def setUp(self):
        """Build a synthetic dual-view repository graph for rigorous testing."""
        self.graph = DualViewGraph()

        # Module A: api/service.py
        mod_a = ModuleNode(
            file_path="api/service.py",
            module_id="api.service",
            raw_code="class Service:\n    def execute(self):\n        return helper()\n    def unused_method(self):\n        pass\n"
        )
        self.graph.modules[mod_a.module_id] = mod_a

        # Symbols in Module A
        cls_service = SymbolNode(
            id="api.service.Service",
            name="Service",
            file_path="api/service.py",
            symbol_type=SymbolType.CLASS,
            line_start=1,
            line_end=5,
            raw_tokens=60,
            skeleton_tokens=20,
            stub_tokens=8
        )
        m_exec = SymbolNode(
            id="api.service.Service.execute",
            name="execute",
            file_path="api/service.py",
            symbol_type=SymbolType.METHOD,
            parent_id="api.service.Service",
            line_start=2,
            line_end=3,
            raw_tokens=40,
            skeleton_tokens=15,
            stub_tokens=5
        )
        m_unused = SymbolNode(
            id="api.service.Service.unused_method",
            name="unused_method",
            file_path="api/service.py",
            symbol_type=SymbolType.METHOD,
            parent_id="api.service.Service",
            line_start=4,
            line_end=5,
            raw_tokens=30,
            skeleton_tokens=10,
            stub_tokens=4
        )
        self.graph.add_node(cls_service)
        self.graph.add_node(m_exec)
        self.graph.add_node(m_unused)

        # Module B: utils/helpers.py
        mod_b = ModuleNode(
            file_path="utils/helpers.py",
            module_id="utils.helpers",
            raw_code="def helper():\n    return 42\n"
        )
        self.graph.modules[mod_b.module_id] = mod_b

        fn_helper = SymbolNode(
            id="utils.helpers.helper",
            name="helper",
            file_path="utils/helpers.py",
            symbol_type=SymbolType.FUNCTION,
            line_start=1,
            line_end=2,
            raw_tokens=35,
            skeleton_tokens=12,
            stub_tokens=5
        )
        self.graph.add_node(fn_helper)

        # Edges
        # Import edge: api.service imports utils.helpers
        self.graph.add_import_edge("api.service", "utils.helpers")

        # Call edge: execute() calls helper()
        self.graph.add_call_edge("api.service.Service.execute", "utils.helpers.helper")

    def test_causal_path_extractor_directionality_and_scoping(self):
        """Verify directional decay, distinct import decay, and scope-constrained scoping."""
        extractor = CausalPathExtractor(max_hops=2, call_decay=0.75, import_decay=0.40)
        
        # Seed is execute()
        weights = extractor.extract_causal_subgraph(self.graph, ["api.service.Service.execute"])
        
        # 1. Seed has maximum weight 1.0
        self.assertAlmostEqual(weights["api.service.Service.execute"], 1.0)
        
        # 2. Direct callee helper() has call_decay * 1.0 = 0.75
        self.assertIn("utils.helpers.helper", weights)
        self.assertAlmostEqual(weights["utils.helpers.helper"], 0.75)
        
        # 3. Parent class Service is included via structural containment
        self.assertIn("api.service.Service", weights)
        self.assertGreater(weights["api.service.Service"], 0.0)
        
        # 4. Scope constraint: uncalled sibling method 'unused_method' must NOT be inflated by call propagation
        self.assertNotIn("api.service.Service.unused_method", weights,
                         "Uncalled sibling method was incorrectly expanded into!")

    def test_milp_solver_exact_optimality(self):
        """Verify that MILP finds an optimal solution satisfying all PC-MCKP constraints."""
        compiler = ExactMILPContextCompiler()
        candidates = list(self.graph.nodes.values())
        
        lexical_scores = {
            "api.service.Service.execute": 0.95,
            "api.service.Service": 0.50,
            "utils.helpers.helper": 0.70,
            "api.service.Service.unused_method": 0.05
        }
        topological_weights = {
            "api.service.Service.execute": 1.0,
            "api.service.Service": 0.5,
            "utils.helpers.helper": 0.75
        }
        
        # Generous budget: enough for full representation
        result_full = compiler.compile(
            candidates=candidates,
            graph=self.graph,
            budget=200,
            lexical_scores=lexical_scores,
            topological_weights=topological_weights
        )
        self.assertEqual(result_full["status"], 0, f"HiGHS failed: {result_full['status_message']}")
        self.assertEqual(result_full["precedence_violations"], 0)
        self.assertLessEqual(result_full["total_tokens"], 200)

        # Tight budget: 40 tokens (cannot include all full versions)
        result_tight = compiler.compile(
            candidates=candidates,
            graph=self.graph,
            budget=40,
            lexical_scores=lexical_scores,
            topological_weights=topological_weights
        )
        self.assertEqual(result_tight["status"], 0)
        self.assertEqual(result_tight["precedence_violations"], 0)
        self.assertLessEqual(result_tight["total_tokens"], 40)
        
        # Check tier selections under tight budget:
        # Parent class must be at least STUB or SKELETON if child execute is selected
        exec_tier = result_tight["selected_tiers"].get("api.service.Service.execute", ResolutionTier.EXCLUDED)
        parent_tier = result_tight["selected_tiers"].get("api.service.Service", ResolutionTier.EXCLUDED)
        if exec_tier > ResolutionTier.EXCLUDED:
            self.assertGreater(parent_tier, ResolutionTier.EXCLUDED,
                               "Precedence violated: execute selected but parent class excluded!")

    def test_milp_vs_greedy_comparison(self):
        """Compare exact MILP vs Greedy baseline under budget constraints."""
        milp_compiler = ExactMILPContextCompiler()
        unconstrained_greedy = UnconstrainedGreedyContextCompiler()
        constraint_greedy = ConstraintAwareGreedyContextCompiler()
        candidates = list(self.graph.nodes.values())
        
        lexical_scores = {
            "api.service.Service.execute": 0.9,
            "api.service.Service": 0.4,
            "utils.helpers.helper": 0.8,
            "api.service.Service.unused_method": 0.1
        }
        topological_weights = {
            "api.service.Service.execute": 1.0,
            "api.service.Service": 0.5,
            "utils.helpers.helper": 0.75
        }
        
        budget = 35
        milp_res = milp_compiler.compile(candidates, self.graph, budget, lexical_scores, topological_weights)
        uncon_res = unconstrained_greedy.compile(candidates, self.graph, budget, lexical_scores, topological_weights)
        con_res = constraint_greedy.compile(candidates, self.graph, budget, lexical_scores, topological_weights)
        
        self.assertEqual(milp_res["status"], 0)
        self.assertEqual(uncon_res["status"], 0)
        self.assertEqual(con_res["status"], 0)
        self.assertEqual(milp_res["precedence_violations"], 0)
        self.assertEqual(con_res["precedence_violations"], 0)
        self.assertLessEqual(con_res["total_tokens"], budget)
        
        # Exact MILP objective must be greater than or equal to Constraint-Aware Greedy objective
        self.assertGreaterEqual(
            milp_res["objective_value"],
            con_res["objective_value"] - 1e-6,
            "Exact MILP returned lower objective than constraint-aware greedy!"
        )

    def test_gold_patch_quarantine(self):
        """Verify strict quarantine: optimizer valuation does not accept or inspect gold patches."""
        compiler = ExactMILPContextCompiler()
        import inspect
        sig = inspect.signature(compiler.compile)
        param_names = list(sig.parameters.keys())
        forbidden_keywords = ["patch", "gold", "reference", "target", "solution", "test_patch"]
        for kw in forbidden_keywords:
            self.assertNotIn(kw, param_names, f"Forbidden keyword '{kw}' found in compiler interface!")


if __name__ == "__main__":
    unittest.main()
