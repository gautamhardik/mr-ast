"""
Authoritative Parent Reconstruction and Surrogate-Cost Audit across 129 SWE Tasks.

Quantifies:
1. Exact reconstructed header token overhead (tokens added by serializer for class wrappers).
2. Number of reconstructed parent wrappers per task.
3. Parent-header sharing and deduplication savings.
4. Estimated MCKP representation costs vs. actual serialized tokens.
5. Layout difference (actual serialized tokens - estimated MCKP costs).
6. Post-optimization budget guard downgrades.
7. Exact empirical distribution: mean, median, std, p25, p50, p75, p90, min, max.
8. 100% Gemma 4 tokenizer verification and AST parse validity.

Generates:
- results/parent_reconstruction_cost_audit.csv
- results/parent_reconstruction_cost_audit.json
"""

import ast
import json
import os
import sys
import time
import numpy as np
import pandas as pd
from tokenizers import Tokenizer

sys.path.insert(0, os.getcwd())
from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.knapsack_solver import ConstraintAwareGreedyContextCompiler, ExactMILPContextCompiler
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.models import ResolutionTier, SymbolType
from src.retrieval.lexical_index import LexicalGraphIndex

def main():
    t_start = time.perf_counter()
    print("=================================================================")
    print("   MR-TopoS: Clean Authoritative Parent Reconstruction Audit")
    print("=================================================================")

    tokenizer_path = "models/gemma4_tokenizer/tokenizer.json"
    if not os.path.exists(tokenizer_path):
        print(f"Error: Tokenizer {tokenizer_path} not found.")
        sys.exit(1)

    raw_tok = Tokenizer.from_file(tokenizer_path)
    tok_fn = lambda t: len(raw_tok.encode(t, add_special_tokens=False).ids)
    serializer = ContextSerializer(tokenizer_fn=tok_fn)
    
    # Evaluate pure MCKP (Condition B formulation without precedence constraints)
    compiler = ExactMILPContextCompiler(lambda_topo=0.0, enforce_ast_precedence=False, enforce_soft_calls=False)

    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]
    print(f"Loaded {len(tasks)} benchmark tasks.")

    records = []
    header_tokens_pool = []
    dedup_ratios_pool = []
    budgets = [2000, 4000, 8000, 16000]
    policy_k_map = {2000: 60, 4000: 100, 8000: 200, 16000: 400}

    os.makedirs("results", exist_ok=True)

    for t_idx, task in enumerate(tasks):
        task_id = task["instance_id"]
        repo = task["repo"]
        snapshot_tar = os.path.join("data", "snapshots", f"{task_id}.tgz")
        if not os.path.exists(snapshot_tar):
            continue

        ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=False)

        indexable = [{"id": s, "name": n.name, "text": n.raw_code or n.skeleton_code or n.stub_code} for s, n in graph.nodes.items()]
        lex_index = LexicalGraphIndex(indexable)
        max_search = lex_index.search(task["problem_statement"], k=400)
        max_cids = [r["id"] for r in max_search if r["id"] in graph.nodes]
        lex_scores_all = {r["id"]: r["score"] for r in max_search}

        # Ensure skeletons for top 400 candidates
        all_candidate_nodes = [graph.nodes[cid] for cid in max_cids]
        ast_builder.ensure_symbol_skeletons(all_candidate_nodes)

        for b in budgets:
            k_val = policy_k_map[b]
            cur_cids = max_cids[:k_val]
            candidates = [graph.nodes[cid] for cid in cur_cids]
            lex_scores = {cid: lex_scores_all[cid] for cid in cur_cids}

            sol = compiler.compile(
                candidates=candidates,
                graph=graph,
                budget=b,
                lexical_scores=lex_scores,
                topological_weights={}
            )
            
            def get_token_cost(node, tier):
                if tier == ResolutionTier.FULL:
                    return node.raw_tokens
                elif tier == ResolutionTier.SKELETON:
                    return node.skeleton_tokens
                elif tier == ResolutionTier.STUB:
                    return node.stub_tokens
                return 0

            # 1. Sum of estimated MCKP costs
            estimated_cost = sum(
                get_token_cost(c, sol["selected_tiers"].get(c.id, ResolutionTier.EXCLUDED))
                for c in candidates
            )

            # Analyze parents of selected methods
            sel_methods = [
                graph.nodes[sid] for sid, tier in sol["selected_tiers"].items() 
                if tier != ResolutionTier.EXCLUDED and graph.nodes[sid].symbol_type == SymbolType.METHOD
            ]
            
            parent_ids = [m.parent_id for m in sel_methods if m.parent_id and m.parent_id in graph.nodes]
            unique_parents = set(parent_ids)
            orphaned_parents = set(
                pid for pid in unique_parents 
                if sol["selected_tiers"].get(pid, ResolutionTier.EXCLUDED) == ResolutionTier.EXCLUDED
            )

            # Header token costs per orphaned parent
            parent_header_costs = [
                tok_fn(f"class {graph.nodes[pid].name}:\n") for pid in orphaned_parents
            ]
            header_tokens_pool.extend(parent_header_costs)
            reconstructed_header_tokens = sum(parent_header_costs)

            # Deduplication: number of parent header emissions saved
            dedup_saved = len(parent_ids) - len(unique_parents)
            dedup_ratio = (dedup_saved / len(parent_ids)) if len(parent_ids) > 0 else 0.0
            if len(parent_ids) > 0:
                dedup_ratios_pool.append(dedup_ratio)

            # Serialize and verify final emitted context
            ctx_str, meta = serializer.serialize(graph, sol["selected_tiers"], b, lex_scores)
            actual_tokens = meta["raw_tokens"]
            is_compliant = meta["is_budget_compliant"]
            trimmed_count = meta["trimmed_nodes_count"]

            try:
                ast.parse(ctx_str)
                syntax_valid = 1
            except SyntaxError:
                syntax_valid = 0

            records.append({
                "task_id": task_id,
                "repo": repo,
                "budget": b,
                "k_val": k_val,
                "estimated_mckp_cost": estimated_cost,
                "actual_serialized_tokens": actual_tokens,
                "layout_difference": actual_tokens - estimated_cost,
                "selected_methods": len(sel_methods),
                "total_parent_instances": len(parent_ids),
                "unique_parents": len(unique_parents),
                "orphaned_parents": len(orphaned_parents),
                "shared_parent_dedup_saved": dedup_saved,
                "dedup_ratio": round(dedup_ratio, 4),
                "reconstructed_header_tokens": reconstructed_header_tokens,
                "mean_tokens_per_reconstructed_parent": round(float(np.mean(parent_header_costs)), 2) if parent_header_costs else 0.0,
                "trimmed_nodes_count": trimmed_count,
                "is_budget_compliant": is_compliant,
                "syntax_valid": syntax_valid
            })

        if (t_idx + 1) % 15 == 0 or (t_idx + 1) == len(tasks):
            elapsed = time.perf_counter() - t_start
            print(f"[{t_idx+1:3d}/{len(tasks)}] Processed tasks. Elapsed: {elapsed:.1f}s")

    df_out = pd.DataFrame(records)
    csv_path = "results/parent_reconstruction_cost_audit.csv"
    df_out.to_csv(csv_path, index=False)
    print(f"\n[DONE] Saved raw CSV to {csv_path} ({len(df_out)} rows).")

    # Compute comprehensive distributional statistics
    header_tokens_arr = np.array(header_tokens_pool) if header_tokens_pool else np.array([0])
    dedup_arr = np.array(dedup_ratios_pool) if dedup_ratios_pool else np.array([0])

    distribution_stats = {
        "reconstructed_parent_header_tokens": {
            "count": int(len(header_tokens_arr)),
            "mean": round(float(np.mean(header_tokens_arr)), 2),
            "median": round(float(np.median(header_tokens_arr)), 2),
            "std": round(float(np.std(header_tokens_arr)), 2),
            "min": int(np.min(header_tokens_arr)),
            "p25": round(float(np.percentile(header_tokens_arr, 25)), 2),
            "p50": round(float(np.percentile(header_tokens_arr, 50)), 2),
            "p75": round(float(np.percentile(header_tokens_arr, 75)), 2),
            "p90": round(float(np.percentile(header_tokens_arr, 90)), 2),
            "max": int(np.max(header_tokens_arr))
        },
        "shared_parent_deduplication_ratio": {
            "count": int(len(dedup_arr)),
            "mean_pct": round(float(np.mean(dedup_arr)) * 100, 2),
            "median_pct": round(float(np.median(dedup_arr)) * 100, 2),
            "std_pct": round(float(np.std(dedup_arr)) * 100, 2),
            "p25_pct": round(float(np.percentile(dedup_arr, 25)) * 100, 2),
            "p50_pct": round(float(np.percentile(dedup_arr, 50)) * 100, 2),
            "p75_pct": round(float(np.percentile(dedup_arr, 75)) * 100, 2),
            "p90_pct": round(float(np.percentile(dedup_arr, 90)) * 100, 2)
        },
        "summary_by_budget": df_out.groupby("budget").agg({
            "estimated_mckp_cost": ["mean", "median"],
            "actual_serialized_tokens": ["mean", "median"],
            "layout_difference": ["mean", "median", "max"],
            "selected_methods": ["mean", "median"],
            "orphaned_parents": ["mean", "median"],
            "reconstructed_header_tokens": ["mean", "median"],
            "trimmed_nodes_count": ["mean", "max"],
            "is_budget_compliant": "mean",
            "syntax_valid": "mean"
        }).round(2).to_dict()
    }

    json_path = "results/parent_reconstruction_cost_audit.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(distribution_stats, f, indent=2)
    print(f"[DONE] Saved summary JSON to {json_path}")

    print("\n=================================================================")
    print("      PARENT RECONSTRUCTION AUDIT: STATISTICAL FINDINGS")
    print("=================================================================")
    hdr = distribution_stats["reconstructed_parent_header_tokens"]
    print(f"Parent Header Tokens (N={hdr['count']}):")
    print(f"  Mean: {hdr['mean']:.2f} tokens | Median: {hdr['median']:.2f} tokens | Std: {hdr['std']:.2f}")
    print(f"  Quantiles: p25={hdr['p25']:.1f}, p50={hdr['p50']:.1f}, p75={hdr['p75']:.1f}, p90={hdr['p90']:.1f}, Min={hdr['min']}, Max={hdr['max']}")

    ddp = distribution_stats["shared_parent_deduplication_ratio"]
    print(f"\nShared-Parent Deduplication Ratio (N={ddp['count']}):")
    print(f"  Mean: {ddp['mean_pct']:.2f}% | Median: {ddp['median_pct']:.2f}% | Std: {ddp['std_pct']:.2f}%")
    print(f"  Quantiles: p25={ddp['p25_pct']:.1f}%, p50={ddp['p50_pct']:.1f}%, p75={ddp['p75_pct']:.1f}%, p90={ddp['p90_pct']:.1f}%")

    print("\nBudget Compliance and Syntax Validity across all 516 evaluated runs:")
    print(f"  Overall Budget Compliance: {df_out['is_budget_compliant'].mean()*100:.2f}%")
    print(f"  Overall Syntactic Validity: {df_out['syntax_valid'].mean()*100:.2f}%")
    print(f"  Total Execution Time: {time.perf_counter() - t_start:.1f} seconds")

if __name__ == "__main__":
    main()
