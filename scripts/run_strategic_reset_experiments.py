"""
Authoritative Strategic Reset Experiment Suite for MR-TopoS.

Executes:
1. Decisive Factorial Ablation (Conditions A, B, C, D, E, F) across B in {2k, 4k, 8k, 16k}.
2. Candidate Pool Saturation Study (K in {60, 100, 200, 400}) across B in {2k, 4k, 8k, 16k}.
3. Authentic Aider Repository Map Baseline across B in {2k, 4k, 8k, 16k}.

Saves unified results into:
- results/strategic_reset/experiment_ledger.csv
- results/strategic_reset/experiment_ledger.json
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

import numpy as np
from tokenizers import Tokenizer

sys.path.insert(0, os.getcwd())

from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.causal_path import CausalPathExtractor
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.knapsack_solver import (
    ConstraintAwareGreedyContextCompiler,
    ExactMILPContextCompiler,
)
from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode, SymbolType
from src.retrieval.aider_repomap import AiderRepoMapBaseline
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
    print("     MR-TopoS: Strategic Reset Definitive Experiment Suite")
    print("=================================================================")
    t_suite_start = time.perf_counter()

    # Load fast offline Gemma 4 tokenizer
    print("Loading Gemma 4 tokenizer from models/gemma4_tokenizer/tokenizer.json...")
    raw_tok = Tokenizer.from_file("models/gemma4_tokenizer/tokenizer.json")
    tok_fn = lambda t: len(raw_tok.encode(t, add_special_tokens=False).ids)
    print(f"Tokenizer loaded successfully. Vocab size: {raw_tok.get_vocab_size()}")

    # Load tasks
    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]
    print(f"Loaded {len(tasks)} benchmark tasks.")

    budgets = [2000, 4000, 8000, 16000]
    serializer = ContextSerializer(tokenizer_fn=tok_fn)
    causal_extractor = CausalPathExtractor(max_hops=2, call_decay=0.75, import_decay=0.40)
    aider_baseline = AiderRepoMapBaseline(tokenizer_fn=tok_fn)

    # Initialize Compilers for Ablation
    compiler_cond_b = ExactMILPContextCompiler(lambda_topo=0.0, enforce_ast_precedence=False, enforce_soft_calls=False)
    compiler_cond_c = ExactMILPContextCompiler(lambda_topo=0.0, enforce_ast_precedence=True, enforce_soft_calls=False)
    compiler_cond_d = ExactMILPContextCompiler(lambda_topo=0.5, enforce_ast_precedence=True, enforce_soft_calls=True)
    compiler_cond_e = ConstraintAwareGreedyContextCompiler(lambda_topo=0.5)
    compiler_cond_f = ExactMILPContextCompiler(lambda_topo=0.5, enforce_ast_precedence=True, enforce_soft_calls=True)

    ledger_records = []
    os.makedirs("results/strategic_reset", exist_ok=True)

    for task_idx, task in enumerate(tasks):
        task_id = task["instance_id"]
        repo = task["repo"]
        problem_statement = task["problem_statement"]
        gold_files_all = extract_gold_files(task.get("patch", ""))

        snapshot_tar = os.path.join("data", "snapshots", f"{task_id}.tgz")
        if not os.path.exists(snapshot_tar):
            print(f"[{task_idx+1}/{len(tasks)}] WARNING: Snapshot missing for {task_id}, skipping.")
            continue

        t_task_start = time.perf_counter()

        # Parse snapshot AST
        ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=False)

        # Classify gold files into pre-existing vs patch-created
        snapshot_files = set(n.file_path for n in graph.nodes.values())
        gold_pre_existing = [f for f in gold_files_all if f in snapshot_files]

        # Build BM25 index over all symbols in snapshot
        indexable_nodes = []
        for sid, node in graph.nodes.items():
            indexable_nodes.append({
                "id": sid,
                "name": node.name,
                "text": node.raw_code or node.skeleton_code or node.stub_code
            })
        lex_index = LexicalGraphIndex(indexable_nodes)

        # Retrieve up to max K=400 candidates for saturation study
        max_k_search = lex_index.search(problem_statement, k=400)
        max_k_cids = [r["id"] for r in max_k_search if r["id"] in graph.nodes]
        all_retrieved_nodes = [graph.nodes[cid] for cid in max_k_cids]
        lex_scores_all = {r["id"]: r["score"] for r in max_k_search}

        # Expand candidate set with parent classes for all top 400 candidates
        nodes_with_parents = list(all_retrieved_nodes)
        for c in all_retrieved_nodes:
            p = graph.get_parent(c.id)
            if p and p not in nodes_with_parents:
                nodes_with_parents.append(p)

        # Generate skeletons and real Gemma 4 subword tokens on-demand
        ast_builder.ensure_symbol_skeletons(nodes_with_parents)

        # Extract causal graph weights
        seed_ids = max_k_cids[:10]
        topo_weights = causal_extractor.extract_causal_subgraph(graph, seed_ids)

        # =================================================================
        # 1. Decisive Factorial Ablation at K=60
        # =================================================================
        k60_cids = max_k_cids[:60]
        k60_candidates = [graph.nodes[cid] for cid in k60_cids]
        k60_lex_scores = {cid: lex_scores_all[cid] for cid in k60_cids}
        k60_utilities = {
            cid: k60_lex_scores.get(cid, 0.0) + 0.5 * topo_weights.get(cid, 0.0)
            for cid in k60_cids
        }

        # Pre-calculate file ranking for Scoped BM25
        file_bm25_scores = defaultdict(float)
        for r in max_k_search[:60]:
            node = graph.nodes.get(r["id"])
            if node:
                file_bm25_scores[node.file_path] += r["score"]

        for budget in budgets:
            # Condition A: Scoped BM25
            t0 = time.perf_counter()
            pieces_a = []
            curr_toks_a = 0
            sel_files_a = set()
            for c in k60_candidates:
                if c.symbol_type == SymbolType.METHOD and c.parent_id and c.parent_id in graph.nodes:
                    p = graph.nodes[c.parent_id]
                    scoped_code = f"class {p.name}:\n" + "    " + c.raw_code.replace("\n", "\n    ")
                else:
                    scoped_code = c.raw_code
                c_toks = tok_fn(scoped_code)
                if curr_toks_a + c_toks <= budget:
                    pieces_a.append(scoped_code)
                    curr_toks_a += c_toks
                    sel_files_a.add(c.file_path)
                if curr_toks_a >= budget:
                    break
            ctx_a = "\n\n".join(pieces_a)
            act_toks_a = tok_fn(ctx_a)
            if act_toks_a > budget:
                ctx_a = serializer._line_truncate_to_budget(ctx_a, budget)
                act_toks_a = tok_fn(ctx_a)
            solve_ms_a = (time.perf_counter() - t0) * 1000

            ledger_records.append({
                "task_id": task_id, "repo": repo, "budget": budget,
                "experiment_group": "factorial_ablation",
                "condition": "A_scoped_bm25", "K_pool": 60,
                "gold_recall_all": round(len(sel_files_a.intersection(set(gold_files_all))) / len(gold_files_all), 4) if gold_files_all else 0.0,
                "gold_recall_pre_existing": round(len(sel_files_a.intersection(set(gold_pre_existing))) / len(gold_pre_existing), 4) if gold_pre_existing else None,
                "retained_symbols_count": len(pieces_a), "retained_full": len(pieces_a), "retained_skel": 0, "retained_stub": 0,
                "syntactic_validity": evaluate_syntactic_validity(ctx_a),
                "solve_time_ms": round(solve_ms_a, 2), "serialized_tokens": act_toks_a,
                "is_budget_compliant": (act_toks_a <= budget)
            })

            # Conditions B, C, D, E, F
            ablation_configs = [
                ("B_mr_only", compiler_cond_b, {cid: k60_lex_scores[cid] for cid in k60_cids}, {}),
                ("C_mr_containment", compiler_cond_c, {cid: k60_lex_scores[cid] for cid in k60_cids}, {}),
                ("D_mr_containment_dep", compiler_cond_d, k60_lex_scores, topo_weights),
                ("E_mrtopos_con_greedy", compiler_cond_e, k60_lex_scores, topo_weights),
                ("F_mrtopos_milp", compiler_cond_f, k60_lex_scores, topo_weights)
            ]

            for cond_name, compiler, l_scores, t_weights in ablation_configs:
                sol = compiler.compile(
                    candidates=k60_candidates, graph=graph, budget=budget,
                    lexical_scores=l_scores, topological_weights=t_weights
                )
                solve_ms = sol["solve_time_ms"]
                ctx_str, meta = serializer.serialize(
                    graph=graph, selected_tiers=sol["selected_tiers"],
                    budget=budget, utilities=k60_utilities
                )
                act_tokens = meta["raw_tokens"]
                sel_files = set(meta["file_paths"])

                r_full = sum(1 for t in sol["selected_tiers"].values() if t == ResolutionTier.FULL)
                r_skel = sum(1 for t in sol["selected_tiers"].values() if t == ResolutionTier.SKELETON)
                r_stub = sum(1 for t in sol["selected_tiers"].values() if t == ResolutionTier.STUB)

                ledger_records.append({
                    "task_id": task_id, "repo": repo, "budget": budget,
                    "experiment_group": "factorial_ablation",
                    "condition": cond_name, "K_pool": 60,
                    "gold_recall_all": round(len(sel_files.intersection(set(gold_files_all))) / len(gold_files_all), 4) if gold_files_all else 0.0,
                    "gold_recall_pre_existing": round(len(sel_files.intersection(set(gold_pre_existing))) / len(gold_pre_existing), 4) if gold_pre_existing else None,
                    "retained_symbols_count": r_full + r_skel + r_stub,
                    "retained_full": r_full, "retained_skel": r_skel, "retained_stub": r_stub,
                    "syntactic_validity": evaluate_syntactic_validity(ctx_str),
                    "solve_time_ms": round(solve_ms, 2), "serialized_tokens": act_tokens,
                    "is_budget_compliant": (act_tokens <= budget)
                })

            # =================================================================
            # 2. Aider Repository Map Baseline
            # =================================================================
            t_aider0 = time.perf_counter()
            aider_res = aider_baseline.compile(graph=graph, query=problem_statement, budget=budget)
            solve_ms_aider = (time.perf_counter() - t_aider0) * 1000
            sel_files_aider = aider_res["selected_files"]

            ledger_records.append({
                "task_id": task_id, "repo": repo, "budget": budget,
                "experiment_group": "aider_repomap_baseline",
                "condition": "aider_repomap", "K_pool": len(graph.nodes),
                "gold_recall_all": round(len(sel_files_aider.intersection(set(gold_files_all))) / len(gold_files_all), 4) if gold_files_all else 0.0,
                "gold_recall_pre_existing": round(len(sel_files_aider.intersection(set(gold_pre_existing))) / len(gold_pre_existing), 4) if gold_pre_existing else None,
                "retained_symbols_count": aider_res["retained_symbols_count"],
                "retained_full": 0, "retained_skel": aider_res["retained_symbols_count"], "retained_stub": 0,
                "syntactic_validity": aider_res["syntactic_validity"],
                "solve_time_ms": round(solve_ms_aider, 2),
                "serialized_tokens": aider_res["actual_tokens"],
                "is_budget_compliant": aider_res["is_compliant"]
            })

        # =================================================================
        # 3. Candidate Pool Saturation Study (K in {100, 200, 400})
        # =================================================================
        for k_val in [100, 200, 400]:
            k_cids = max_k_cids[:k_val]
            k_candidates = [graph.nodes[cid] for cid in k_cids]
            k_lex_scores = {cid: lex_scores_all[cid] for cid in k_cids}
            k_utilities = {
                cid: k_lex_scores.get(cid, 0.0) + 0.5 * topo_weights.get(cid, 0.0)
                for cid in k_cids
            }

            for budget in budgets:
                sol = compiler_cond_f.compile(
                    candidates=k_candidates, graph=graph, budget=budget,
                    lexical_scores=k_lex_scores, topological_weights=topo_weights
                )
                solve_ms = sol["solve_time_ms"]
                ctx_str, meta = serializer.serialize(
                    graph=graph, selected_tiers=sol["selected_tiers"],
                    budget=budget, utilities=k_utilities
                )
                act_tokens = meta["raw_tokens"]
                sel_files = set(meta["file_paths"])

                r_full = sum(1 for t in sol["selected_tiers"].values() if t == ResolutionTier.FULL)
                r_skel = sum(1 for t in sol["selected_tiers"].values() if t == ResolutionTier.SKELETON)
                r_stub = sum(1 for t in sol["selected_tiers"].values() if t == ResolutionTier.STUB)

                ledger_records.append({
                    "task_id": task_id, "repo": repo, "budget": budget,
                    "experiment_group": "candidate_pool_saturation",
                    "condition": f"saturation_K{k_val}", "K_pool": k_val,
                    "gold_recall_all": round(len(sel_files.intersection(set(gold_files_all))) / len(gold_files_all), 4) if gold_files_all else 0.0,
                    "gold_recall_pre_existing": round(len(sel_files.intersection(set(gold_pre_existing))) / len(gold_pre_existing), 4) if gold_pre_existing else None,
                    "retained_symbols_count": r_full + r_skel + r_stub,
                    "retained_full": r_full, "retained_skel": r_skel, "retained_stub": r_stub,
                    "syntactic_validity": evaluate_syntactic_validity(ctx_str),
                    "solve_time_ms": round(solve_ms, 2), "serialized_tokens": act_tokens,
                    "is_budget_compliant": (act_tokens <= budget)
                })

        t_task_elapsed = time.perf_counter() - t_task_start
        if (task_idx + 1) % 10 == 0 or (task_idx + 1) == len(tasks):
            print(f"[{task_idx+1:3d}/{len(tasks)}] Task {task_id} completed in {t_task_elapsed:.2f}s | Cumulative records: {len(ledger_records)}")

    # Save to CSV
    csv_path = "results/strategic_reset/experiment_ledger.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ledger_records[0].keys())
        writer.writeheader()
        writer.writerows(ledger_records)
    print(f"\n[DONE] Saved authoritative experiment ledger to {csv_path} ({len(ledger_records)} records).")

    # Save to JSON
    json_path = "results/strategic_reset/experiment_ledger.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ledger_records, f, indent=2)
    print(f"[DONE] Saved JSON experiment ledger to {json_path}")
    print(f"Total experiment runtime: {(time.perf_counter() - t_suite_start):.2f}s")


if __name__ == "__main__":
    main()

