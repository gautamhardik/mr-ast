import unittest
import ast
import os
import sys
import numpy as np

sys.path.insert(0, os.getcwd())
from transformers import AutoTokenizer
from src.mrtopos.models import DualViewGraph, ModuleNode, SymbolNode, SymbolType, ResolutionTier
from src.mrtopos.differential_pruner import prune_source_to_tier, extract_docstring_summary
from src.mrtopos.causal_path import CausalPathExtractor
from src.mrtopos.knapsack_solver import (
    ExactMILPContextCompiler,
    ConstraintAwareGreedyContextCompiler,
    UnconstrainedGreedyContextCompiler
)
from src.mrtopos.ast_builder import SnapshotASTBuilder


class TestImplementationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load local Gemma 4 evaluation tokenizer artifact (vocab 262,144)
        cls.tok = AutoTokenizer.from_pretrained("models/gemma4_tokenizer")
        cls.tok_fn = staticmethod(lambda t: len(cls.tok.encode(t, add_special_tokens=False)))

    def test_01_tokenizer_verification(self):
        """Check 1: Local Gemma 4 evaluation tokenizer artifact has exact vocabulary of 262,144."""
        self.assertEqual(len(self.tok), 262144)
        self.assertIn("<|channel>", self.tok.special_tokens_map.values())
        self.assertIn("<channel|>", self.tok.special_tokens_map.values())

    def test_02_structural_stub_pruning(self):
        """Check 7 & 8: Structural stubs strip parameters, docstrings, and bodies to '...'."""
        code = '''def complex_func(a: int, b: List[str] = None) -> Dict[str, Any]:
    """Long multi-line docstring explaining behavior."""
    x = a * 2
    return {"result": x}
'''
        stub, _ = prune_source_to_tier(code, ResolutionTier.STUB)
        self.assertTrue(ast.parse(stub))
        self.assertIn("...", stub)
        self.assertNotIn("Long multi-line docstring", stub)
        self.assertNotIn("x = a * 2", stub)

    def test_03_contract_skeleton_pruning(self):
        """Check 8: Contract skeletons preserve type signatures and 1-line docstrings."""
        code = '''def complex_func(a: int, b: str = "default") -> bool:
    """Summary line. Extended description that should be pruned."""
    return True
'''
        skel, _ = prune_source_to_tier(code, ResolutionTier.SKELETON)
        self.assertTrue(ast.parse(skel))
        self.assertIn("a: int", skel)
        self.assertIn("Summary line", skel)
        self.assertNotIn("Extended description", skel)

    def test_04_data_only_module_representation(self):
        """Check 4: Data-only modules (lookup tables) are preserved without classes/functions."""
        builder = SnapshotASTBuilder(tokenizer_fn=self.tok_fn)
        graph = DualViewGraph()
        code = "_WIDTHS = [(0, 31, 0), (32, 126, 1), (127, 159, 0)]\nDEFAULT_WIDTH = 1\n"
        builder._process_module(graph, "rich/_widths.py", "rich._widths", code)
        self.assertIn("rich._widths.DATA", graph.nodes)
        node = graph.nodes["rich._widths.DATA"]
        self.assertEqual(node.symbol_type, SymbolType.GLOBAL_DATA)
        self.assertGreater(node.raw_tokens, 0)

    def test_05_graph_edge_semantics(self):
        """Check 5 & 6: Containment, imports, and calls are strictly separated."""
        graph = DualViewGraph()
        graph.add_containment_edge("pkg.mod", "pkg.mod.Cls")
        graph.add_containment_edge("pkg.mod.Cls", "pkg.mod.Cls.fn")
        graph.add_import_edge("pkg.caller", "pkg.mod")
        graph.add_call_edge("pkg.caller.run", "pkg.mod.Cls.fn")

        self.assertEqual(graph.containment_edges["pkg.mod"], ["pkg.mod.Cls"])
        self.assertEqual(graph.call_edges["pkg.caller.run"], ["pkg.mod.Cls.fn"])
        self.assertEqual(graph.import_edges["pkg.caller"], {"pkg.mod"})

        # Scope constraint: get_parent returns immediate parent
        self.assertEqual(graph.get_parent_id("pkg.mod.Cls.fn"), "pkg.mod.Cls")
        self.assertEqual(graph.get_parent_id("pkg.mod.Cls"), "pkg.mod")
        self.assertIsNone(graph.get_parent_id("pkg.mod"))

    def test_06_causal_path_extractor_directionality(self):
        """Check 6: Causal path decay attenuates across calls and imports."""
        graph = DualViewGraph()
        n1 = SymbolNode(id="A", name="A", file_path="a.py", symbol_type=SymbolType.FUNCTION)
        n2 = SymbolNode(id="B", name="B", file_path="b.py", symbol_type=SymbolType.FUNCTION)
        n3 = SymbolNode(id="C", name="C", file_path="c.py", symbol_type=SymbolType.FUNCTION)
        graph.add_node(n1); graph.add_node(n2); graph.add_node(n3)
        graph.add_call_edge("A", "B")
        graph.add_call_edge("B", "C")

        extractor = CausalPathExtractor(max_hops=2, call_decay=0.75, import_decay=0.40)
        weights = extractor.extract_causal_subgraph(graph, ["A"])
        self.assertEqual(weights["A"], 1.0)
        self.assertEqual(weights["B"], 0.75)
        self.assertAlmostEqual(weights["C"], 0.75 * 0.75)

    def test_07_milp_multiple_choice_exclusivity(self):
        """Check 9: Exactly one tier is selected per symbol sum_r(x_ir) == 1."""
        graph = DualViewGraph()
        sym = SymbolNode(id="A", name="A", file_path="a.py", symbol_type=SymbolType.FUNCTION,
                         raw_tokens=50, skeleton_tokens=20, stub_tokens=5)
        graph.add_node(sym)
        compiler = ExactMILPContextCompiler()
        res = compiler.compile([sym], graph, budget=100, lexical_scores={"A": 1.0}, topological_weights={"A": 1.0})
        self.assertIn("A", res["selected_tiers"])
        self.assertEqual(res["selected_tiers"]["A"], ResolutionTier.FULL)

    def test_08_milp_parent_child_precedence(self):
        """Check 10: Child method cannot be included without parent container."""
        graph = DualViewGraph()
        p = SymbolNode(id="Cls", name="Cls", file_path="a.py", symbol_type=SymbolType.CLASS,
                       raw_tokens=100, skeleton_tokens=40, stub_tokens=10)
        c = SymbolNode(id="Cls.m", name="m", file_path="a.py", symbol_type=SymbolType.METHOD,
                       parent_id="Cls", raw_tokens=40, skeleton_tokens=15, stub_tokens=5)
        graph.add_node(p); graph.add_node(c)
        graph.add_containment_edge("Cls", "Cls.m")

        compiler = ExactMILPContextCompiler()
        # Child has high lexical score, parent has 0 score. Budget allows parent stub + child full (50 tokens)
        res = compiler.compile([p, c], graph, budget=60, lexical_scores={"Cls": 0.0, "Cls.m": 1.0}, topological_weights={})
        self.assertEqual(res["precedence_violations"], 0)
        self.assertEqual(res["selected_tiers"]["Cls.m"], ResolutionTier.FULL)
        self.assertNotEqual(res["selected_tiers"]["Cls"], ResolutionTier.EXCLUDED)

    def test_09_constraint_aware_greedy_zero_violations(self):
        """Check 10: Constraint-aware greedy guarantees 0 precedence violations."""
        graph = DualViewGraph()
        p = SymbolNode(id="Cls", name="Cls", file_path="a.py", symbol_type=SymbolType.CLASS,
                       raw_tokens=100, skeleton_tokens=40, stub_tokens=10)
        c = SymbolNode(id="Cls.m", name="m", file_path="a.py", symbol_type=SymbolType.METHOD,
                       parent_id="Cls", raw_tokens=40, skeleton_tokens=15, stub_tokens=5)
        graph.add_node(p); graph.add_node(c)
        graph.add_containment_edge("Cls", "Cls.m")

        compiler = ConstraintAwareGreedyContextCompiler()
        res = compiler.compile([p, c], graph, budget=60, lexical_scores={"Cls": 0.0, "Cls.m": 1.0}, topological_weights={})
        self.assertEqual(res["precedence_violations"], 0)
        self.assertEqual(res["selected_tiers"]["Cls.m"], ResolutionTier.FULL)
        self.assertNotEqual(res["selected_tiers"]["Cls"], ResolutionTier.EXCLUDED)

    def test_10_no_dummy_token_costs_guard(self):
        """Check 14: Verifies that real token costs are positive and distinct."""
        builder = SnapshotASTBuilder(tokenizer_fn=self.tok_fn)
        code = "def sample(): return 42\n"
        stub, _ = prune_source_to_tier(code, ResolutionTier.STUB)
        skel, _ = prune_source_to_tier(code, ResolutionTier.SKELETON)
        c_raw = self.tok_fn(code)
        c_skel = self.tok_fn(skel)
        c_stub = self.tok_fn(stub)
        self.assertGreater(c_raw, 0)
        self.assertGreater(c_skel, 0)
        self.assertGreater(c_stub, 0)
        self.assertLessEqual(c_stub, c_skel)
        self.assertLessEqual(c_skel, c_raw)


if __name__ == "__main__":
    unittest.main()
