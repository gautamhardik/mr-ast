"""
Intentionally Over-Budget Serialization Test and Tracing for Budget Guard.
"""

import ast
import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from tokenizers import Tokenizer
from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType
from src.mrtopos.context_serializer import ContextSerializer

def trace_budget_guard():
    raw_tok = Tokenizer.from_file("models/gemma4_tokenizer/tokenizer.json")
    tok_fn = lambda t: len(raw_tok.encode(t).ids)
    serializer = ContextSerializer(tokenizer_fn=tok_fn)

    graph = DualViewGraph()

    # Create a parent class
    cls_node = SymbolNode(
        id="mod.ParentClass", name="ParentClass", file_path="mod.py",
        symbol_type=SymbolType.CLASS, line_start=1, line_end=50,
        docstring_summary="Parent container class with multiple methods."
    )
    graph.add_node(cls_node)

    # Method 1: High utility, FULL
    m1 = SymbolNode(
        id="mod.ParentClass.critical_method", name="critical_method", file_path="mod.py",
        symbol_type=SymbolType.METHOD, parent_id="mod.ParentClass",
        line_start=5, line_end=15,
        raw_code="def critical_method(self, x: int) -> int:\n    # A substantial implementation block\n    res = 0\n    for i in range(x):\n        res += i * 2\n    return res\n",
        skeleton_code="def critical_method(self, x: int) -> int:\n    ...",
        stub_code="def critical_method(self, ...): ..."
    )
    graph.add_node(m1)

    # Method 2: Medium utility, SKELETON
    m2 = SymbolNode(
        id="mod.ParentClass.secondary_method", name="secondary_method", file_path="mod.py",
        symbol_type=SymbolType.METHOD, parent_id="mod.ParentClass",
        line_start=20, line_end=30,
        raw_code="def secondary_method(self, y: str) -> bool:\n    return len(y) > 5\n",
        skeleton_code="def secondary_method(self, y: str) -> bool:\n    ...",
        stub_code="def secondary_method(self, ...): ..."
    )
    graph.add_node(m2)

    # Standalone function: Low utility, STUB
    fn_stub = SymbolNode(
        id="mod.low_priority_helper", name="low_priority_helper", file_path="mod.py",
        symbol_type=SymbolType.FUNCTION,
        line_start=35, line_end=45,
        raw_code="def low_priority_helper():\n    pass\n",
        skeleton_code="def low_priority_helper():\n    ...",
        stub_code="def low_priority_helper(): ..."
    )
    graph.add_node(fn_stub)

    # Initial selected tiers
    initial_tiers = {
        "mod.ParentClass": ResolutionTier.STUB,
        "mod.ParentClass.critical_method": ResolutionTier.FULL,
        "mod.ParentClass.secondary_method": ResolutionTier.SKELETON,
        "mod.low_priority_helper": ResolutionTier.STUB
    }

    utilities = {
        "mod.ParentClass": 10.0,
        "mod.ParentClass.critical_method": 50.0,
        "mod.ParentClass.secondary_method": 25.0,
        "mod.low_priority_helper": 2.0
    }

    # Measure unconstrained tokens
    raw_context, included = serializer._assemble_context(graph, initial_tiers)
    unconstrained_tokens = tok_fn(raw_context)

    # We now test under a tight budget that forces downgrades:
    # Set budget to e.g. 40 tokens (unconstrained is ~85 tokens)
    target_budget = 40

    # Let's inspect step-by-step downgrade trace:
    active_tiers = dict(initial_tiers)
    trace_steps = []

    def sort_key(sid: str):
        tier = active_tiers[sid]
        return (int(tier), utilities.get(sid, 0.0))

    prunable_sids = sorted(active_tiers.keys(), key=sort_key)
    sorted_order_desc = [(sid, str(active_tiers[sid]), utilities.get(sid, 0.0)) for sid in prunable_sids]

    trimmed_count = 0
    raw_tokens = unconstrained_tokens
    step_num = 0

    for sid in prunable_sids:
        curr_tier = active_tiers[sid]
        prev_tier_str = str(curr_tier)
        new_tier = curr_tier

        if curr_tier == ResolutionTier.STUB:
            new_tier = ResolutionTier.EXCLUDED
        elif curr_tier == ResolutionTier.SKELETON:
            new_tier = ResolutionTier.STUB
        elif curr_tier == ResolutionTier.FULL:
            new_tier = ResolutionTier.SKELETON

        active_tiers[sid] = new_tier
        trimmed_count += 1
        step_num += 1

        ctx_str, inc = serializer._assemble_context(graph, active_tiers)
        tok_count = tok_fn(ctx_str)

        trace_steps.append({
            "step": step_num,
            "target_symbol": sid,
            "action": f"{prev_tier_str} -> {str(new_tier)}",
            "tokens_after_step": tok_count,
            "budget": target_budget,
            "is_under_budget": tok_count <= target_budget
        })

        if tok_count <= target_budget:
            raw_tokens = tok_count
            break
        raw_tokens = tok_count

    line_truncated = False
    if raw_tokens > target_budget:
        ctx_str = serializer._line_truncate_to_budget(ctx_str, target_budget)
        raw_tokens = tok_fn(ctx_str)
        line_truncated = True

    # AST validation on final context
    is_valid_ast = False
    try:
        ast.parse(ctx_str)
        is_valid_ast = True
    except SyntaxError as e:
        is_valid_ast = False

    report = {
        "unconstrained_tokens": unconstrained_tokens,
        "target_budget": target_budget,
        "prunable_sort_order": sorted_order_desc,
        "trace_steps": trace_steps,
        "line_truncated": line_truncated,
        "final_tokens": raw_tokens,
        "is_budget_compliant": raw_tokens <= target_budget,
        "is_valid_ast": is_valid_ast,
        "final_context_code": ctx_str
    }

    with open("results/budget_guard_trace.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Budget guard trace written to results/budget_guard_trace.json:")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    trace_budget_guard()
