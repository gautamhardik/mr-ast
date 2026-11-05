"""
Master Benchmark Execution Script for MR-TopoS Research Paper.
Evaluates 129 tasks x 4 budgets x 5 methods = 2,580 conditions.
Uses official Google Gemma 4 tokenizer (vocab 262,144) and strict real-token budgets.
"""

import ast
import csv
import json
import os
import re
import sys
import time
from collections import defaultdict
from typing import Dict, List, Set, Tuple

sys.path.insert(0, os.getcwd())

import numpy as np
from transformers import AutoTokenizer

from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.causal_path import CausalPathExtractor
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.knapsack_solver import (
    ConstraintAwareGreedyContextCompiler,
    ExactMILPContextCompiler,
)
from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType
from src.retrieval.lexical_index import LexicalGraphIndex


def extract_gold_files(patch: str) -> List[str]:
    """Extract list of ground-truth modified file paths from unified git diff."""
    if not patch:
        return []
    matches = re.findall(r"\+\+\+ b/(.+?)\n", patch)
    return [m.strip() for m in matches if m.strip() and m.strip() != "/dev/null"]


def evaluate_syntactic_validity(code_text: str) -> int:
    """Returns 1 if code parses as valid Python AST, 0 otherwise."""
    if not code_text.strip():
        return 1
    try:
        ast.parse(code_text)
        return 1
    except SyntaxError:
        return 0


def main():
    print("=================================================================")
    print("       MR-TopoS: Master Real-Token 129-Task Benchmark Execution")
    print("=================================================================")
    t_start = time.perf_counter()

    # 1. Load official Gemma 4 tokenizer
    print("Loading official Gemma 4 tokenizer (models/gemma4_tokenizer)...")
    tokenizer = AutoTokenizer.from_pretrained("models/gemma4_tokenizer")
    tok_fn = lambda t: len(tokenizer.encode(t, add_special_tokens=False))
    print(f"Tokenizer loaded successfully. Vocab size: {len(tokenizer)}")

    # 2. Load all 129 tasks
    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]
    print(f"Loaded {len(tasks)} benchmark tasks.")

    budgets = [2000, 4000, 8000, 16000]
    methods = ["full_file", "bm25_raw", "bm25_scoped", "mrtopos_con_greedy", "mrtopos_milp"]

    serializer = ContextSerializer(tokenizer_fn=tok_fn)
    causal_extractor = CausalPathExtractor(max_hops=2, call_decay=0.75, import_decay=0.40)
    milp_compiler = ExactMILPContextCompiler(lambda_topo=0.5, gamma_slack=5.0)
    con_greedy_compiler = ConstraintAwareGreedyContextCompiler(lambda_topo=0.5)

    per_task_records = []
    budget_audit_records = []

    for task_idx, task in enumerate(tasks):
        task_id = task["instance_id"]
        repo = task["repo"]
        problem_statement = task["problem_statement"]
        gold_files = extract_gold_files(task.get("patch", ""))

        snapshot_tar = os.path.join("data", "snapshots", f"{task_id}.tgz")
        if not os.path.exists(snapshot_tar):
            print(f"[{task_idx+1}/{len(tasks)}] WARNING: Snapshot not found for {task_id}, skipping.")
            continue

        # Parse Snapshot AST (Fast mode: skeletons on demand)
        ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=False)

        # Build BM25 index over all symbols in snapshot
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

        # Expand candidate set with parent classes
        all_candidate_nodes = list(candidates)
        for c in candidates:
            p = graph.get_parent(c.id)
            if p and p not in all_candidate_nodes:
                all_candidate_nodes.append(p)

        # Ensure candidates and their parents have real Gemma 4 subword tokens & skeletons
        ast_builder.ensure_symbol_skeletons(all_candidate_nodes)

        # Causal weights
        seed_ids = candidate_ids[:10]
        topo_weights = causal_extractor.extract_causal_subgraph(graph, seed_ids)

        utilities = {
            cid: lex_scores.get(cid, 0.0) + 0.5 * topo_weights.get(cid, 0.0)
            for cid in candidate_ids
        }

        # Aggregate BM25 file ranking for full_file baseline
        file_bm25_scores = defaultdict(float)
        for r in search_res:
            node = graph.nodes.get(r["id"])
            if node:
                file_bm25_scores[node.file_path] += r["score"]
        ranked_files = sorted(file_bm25_scores.keys(), key=lambda fp: file_bm25_scores[fp], reverse=True)

        for budget in budgets:
            for method in methods:
                t0 = time.perf_counter()
                selected_files: Set[str] = set()
                retained_sym_count = 0
                retained_full = 0
                retained_skel = 0
                retained_stub = 0
                context_str = ""
                nominal_tokens = 0
                actual_tokens = 0
                trimmed_count = 0
                is_compliant = True

                # ==========================================
                # Method 1: full_file
                # ==========================================
                if method == "full_file":
                    sections = []
                    curr_toks = 0
                    for fp in ranked_files:
                        # Find module in graph
                        mod = next((m for m in graph.modules.values() if m.file_path == fp), None)
                        if not mod or not mod.raw_code:
                            continue
                        mod_toks = tok_fn(mod.raw_code) + 10  # approximate file header cost
                        if curr_toks + mod_toks <= budget or not sections:
                            sections.append(f"# File: {fp}\n{mod.raw_code}")
                            curr_toks += mod_toks
                            selected_files.add(fp)
                            # All symbols in module are retained at full
                            syms_in_mod = [s for s in graph.nodes.values() if s.file_path == fp]
                            retained_sym_count += len(syms_in_mod)
                            retained_full += len(syms_in_mod)
                        if curr_toks >= budget:
                            break

                    context_str = "\n\n".join(sections)
                    actual_tokens = tok_fn(context_str)
                    if actual_tokens > budget:
                        context_str = serializer._line_truncate_to_budget(context_str, budget)
                        actual_tokens = tok_fn(context_str)
                    nominal_tokens = actual_tokens
                    solve_ms = (time.perf_counter() - t0) * 1000

                # ==========================================
                # Method 2: bm25_raw
                # ==========================================
                elif method == "bm25_raw":
                    pieces = []
                    curr_toks = 0
                    for c in candidates:
                        c_toks = c.raw_tokens
                        if curr_toks + c_toks <= budget:
                            pieces.append(c.raw_code)
                            curr_toks += c_toks
                            selected_files.add(c.file_path)
                            retained_sym_count += 1
                            retained_full += 1
                        if curr_toks >= budget:
                            break

                    context_str = "\n\n".join(pieces)
                    actual_tokens = tok_fn(context_str)
                    if actual_tokens > budget:
                        context_str = serializer._line_truncate_to_budget(context_str, budget)
                        actual_tokens = tok_fn(context_str)
                    nominal_tokens = actual_tokens
                    solve_ms = (time.perf_counter() - t0) * 1000

                # ==========================================
                # Method 3: bm25_scoped
                # ==========================================
                elif method == "bm25_scoped":
                    pieces = []
                    curr_toks = 0
                    for c in candidates:
                        if c.symbol_type == SymbolType.METHOD and c.parent_id and c.parent_id in graph.nodes:
                            p = graph.nodes[c.parent_id]
                            # Wrap in parent class stub
                            scoped_code = f"class {p.name}:\n" + "    " + c.raw_code.replace("\n", "\n    ")
                        else:
                            scoped_code = c.raw_code

                        c_toks = tok_fn(scoped_code)
                        if curr_toks + c_toks <= budget:
                            pieces.append(scoped_code)
                            curr_toks += c_toks
                            selected_files.add(c.file_path)
                            retained_sym_count += 1
                            retained_full += 1
                        if curr_toks >= budget:
                            break

                    context_str = "\n\n".join(pieces)
                    actual_tokens = tok_fn(context_str)
                    if actual_tokens > budget:
                        context_str = serializer._line_truncate_to_budget(context_str, budget)
                        actual_tokens = tok_fn(context_str)
                    nominal_tokens = actual_tokens
                    solve_ms = (time.perf_counter() - t0) * 1000

                # ==========================================
                # Method 4: mrtopos_con_greedy
                # ==========================================
                elif method == "mrtopos_con_greedy":
                    sol = con_greedy_compiler.compile(
                        candidates=candidates,
                        graph=graph,
                        budget=budget,
                        lexical_scores=lex_scores,
                        topological_weights=topo_weights
                    )
                    solve_ms = sol["solve_time_ms"]
                    nominal_tokens = sol["total_tokens"]
                    context_str, meta = serializer.serialize(
                        graph=graph,
                        selected_tiers=sol["selected_tiers"],
                        budget=budget,
                        utilities=utilities
                    )
                    actual_tokens = meta["raw_tokens"]
                    trimmed_count = meta["trimmed_nodes_count"]
                    selected_files = set(meta["file_paths"])
                    for sid, tier in sol["selected_tiers"].items():
                        if tier == ResolutionTier.FULL:
                            retained_full += 1
                        elif tier == ResolutionTier.SKELETON:
                            retained_skel += 1
                        elif tier == ResolutionTier.STUB:
                            retained_stub += 1
                    retained_sym_count = retained_full + retained_skel + retained_stub

                # ==========================================
                # Method 5: mrtopos_milp
                # ==========================================
                elif method == "mrtopos_milp":
                    sol = milp_compiler.compile(
                        candidates=candidates,
                        graph=graph,
                        budget=budget,
                        lexical_scores=lex_scores,
                        topological_weights=topo_weights
                    )
                    solve_ms = sol["solve_time_ms"]
                    nominal_tokens = sol["total_tokens"]
                    context_str, meta = serializer.serialize(
                        graph=graph,
                        selected_tiers=sol["selected_tiers"],
                        budget=budget,
                        utilities=utilities
                    )
                    actual_tokens = meta["raw_tokens"]
                    trimmed_count = meta["trimmed_nodes_count"]
                    selected_files = set(meta["file_paths"])
                    for sid, tier in sol["selected_tiers"].items():
                        if tier == ResolutionTier.FULL:
                            retained_full += 1
                        elif tier == ResolutionTier.SKELETON:
                            retained_skel += 1
                        elif tier == ResolutionTier.STUB:
                            retained_stub += 1
                    retained_sym_count = retained_full + retained_skel + retained_stub

                # Evaluation Metrics
                is_compliant = (actual_tokens <= budget)
                syntactic_validity = evaluate_syntactic_validity(context_str)

                # Gold file hits
                gold_set = set(gold_files)
                hits = selected_files.intersection(gold_set)
                gold_recall = len(hits) / len(gold_set) if gold_set else 0.0

                # Hit@1, Hit@5, Hit@10 over selected files
                selected_files_list = list(selected_files)
                hit_1 = 1 if any(f in gold_set for f in selected_files_list[:1]) else 0
                hit_5 = 1 if any(f in gold_set for f in selected_files_list[:5]) else 0
                hit_10 = 1 if any(f in gold_set for f in selected_files_list[:10]) else 0

                per_task_records.append({
                    "task_id": task_id,
                    "repo": repo,
                    "budget": budget,
                    "method": method,
                    "gold_file_recall": round(gold_recall, 4),
                    "gold_files_hit_at_1": hit_1,
                    "gold_files_hit_at_5": hit_5,
                    "gold_files_hit_at_10": hit_10,
                    "retained_symbols_count": retained_sym_count,
                    "retained_full_symbols": retained_full,
                    "retained_skel_symbols": retained_skel,
                    "retained_stub_symbols": retained_stub,
                    "syntactic_validity": syntactic_validity,
                    "solve_time_ms": round(solve_ms, 2),
                    "serialized_tokens": actual_tokens,
                    "is_budget_compliant": is_compliant
                })

                budget_audit_records.append({
                    "task_id": task_id,
                    "method": method,
                    "budget": budget,
                    "nominal_tokens": nominal_tokens,
                    "serialized_tokens": actual_tokens,
                    "overhead_absorbed_by_trimming": trimmed_count,
                    "is_compliant": is_compliant
                })

        if (task_idx + 1) % 10 == 0 or (task_idx + 1) == len(tasks):
            elapsed = time.perf_counter() - t_start
            print(f"[{task_idx+1}/{len(tasks)}] Completed in {elapsed:.1f}s...")

    # Write per_task.csv
    os.makedirs("results/final_benchmark", exist_ok=True)
    per_task_path = "results/final_benchmark/per_task.csv"
    with open(per_task_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "task_id", "repo", "budget", "method", "gold_file_recall",
            "gold_files_hit_at_1", "gold_files_hit_at_5", "gold_files_hit_at_10",
            "retained_symbols_count", "retained_full_symbols", "retained_skel_symbols",
            "retained_stub_symbols", "syntactic_validity", "solve_time_ms",
            "serialized_tokens", "is_budget_compliant"
        ])
        writer.writeheader()
        writer.writerows(per_task_records)
    print(f"Saved {len(per_task_records)} rows to {per_task_path}")

    # Write budget_audit.csv
    budget_audit_path = "results/final_benchmark/budget_audit.csv"
    with open(budget_audit_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "task_id", "method", "budget", "nominal_tokens",
            "serialized_tokens", "overhead_absorbed_by_trimming", "is_compliant"
        ])
        writer.writeheader()
        writer.writerows(budget_audit_records)
    print(f"Saved budget audit to {budget_audit_path}")

    # Compute aggregate.csv (mean across tasks for each method and budget)
    agg_groups = defaultdict(list)
    for r in per_task_records:
        key = (r["method"], r["budget"])
        agg_groups[key].append(r)

    agg_records = []
    for (m, b), recs in sorted(agg_groups.items()):
        N = len(recs)
        agg_records.append({
            "method": m,
            "budget": b,
            "mean_gold_file_recall": round(float(np.mean([x["gold_file_recall"] for x in recs])), 4),
            "hit_at_1": round(float(np.mean([x["gold_files_hit_at_1"] for x in recs])), 4),
            "hit_at_5": round(float(np.mean([x["gold_files_hit_at_5"] for x in recs])), 4),
            "hit_at_10": round(float(np.mean([x["gold_files_hit_at_10"] for x in recs])), 4),
            "mean_retained_symbols": round(float(np.mean([x["retained_symbols_count"] for x in recs])), 2),
            "mean_full_symbols": round(float(np.mean([x["retained_full_symbols"] for x in recs])), 2),
            "mean_skel_symbols": round(float(np.mean([x["retained_skel_symbols"] for x in recs])), 2),
            "mean_stub_symbols": round(float(np.mean([x["retained_stub_symbols"] for x in recs])), 2),
            "syntactic_validity_rate": round(float(np.mean([x["syntactic_validity"] for x in recs])), 4),
            "mean_solve_time_ms": round(float(np.mean([x["solve_time_ms"] for x in recs])), 2),
            "mean_tokens": round(float(np.mean([x["serialized_tokens"] for x in recs])), 1),
            "compliance_rate": round(float(np.mean([1.0 if x["is_budget_compliant"] else 0.0 for x in recs])), 4),
        })

    agg_path = "results/final_benchmark/aggregate.csv"
    with open(agg_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "method", "budget", "mean_gold_file_recall", "hit_at_1", "hit_at_5", "hit_at_10",
            "mean_retained_symbols", "mean_full_symbols", "mean_skel_symbols", "mean_stub_symbols",
            "syntactic_validity_rate", "mean_solve_time_ms", "mean_tokens", "compliance_rate"
        ])
        writer.writeheader()
        writer.writerows(agg_records)
    print(f"Saved aggregate metrics to {agg_path}")

    # Compute per_repository.csv
    repo_groups = defaultdict(list)
    for r in per_task_records:
        key = (r["repo"], r["method"], r["budget"])
        repo_groups[key].append(r)

    repo_records = []
    for (repo, m, b), recs in sorted(repo_groups.items()):
        repo_records.append({
            "repo": repo,
            "method": m,
            "budget": b,
            "mean_gold_file_recall": round(float(np.mean([x["gold_file_recall"] for x in recs])), 4),
            "hit_at_1": round(float(np.mean([x["gold_files_hit_at_1"] for x in recs])), 4),
            "hit_at_5": round(float(np.mean([x["gold_files_hit_at_5"] for x in recs])), 4),
            "mean_retained_symbols": round(float(np.mean([x["retained_symbols_count"] for x in recs])), 2),
            "syntactic_validity_rate": round(float(np.mean([x["syntactic_validity"] for x in recs])), 4),
            "mean_solve_time_ms": round(float(np.mean([x["solve_time_ms"] for x in recs])), 2)
        })

    repo_path = "results/final_benchmark/per_repository.csv"
    with open(repo_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "repo", "method", "budget", "mean_gold_file_recall", "hit_at_1", "hit_at_5",
            "mean_retained_symbols", "syntactic_validity_rate", "mean_solve_time_ms"
        ])
        writer.writeheader()
        writer.writerows(repo_records)
    print(f"Saved per-repository metrics to {repo_path}")

    total_time = time.perf_counter() - t_start
    print(f"\n=================================================================")
    print(f"Benchmark Execution Finished Successfully in {total_time:.1f} seconds!")
    print(f"=================================================================")


if __name__ == "__main__":
    main()

