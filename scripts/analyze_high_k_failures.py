"""
Detailed Root-Cause Analysis of High-K Syntax Validity Failures.

Analyzes the 28 failures across saturation_K100 (4), saturation_K200 (9), and saturation_K400 (15).
Categorizes errors, reproduces them, and designs the regression test.
"""

import ast
import json
import os
import sys
import pandas as pd
from tokenizers import Tokenizer

sys.path.insert(0, os.getcwd())
from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.knapsack_solver import ExactMILPContextCompiler
from src.mrtopos.context_serializer import ContextSerializer
from src.retrieval.lexical_index import LexicalGraphIndex

def main():
    df = pd.read_csv("results/strategic_reset/experiment_ledger.csv")
    failures = df[df["condition"].str.startswith("saturation") & (df["syntactic_validity"] == 0)].copy()
    print(f"Total Saturation Failures: {len(failures)}")
    print(failures.groupby(["condition", "budget"]).size())

    raw_tok = Tokenizer.from_file("models/gemma4_tokenizer/tokenizer.json")
    tok_fn = lambda t: len(raw_tok.encode(t, add_special_tokens=False).ids)
    serializer = ContextSerializer(tokenizer_fn=tok_fn)
    compiler = ExactMILPContextCompiler(lambda_topo=0.5, enforce_ast_precedence=True, enforce_soft_calls=True)

    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks_map = {json.loads(l)["instance_id"]: json.loads(l) for l in f}

    failure_records = []

    for idx, row in failures.iterrows():
        task_id = row["task_id"]
        budget = int(row["budget"])
        k_val = int(row["K_pool"])
        cond = row["condition"]

        task = tasks_map[task_id]
        snapshot_tar = os.path.join("data", "snapshots", f"{task_id}.tgz")
        if not os.path.exists(snapshot_tar):
            continue

        ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=False)

        indexable = [{"id": s, "name": n.name, "text": n.raw_code or n.skeleton_code or n.stub_code} for s, n in graph.nodes.items()]
        lex_index = LexicalGraphIndex(indexable)
        search_res = lex_index.search(task["problem_statement"], k=k_val)
        cids = [r["id"] for r in search_res if r["id"] in graph.nodes]
        candidates = [graph.nodes[cid] for cid in cids]
        
        nodes_with_parents = list(candidates)
        for c in candidates:
            p = graph.get_parent(c.id)
            if p and p not in nodes_with_parents:
                nodes_with_parents.append(p)
        ast_builder.ensure_symbol_skeletons(nodes_with_parents)

        lex_scores = {cid: 1.0 for cid in cids}
        sol = compiler.compile(candidates=candidates, graph=graph, budget=budget, lexical_scores=lex_scores, topological_weights={})
        ctx_str, meta = serializer.serialize(graph, sol["selected_tiers"], budget, lex_scores)

        # Inspect syntax failure
        err_type = ""
        err_msg = ""
        err_line = -1
        err_snippet = ""
        try:
            ast.parse(ctx_str)
            err_type = "NONE_PARSED_NOW"
        except SyntaxError as e:
            err_type = type(e).__name__
            err_msg = str(e)
            err_line = e.lineno
            lines = ctx_str.split("\n")
            start = max(0, err_line - 3)
            end = min(len(lines), err_line + 3)
            err_snippet = "\n".join(f"{i+1}: {lines[i]}" for i in range(start, end))

        has_budget_marker = "# [Context budget limit reached]" in ctx_str
        is_exact_budget = (meta["raw_tokens"] == budget)

        failure_records.append({
            "task_id": task_id,
            "budget": budget,
            "k_val": k_val,
            "condition": cond,
            "serialized_tokens": meta["raw_tokens"],
            "budget": budget,
            "is_exact_budget": is_exact_budget,
            "has_budget_marker": has_budget_marker,
            "trimmed_nodes_count": meta["trimmed_nodes_count"],
            "err_type": err_type,
            "err_msg": err_msg,
            "err_line": err_line,
            "err_snippet": err_snippet
        })

    df_out = pd.DataFrame(failure_records)
    print("\nFailure Categories:")
    print(df_out["err_msg"].value_counts())
    print("\nHas Budget Marker (# [Context budget limit reached]):")
    print(df_out["has_budget_marker"].value_counts())

    out_file = "results/high_k_failure_audit.json"
    df_out.to_json(out_file, orient="records", indent=2)
    print(f"\n[DONE] Saved failure records to {out_file}")

if __name__ == "__main__":
    main()

