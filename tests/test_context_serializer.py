"""
Unit tests for ContextSerializer with Gemma 4 Tokenizer.
"""

import ast
import unittest
from transformers import AutoTokenizer

from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType
from src.mrtopos.context_serializer import ContextSerializer


class TestContextSerializer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tok = AutoTokenizer.from_pretrained("models/gemma4_tokenizer")
        cls.tok_fn = staticmethod(lambda t: len(cls.tok.encode(t, add_special_tokens=False)))
        cls.serializer = ContextSerializer(tokenizer_fn=cls.tok_fn)

    def test_class_method_reconstruction(self):
        """Verify child method is properly indented inside parent class."""
        graph = DualViewGraph()
        c = SymbolNode(
            id="pkg.mod.Cls", name="Cls", file_path="pkg/mod.py",
            symbol_type=SymbolType.CLASS, line_start=1, line_end=20,
            docstring_summary="Main service handler."
        )
        m = SymbolNode(
            id="pkg.mod.Cls.process", name="process", file_path="pkg/mod.py",
            symbol_type=SymbolType.METHOD, parent_id="pkg.mod.Cls",
            line_start=5, line_end=15,
            raw_code="def process(self, x: int) -> int:\n    return x * 2\n",
            skeleton_code="def process(self, x: int) -> int:\n    ...",
            stub_code="def process(self, ...): ..."
        )
        graph.add_node(c)
        graph.add_node(m)

        tiers = {
            "pkg.mod.Cls": ResolutionTier.SKELETON,
            "pkg.mod.Cls.process": ResolutionTier.FULL
        }
        text, meta = self.serializer.serialize(graph, tiers, budget=1000)
        self.assertIn("# File: pkg/mod.py", text)
        self.assertIn("class Cls:", text)
        self.assertIn('"""Main service handler."""', text)
        self.assertIn("    def process(self, x: int) -> int:", text)
        self.assertIn("        return x * 2", text)
        self.assertTrue(meta["is_budget_compliant"])
        self.assertEqual(meta["num_files"], 1)
        self.assertEqual(meta["num_symbols"], 2)

        # Check Python syntactic validity
        parsed = ast.parse(text)
        self.assertTrue(parsed)

    def test_strict_budget_guard_trimming(self):
        """Verify that when raw tokens exceed budget, serializer trims nodes until <= budget."""
        graph = DualViewGraph()
        symbols = []
        for i in range(10):
            sid = f"pkg.mod.fn_{i}"
            fn = SymbolNode(
                id=sid, name=f"fn_{i}", file_path="pkg/mod.py",
                symbol_type=SymbolType.FUNCTION, line_start=i * 10, line_end=i * 10 + 5,
                raw_code=f"def fn_{i}():\n    return 'some long string content to use tokens {i}'\n",
                skeleton_code=f"def fn_{i}():\n    ...",
                stub_code=f"def fn_{i}(): ..."
            )
            graph.add_node(fn)
            symbols.append(fn)

        tiers = {s.id: ResolutionTier.FULL for s in symbols}
        utilities = {s.id: float(i) for i, s in enumerate(symbols)}

        # Budget of 50 tokens is too small for 10 full functions (~150 tokens)
        budget = 50
        text, meta = self.serializer.serialize(graph, tiers, budget=budget, utilities=utilities)
        self.assertTrue(meta["is_budget_compliant"])
        self.assertLessEqual(meta["raw_tokens"], budget)
        self.assertGreater(meta["trimmed_nodes_count"], 0)


if __name__ == "__main__":
    unittest.main()

