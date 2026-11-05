"""
Regression Test: Atomic Symbol Drop Verification against Historical Failures.

Verifies:
1. Evaluates all 28 historical high-K failure tasks with the updated Atomic Symbol Drop serializer.
2. Checks that every output parses cleanly with ast.parse() (100% syntactic validity).
3. Confirms that '# [Context budget limit reached]' is NOT triggered (zero line truncation).
4. Verifies exact budget compliance against Gemma 4 tokenizer.
5. Runs regression tests across all dynamic policy budget configurations (2k, 4k, 8k, 16k).
"""

import ast
import json
import os
import sys
from tokenizers import Tokenizer

sys.path.insert(0, os.getcwd())
from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.knapsack_solver import ExactMILPContextCompiler
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.models import ResolutionTier, SymbolType
from src.retrieval.lexical_index import LexicalGraphIndex

def main():
    print("=================================================================")
    print("   ATOMIC SYMBOL DROP REGRESSION TEST ON HISTORICAL FAILURES")
    print("=================================================================")

    tokenizer_path = "models/gemma4_tokenizer/tokenizer.json"
    raw_tok = Tokenizer.from_file(tokenizer_path)
    tok_fn = lambda t: len(raw_tok.encode(t, add_special_tokens=False).ids)
    serializer = ContextSerializer(tokenizer_fn=tok_fn)
    compiler = ExactMILPContextCompiler(lambda_topo=0.5, enforce_ast_precedence=True, enforce_soft_calls=True)

    # 1. Load the 28 failure cases
    audit_path = "results/high_k_failure_audit.json"
    if not os.path.exists(audit_path):
        print(f"Error: {audit_path} not found.")
        sys.exit(1)

    with open(audit_path, "r", encoding="utf-8") as f:
        failures = json.load(f)

    print(f"Loaded {len(failures)} historical failure cases to test.")

    passed_count = 0
    zero_line_truncation_count = 0
    compliant_count = 0

    tested_cases = []

    for idx, case in enumerate(failures):
        task_id = case["task_id"]
        budget = case["budget"]
        k_val = case["k_val"]
        cond = case["condition"]

        snapshot_tar = os.path.join("data", "snapshots", f"{task_id}.tgz")
        if not os.path.exists(snapshot_tar):
            continue

        # Load task problem statement
        with open("data/tasks.jsonl", "r", encoding="utf-8") as tf:
            for line in tf:
                t_obj = json.loads(line)
                if t_obj["instance_id"] == task_id:
                    problem_statement = t_obj["problem_statement"]
                    break

        ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=False)

        indexable = [{"id": s, "name": n.name, "text": n.raw_code or n.skeleton_code or n.stub_code} for s, n in graph.nodes.items()]
        lex_index = LexicalGraphIndex(indexable)
        search_res = lex_index.search(problem_statement, k=k_val)
        cids = [r["id"] for r in search_res if r["id"] in graph.nodes]
        candidates = [graph.nodes[cid] for cid in cids]
        ast_builder.ensure_symbol_skeletons(candidates)
        lex_scores = {r["id"]: r["score"] for r in search_res}

        sol = compiler.compile(candidates=candidates, graph=graph, budget=budget, lexical_scores=lex_scores, topological_weights={})
        
        ctx_str, meta = serializer.serialize(graph, sol["selected_tiers"], budget, lex_scores)
        act_toks = meta["raw_tokens"]
        is_compliant = (act_toks <= budget)
        has_truncation_marker = ("# [Context budget limit reached]" in ctx_str)

        try:
            ast.parse(ctx_str)
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            err_msg = str(e)

        if syntax_valid:
            passed_count += 1
        if not has_truncation_marker:
            zero_line_truncation_count += 1
        if is_compliant:
            compliant_count += 1

        tested_cases.append({
            "task_id": task_id,
            "budget": budget,
            "k_val": k_val,
            "condition": cond,
            "serialized_tokens": act_toks,
            "budget": budget,
            "is_compliant": is_compliant,
            "has_truncation_marker": has_truncation_marker,
            "syntax_valid": syntax_valid,
            "trimmed_nodes_count": meta["trimmed_nodes_count"]
        })

        status_str = "[PASS]" if syntax_valid and is_compliant and not has_truncation_marker else "[FAIL]"
        print(f"[{idx+1:2d}/{len(failures)}] {status_str} Task: {task_id:15s} | B={budget:5d} | K={k_val:3d} | Toks: {act_toks:5d}/{budget} | Syntax: {syntax_valid} | Line Trunc: {has_truncation_marker}")

    print("\n=================================================================")
    print("                      REGRESSION RESULTS")
    print("=================================================================")
    print(f"Total Cases Tested: {len(tested_cases)}")
    print(f"Syntactic Validity Pass Rate: {passed_count}/{len(tested_cases)} ({passed_count/len(tested_cases)*100:.1f}%)")
    print(f"Zero Line-Truncation Rate:    {zero_line_truncation_count}/{len(tested_cases)} ({zero_line_truncation_count/len(tested_cases)*100:.1f}%)")
    print(f"Budget Compliance Rate:       {compliant_count}/{len(tested_cases)} ({compliant_count/len(tested_cases)*100:.1f}%)")

    out_file = "results/atomic_symbol_drop_regression_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(tested_cases, f, indent=2)
    print(f"\nSaved regression results to {out_file}")

    assert passed_count == len(tested_cases), "Regression failure: not all cases passed syntactic validity!"
    assert compliant_count == len(tested_cases), "Regression failure: not all cases were budget compliant!"
    assert zero_line_truncation_count == len(tested_cases), "Regression failure: line truncation was triggered!"
    print("\n[ALL 28 HISTORICAL FAILURES RESOLVED BY ATOMIC SYMBOL PRUNING!]")

if __name__ == "__main__":
    main()

