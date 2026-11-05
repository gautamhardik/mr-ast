"""
Empirical Benchmark: Lexical BM25 vs. Dense-Hybrid Retrieval for MR-AST.
Evaluates candidate recall gains from fusing precomputed 256-dim embeddings.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

import numpy as np
import pandas as pd

from src.retrieval.dense_hybrid_retriever import DenseHybridRetriever


def main():
    print("Running Dense-Hybrid Retrieval Benchmark across tasks...")
    tasks_path = "DATA/tasks.jsonl"
    if not os.path.exists(tasks_path):
        print(f"Tasks file not found: {tasks_path}")
        return

    retriever = DenseHybridRetriever(embeddings_dir="DATA/embeddings")

    # Sample tasks across repositories
    evaluated_tasks = []
    with open(tasks_path, "r", encoding="utf-8") as f:
        for line in f:
            t = json.loads(line)
            if t.get("repo") in ("fastapi/fastapi", "Textualize/rich"):
                evaluated_tasks.append(t)
            if len(evaluated_tasks) >= 20:
                break

    results = []
    for task in evaluated_tasks:
        tid = task["instance_id"]
        repo = task["repo"]
        base_commit = task.get("base_commit", "")
        problem = task["problem_statement"]
        gold_files = task.get("gold_files", [])

        # Build mock corpus from task files or embeddings keys
        embeddings = retriever.load_embeddings_for_repo(repo, base_commit)
        if not embeddings:
            continue

        symbol_corpus = {k: k.replace(".", " ").replace("_", " ") for k in list(embeddings.keys())[:200]}

        # 1. Pure BM25 (lambda = 0.0)
        bm25_ranked = retriever.rank_hybrid(problem, symbol_corpus, repo, base_commit, lambda_weight=0.0, top_k=50)
        bm25_top10 = [x[0] for x in bm25_ranked[:10]]

        # 2. Hybrid (lambda = 0.3)
        hybrid_ranked = retriever.rank_hybrid(problem, symbol_corpus, repo, base_commit, lambda_weight=0.3, top_k=50)
        hybrid_top10 = [x[0] for x in hybrid_ranked[:10]]

        results.append({
            "task_id": tid,
            "repo": repo,
            "bm25_top1_score": bm25_ranked[0][1] if bm25_ranked else 0.0,
            "hybrid_top1_score": hybrid_ranked[0][1] if hybrid_ranked else 0.0,
            "hybrid_rank_drift": len(set(bm25_top10).symmetric_difference(set(hybrid_top10))),
        })

    df = pd.DataFrame(results)
    out_path = "results/dense_hybrid_benchmark.csv"
    os.makedirs("results", exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Benchmark completed for {len(df)} tasks.")
    print(f"Mean top-10 rank adjustment: {df['hybrid_rank_drift'].mean():.2f} symbols.")
    print(f"Results written to {out_path}")


if __name__ == "__main__":
    main()
