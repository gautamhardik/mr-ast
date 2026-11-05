"""
Adversarial Serializer Invariant and Fallback Stage Verification Suite for MR-TopoS.

Tests:
1. Low-utility parent STUB containing high-utility FULL child.
2. Multiple methods sharing one parent class container.
3. Nested classes containing selected methods.
4. Parent representation downgraded while child remains FULL.
5. Over-budget stress test triggering fallback trimming across stages.
6. Empirical audit of fallback stage activations across all 2,580 benchmark conditions.
"""

import ast
import json
import os
import sys
import textwrap
from typing import Dict, List, Set, Tuple

import pandas as pd
from tokenizers import Tokenizer

sys.path.insert(0, os.getcwd())

from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType


def run_invariant_tests():
    print("=================================================================")
    print("       MR-TopoS: Adversarial Serializer Invariant Tests")
    print("=================================================================")

    raw_tok = Tokenizer.from_file("models/gemma4_tokenizer/tokenizer.json")
    tok_fn = lambda t: len(raw_tok.encode(t, add_special_tokens=False).ids)
    serializer = ContextSerializer(tokenizer_fn=tok_fn)

    results = []

    # -------------------------------------------------------------
    # Case 1: Low-utility parent STUB + High-utility FULL child
    # -------------------------------------------------------------
    graph1 = DualViewGraph()
    parent1 = SymbolNode(
        id="app.core.Worker", name="Worker", file_path="app/core.py", symbol_type=SymbolType.CLASS,
        parent_id=None, line_start=1, line_end=20, raw_code="class Worker:\n    pass",
        stub_code="class Worker:\n    pass", skeleton_code="class Worker:\n    pass"
    )
    child1 = SymbolNode(
        id="app.core.Worker.run", name="run", file_path="app/core.py", symbol_type=SymbolType.METHOD,
        parent_id="app.core.Worker", line_start=5, line_end=15,
        raw_code="def run(self):\n    total = sum(i for i in range(10))\n    return total",
        stub_code="def run(self):\n    pass", skeleton_code="def run(self):\n    pass"
    )
    graph1.add_node(parent1)
    graph1.add_node(child1)

    selected1 = {
        "app.core.Worker": ResolutionTier.STUB,
        "app.core.Worker.run": ResolutionTier.FULL
    }
    utils1 = {
        "app.core.Worker": 0.05,     # Very low utility
        "app.core.Worker.run": 0.95  # Very high utility
    }

    ctx1, meta1 = serializer.serialize(graph1, selected1, budget=200, utilities=utils1)
    is_valid1 = False
    try:
        ast.parse(ctx1)
        is_valid1 = True
    except SyntaxError:
        is_valid1 = False

    has_class1 = "class Worker:" in ctx1
    has_indented_run1 = "    def run(self):" in ctx1
    results.append({
        "case": "Case 1: Low-utility STUB parent + High-utility FULL child",
        "ast_valid": is_valid1,
        "contains_parent_wrapper": has_class1,
        "contains_indented_child": has_indented_run1,
        "passed": is_valid1 and has_class1 and has_indented_run1
    })

    # -------------------------------------------------------------
    # Case 2: Multiple methods sharing one parent class container
    # -------------------------------------------------------------
    graph2 = DualViewGraph()
    parent2 = SymbolNode(
        id="pkg.service.Manager", name="Manager", file_path="pkg/service.py", symbol_type=SymbolType.CLASS,
        parent_id=None, line_start=1, line_end=30, raw_code="class Manager:\n    pass",
        stub_code="class Manager:\n    pass", skeleton_code="class Manager:\n    pass"
    )
    m2_a = SymbolNode(
        id="pkg.service.Manager.start", name="start", file_path="pkg/service.py", symbol_type=SymbolType.METHOD,
        parent_id="pkg.service.Manager", line_start=5, line_end=10,
        raw_code="def start(self):\n    self.active = True",
        stub_code="def start(self):\n    pass", skeleton_code="def start(self):\n    pass"
    )
    m2_b = SymbolNode(
        id="pkg.service.Manager.stop", name="stop", file_path="pkg/service.py", symbol_type=SymbolType.METHOD,
        parent_id="pkg.service.Manager", line_start=12, line_end=18,
        raw_code="def stop(self):\n    self.active = False",
        stub_code="def stop(self):\n    pass", skeleton_code="def stop(self):\n    pass"
    )
    graph2.add_node(parent2)
    graph2.add_node(m2_a)
    graph2.add_node(m2_b)

    selected2 = {
        "pkg.service.Manager": ResolutionTier.STUB,
        "pkg.service.Manager.start": ResolutionTier.FULL,
        "pkg.service.Manager.stop": ResolutionTier.SKELETON
    }
    ctx2, meta2 = serializer.serialize(graph2, selected2, budget=300)
    is_valid2 = False
    try:
        ast.parse(ctx2)
        is_valid2 = True
    except SyntaxError:
        is_valid2 = False

    has_class2 = ctx2.count("class Manager:") == 1
    has_m_a = "    def start(self):" in ctx2
    has_m_b = "    def stop(self):" in ctx2
    results.append({
        "case": "Case 2: Multi-method shared parent container",
        "ast_valid": is_valid2,
        "contains_parent_wrapper": has_class2,
        "contains_indented_children": has_m_a and has_m_b,
        "passed": is_valid2 and has_class2 and has_m_a and has_m_b
    })

    # -------------------------------------------------------------
    # Case 3: Nested class containing selected method
    # -------------------------------------------------------------
    graph3 = DualViewGraph()
    outer3 = SymbolNode(
        id="mod.Outer", name="Outer", file_path="mod.py", symbol_type=SymbolType.CLASS,
        parent_id=None, line_start=1, line_end=20, raw_code="class Outer:\n    pass",
        stub_code="class Outer:\n    pass", skeleton_code="class Outer:\n    pass"
    )
    inner3 = SymbolNode(
        id="mod.Outer.Inner", name="Inner", file_path="mod.py", symbol_type=SymbolType.CLASS,
        parent_id="mod.Outer", line_start=2, line_end=15, raw_code="    class Inner:\n        pass",
        stub_code="class Inner:\n    pass", skeleton_code="class Inner:\n    pass"
    )
    method3 = SymbolNode(
        id="mod.Outer.Inner.execute", name="execute", file_path="mod.py", symbol_type=SymbolType.METHOD,
        parent_id="mod.Outer.Inner", line_start=5, line_end=10,
        raw_code="def execute(self):\n    return True",
        stub_code="def execute(self):\n    pass", skeleton_code="def execute(self):\n    pass"
    )
    graph3.add_node(outer3)
    graph3.add_node(inner3)
    graph3.add_node(method3)

    selected3 = {
        "mod.Outer": ResolutionTier.STUB,
        "mod.Outer.Inner": ResolutionTier.STUB,
        "mod.Outer.Inner.execute": ResolutionTier.FULL
    }
    ctx3, meta3 = serializer.serialize(graph3, selected3, budget=300)
    is_valid3 = False
    try:
        ast.parse(ctx3)
        is_valid3 = True
    except SyntaxError:
        is_valid3 = False

    results.append({
        "case": "Case 3: Nested class hierarchy",
        "ast_valid": is_valid3,
        "contains_inner_class": "class Inner:" in ctx3,
        "contains_indented_method": "    def execute(self):" in ctx3,
        "passed": is_valid3 and ("class Inner:" in ctx3) and ("    def execute(self):" in ctx3)
    })

    # -------------------------------------------------------------
    # Case 4: Parent representation downgraded (STUB -> EXCLUDED in active tiers)
    # -------------------------------------------------------------
    # Even if parent node is downgraded to EXCLUDED during trimming, child FULL method
    # must still be enclosed in class {Parent}:
    selected4 = {
        "app.core.Worker": ResolutionTier.EXCLUDED,  # Parent downgraded
        "app.core.Worker.run": ResolutionTier.FULL   # Child remains FULL
    }
    ctx4, meta4 = serializer.serialize(graph1, selected4, budget=200)
    is_valid4 = False
    try:
        ast.parse(ctx4)
        is_valid4 = True
    except SyntaxError:
        is_valid4 = False

    results.append({
        "case": "Case 4: Parent downgraded to EXCLUDED while child remains selected",
        "ast_valid": is_valid4,
        "contains_parent_wrapper": "class Worker:" in ctx4,
        "contains_indented_child": "    def run(self):" in ctx4,
        "passed": is_valid4 and ("class Worker:" in ctx4) and ("    def run(self):" in ctx4)
    })

    # -------------------------------------------------------------
    # Case 5: Over-budget stress test triggering fallback trimming across stages
    # -------------------------------------------------------------
    # Create 5 full symbols totaling ~150 tokens, force budget to 40 tokens
    graph5 = DualViewGraph()
    parent5 = SymbolNode(
        id="app.calc.Calculator", name="Calculator", file_path="app/calc.py", symbol_type=SymbolType.CLASS,
        parent_id=None, line_start=1, line_end=50, raw_code="class Calculator:\n    pass",
        stub_code="class Calculator:\n    pass", skeleton_code="class Calculator:\n    pass"
    )
    graph5.add_node(parent5)
    selected5 = {"app.calc.Calculator": ResolutionTier.STUB}
    utils5 = {"app.calc.Calculator": 0.1}

    for idx in range(1, 5):
        sid = f"app.calc.Calculator.method_{idx}"
        code = f"def method_{idx}(self, a, b):\n    # docstring\n    res = a + b * {idx}\n    return res"
        skel = f"def method_{idx}(self, a, b):\n    ..."
        stub = f"def method_{idx}(self, a, b): pass"
        node = SymbolNode(
            id=sid, name=f"method_{idx}", file_path="app/calc.py", symbol_type=SymbolType.METHOD,
            parent_id="app.calc.Calculator", line_start=idx * 10, line_end=idx * 10 + 5,
            raw_code=code, raw_tokens=tok_fn(code),
            skeleton_code=skel, skeleton_tokens=tok_fn(skel),
            stub_code=stub, stub_tokens=tok_fn(stub)
        )
        graph5.add_node(node)
        selected5[sid] = ResolutionTier.FULL
        utils5[sid] = 0.2 * idx

    # Run serialization with extreme budget: 35 tokens
    ctx5, meta5 = serializer.serialize(graph5, selected5, budget=35, utilities=utils5)
    is_valid5 = False
    try:
        ast.parse(ctx5)
        is_valid5 = True
    except SyntaxError:
        is_valid5 = False

    results.append({
        "case": "Case 5: Over-budget fallback stress test (35 tokens)",
        "budget": 35,
        "final_tokens": meta5["raw_tokens"],
        "is_budget_compliant": meta5["is_budget_compliant"],
        "trimmed_nodes_count": meta5["trimmed_nodes_count"],
        "ast_valid": is_valid5,
        "passed": meta5["is_budget_compliant"] and is_valid5
    })

    print("\n--- Invariant Test Suite Results ---")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['case']} | AST Valid: {r['ast_valid']}")

    # -------------------------------------------------------------
    # 6. Empirical Audit of Fallback Across 2,580 Benchmark Conditions
    # -------------------------------------------------------------
    print("\n--- Auditing 2,580 Benchmark Conditions in budget_audit.csv ---")
    budget_csv = "results/final_benchmark/budget_audit.csv"
    if os.path.exists(budget_csv):
        df_audit = pd.read_csv(budget_csv)
        total_runs = len(df_audit)
        zero_overhead = (df_audit["overhead_absorbed_by_trimming"] == 0).sum()
        positive_overhead = (df_audit["overhead_absorbed_by_trimming"] > 0).sum()
        max_overhead = df_audit["overhead_absorbed_by_trimming"].max()
        mean_overhead = df_audit["overhead_absorbed_by_trimming"].mean()
        compliance_rate = (df_audit["is_compliant"] == True).mean() * 100.0

        # Method breakdown
        method_stats = {}
        for method, group in df_audit.groupby("method"):
            pos_runs = (group["overhead_absorbed_by_trimming"] > 0).sum()
            method_stats[method] = {
                "total_runs": len(group),
                "zero_overhead_runs": (group["overhead_absorbed_by_trimming"] == 0).sum(),
                "positive_overhead_runs": int(pos_runs),
                "positive_overhead_pct": round(float(pos_runs) / len(group) * 100.0, 2),
                "mean_overhead_tokens": round(float(group["overhead_absorbed_by_trimming"].mean()), 2),
                "max_overhead_tokens": int(group["overhead_absorbed_by_trimming"].max()),
                "compliance_pct": round(float((group["is_compliant"] == True).mean()) * 100.0, 2)
            }

        audit_summary = {
            "total_conditions": int(total_runs),
            "overall_compliance_pct": float(compliance_rate),
            "zero_overhead_runs": int(zero_overhead),
            "positive_overhead_runs": int(positive_overhead),
            "max_overhead_tokens": int(max_overhead),
            "mean_overhead_tokens": round(float(mean_overhead), 2),
            "method_breakdown": {
                m: {k: (int(v) if str(type(v)).find("int") != -1 else float(v))
                    for k, v in s.items()}
                for m, s in method_stats.items()
            }
        }

        # Save structured results
        out_json = "results/serializer_invariants_results.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump({
                "synthetic_invariant_tests": results,
                "benchmark_fallback_audit": audit_summary
            }, f, indent=2)
        print(f"Audit completed. Results saved to {out_json}")
        print(f"Total Conditions: {total_runs} | Compliance: {compliance_rate:.1f}%")
        print(f"Zero Overhead Runs: {zero_overhead}/{total_runs} ({zero_overhead/total_runs*100:.1f}%)")
        print(f"Positive Overhead Runs: {positive_overhead}/{total_runs} ({positive_overhead/total_runs*100:.1f}%)")
        for m, s in method_stats.items():
            print(f"  {m:20s}: {s['positive_overhead_runs']}/{s['total_runs']} triggered trimming ({s['positive_overhead_pct']}%), max {s['max_overhead_tokens']} toks")

if __name__ == "__main__":
    run_invariant_tests()
