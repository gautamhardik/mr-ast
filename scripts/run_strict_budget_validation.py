"""
Validation Script for Real-Token Budget Enforcement and Context Serialization.
Evaluates 20 task-budget conditions across all 4 repositories in the Gemma SE benchmark.
"""

import csv
import json
import os
import sys
import time
from typing import Dict, List

sys.path.insert(0, os.getcwd())

from transformers import AutoTokenizer

from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.causal_path import CausalPathExtractor
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.knapsack_solver import ExactMILPContextCompiler
from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode
from src.retrieval.lexical_index import LexicalGraphIndex


def main():
    print("=== Loading Official Gemma 4 Tokenizer ===")
    tok = AutoTokenizer.from_pretrained("models/gemma4_tokenizer")
    tok_fn = lambda t: len(tok.encode(t, add_special_tokens=False))
    print(f"Tokenizer loaded successfully. Vocab: {len(tok)}")

    # Load tasks
    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        all_tasks = [json.loads(line) for line in f]

    target_task_ids = [
        "fastapi_14964",
        "fastapi_15588",
        "requests_7328",
        "rich_3905",
        "httpx_3672"
    ]
    tasks = [t for t in all_tasks if t["instance_id"] in target_task_ids]
    print(f"Loaded {len(tasks)} target validation tasks across 4 repositories.")

    budgets = [2000, 4000, 8000, 16000]
    serializer = ContextSerializer(tokenizer_fn=tok_fn)
    causal_extractor = CausalPathExtractor(max_hops=2, call_decay=0.75, import_decay=0.40)
    milp_compiler = ExactMILPContextCompiler(lambda_topo=0.5, gamma_slack=5.0)

    results = []

    for task in tasks:
        task_id = task["instance_id"]
        repo = task["repo"]
        problem_statement = task["problem_statement"]
        print(f"\n--> Processing {task_id} ({repo})...")

        # Snapshot path
        snapshot_tar = os.path.join("data", "snapshots", f"{task_id}.tgz")
        if not os.path.exists(snapshot_tar):
            print(f"Warning: snapshot not found {snapshot_tar}, skipping...")
            continue

        ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)
        t_parse0 = time.perf_counter()
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=True)
        parse_ms = (time.perf_counter() - t_parse0) * 1000
        print(f"  Parsed {len(graph.nodes)} symbols across {len(graph.modules)} modules in {parse_ms:.1f} ms.")

        # Build BM25 index over symbols
        indexable_nodes = []
        for sid, node in graph.nodes.items():
            indexable_nodes.append({
                "id": sid,
                "name": node.name,
                "text": node.raw_code or node.skeleton_code or node.stub_code
            })
        lex_index = LexicalGraphIndex(indexable_nodes)
        search_res = lex_index.search(problem_statement, k=60)
        candidate_ids = [r["id"] for r in search_res if r["id"] in graph.nodes]
        candidates = [graph.nodes[cid] for cid in candidate_ids]
        lex_scores = {r["id"]: r["score"] for r in search_res}

        # Causal weights
        seed_ids = candidate_ids[:10]
        topo_weights = causal_extractor.extract_causal_subgraph(graph, seed_ids)

        # Utilities
        utilities = {
            cid: lex_scores.get(cid, 0.0) + 0.5 * topo_weights.get(cid, 0.0)
            for cid in candidate_ids
        }

        for budget in budgets:
            t_solve0 = time.perf_counter()
            sol = milp_compiler.compile(
                candidates=candidates,
                graph=graph,
                budget=budget,
                lexical_scores=lex_scores,
                topological_weights=topo_weights
            )
            solve_ms = (time.perf_counter() - t_solve0) * 1000

            selected_tiers = sol["selected_tiers"]
            context_str, meta = serializer.serialize(
                graph=graph,
                selected_tiers=selected_tiers,
                budget=budget,
                utilities=utilities
            )

            is_compliant = meta["is_budget_compliant"]
            actual_toks = meta["raw_tokens"]
            print(f"    Budget: {budget:>5} | MILP Nom: {sol['total_tokens']:>5} | Serialized: {actual_toks:>5} | "
                  f"Trimmed: {meta['trimmed_nodes_count']:>2} | Files: {meta['num_files']:>2} | Compliant: {is_compliant}")

            results.append({
                "task_id": task_id,
                "repo": repo,
                "budget": budget,
                "milp_nominal_tokens": sol["total_tokens"],
                "serialized_subword_tokens": actual_toks,
                "is_compliant": is_compliant,
                "num_files": meta["num_files"],
                "num_symbols": meta["num_symbols"],
                "trimmed_nodes_count": meta["trimmed_nodes_count"],
                "solve_time_ms": round(solve_ms, 2)
            })

    # Save to CSV
    os.makedirs("results/validation", exist_ok=True)
    out_csv = "results/validation/budget_compliance.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "task_id", "repo", "budget", "milp_nominal_tokens",
            "serialized_subword_tokens", "is_compliant", "num_files",
            "num_symbols", "trimmed_nodes_count", "solve_time_ms"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n=== Validation Complete: {len(results)} runs written to {out_csv} ===")
    all_compliant = all(r["is_compliant"] for r in results)
    print(f"Strict Budget Invariant Compliance: {'100.0% PASS' if all_compliant else 'FAIL'}")
    assert all_compliant, "Budget compliance failed!"


if __name__ == "__main__":
    main()
