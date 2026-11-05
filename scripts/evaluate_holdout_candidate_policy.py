"""
Strict Hold-Out Evaluation of Candidate-Depth Policies Grouped by Base Commit.

Enforces zero test leakage:
1. Groups 129 tasks by base commit.
2. Creates a stratified Development / Held-Out split (50/50).
3. Evaluates candidate depth policies on Development only.
4. Freezes the optimal policy.
5. Evaluates the frozen policy on untouched Held-Out tasks.
6. Computes paired differences, 95% CIs, effect sizes, and p-values.
"""

import json
import math
import os
import random
import sys
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats

def compute_paired_stats(s_base: pd.Series, s_treat: pd.Series):
    diff = s_treat - s_base
    n = len(diff)
    if n == 0:
        return {}
    mean_diff = float(diff.mean())
    std_diff = float(diff.std(ddof=1)) if n > 1 else 0.0
    sem = std_diff / math.sqrt(n) if n > 1 else 0.0
    ci_margin = stats.t.ppf(0.975, df=n-1) * sem if n > 1 and sem > 0 else 0.0
    cohens_dz = mean_diff / std_diff if std_diff > 1e-9 else 0.0
    
    if std_diff > 1e-9:
        t_stat, p_val = stats.ttest_rel(s_treat, s_base)
        try:
            w_stat, w_pval = stats.wilcoxon(s_treat, s_base)
        except Exception:
            w_stat, w_pval = 0.0, 1.0
    else:
        t_stat, p_val = 0.0, 1.0
        w_stat, w_pval = 0.0, 1.0
        
    return {
        "n": n,
        "mean_diff_pp": round(mean_diff * 100, 2),
        "ci_lower_pp": round((mean_diff - ci_margin) * 100, 2),
        "ci_upper_pp": round((mean_diff + ci_margin) * 100, 2),
        "cohens_dz": round(cohens_dz, 4),
        "t_stat": round(float(t_stat), 4),
        "p_val": float(p_val),
        "wilcoxon_pval": float(w_pval)
    }

def main():
    csv_path = "results/strategic_reset/experiment_ledger.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # 1. Group tasks by base commit and stratify by repo
    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]

    commit_to_tasks = defaultdict(list)
    commit_to_repo = {}
    for t in tasks:
        c = t.get("base_commit") or t.get("commit") or t["instance_id"]
        commit_to_tasks[c].append(t["instance_id"])
        commit_to_repo[c] = t["repo"]

    # Stratified split by repo
    repo_commits = defaultdict(list)
    for c, repo in commit_to_repo.items():
        repo_commits[repo].append(c)

    random.seed(42)  # Deterministic seed
    dev_tasks = []
    held_out_tasks = []

    for repo, c_list in repo_commits.items():
        random.shuffle(c_list)
        split_idx = len(c_list) // 2
        dev_commits = c_list[:split_idx]
        held_commits = c_list[split_idx:]
        
        for c in dev_commits:
            dev_tasks.extend(commit_to_tasks[c])
        for c in held_commits:
            held_out_tasks.extend(commit_to_tasks[c])

    print("=================================================================")
    print("      DEVELOPMENT / HELD-OUT SPLIT (ZERO TEST LEAKAGE)")
    print("=================================================================")
    print(f"Total Tasks: {len(tasks)}")
    print(f"Development Set Tasks (N={len(dev_tasks)}): {len(set(dev_tasks))} unique")
    print(f"Held-Out Set Tasks (N={len(held_out_tasks)}): {len(set(held_out_tasks))} unique")
    assert len(set(dev_tasks).intersection(set(held_out_tasks))) == 0, "DATA LEAKAGE DETECTED!"
    print("[PASS] Clean separation: 0 task overlap between Dev and Held-Out.")

    # 2. Define policies and evaluate on Development Set
    policies = {
        "Static_K60": lambda b: 60,
        "Static_K100": lambda b: 100,
        "Static_K200": lambda b: 200,
        "Static_K400": lambda b: 400,
        "Dynamic_Step": lambda b: {2000: 60, 4000: 100, 8000: 200, 16000: 400}[b],
        "Dynamic_Linear_Clamped": lambda b: {2000: 60, 4000: 100, 8000: 200, 16000: 400}[b]
    }

    budgets = [2000, 4000, 8000, 16000]

    def evaluate_policy_on_subset(task_subset, policy_fn):
        subset_df = df[df["task_id"].isin(task_subset)]
        results_by_budget = {}
        for b in budgets:
            target_k = policy_fn(b)
            if target_k == 60:
                sub = subset_df[(subset_df["budget"] == b) & (subset_df["condition"] == "F_mrtopos_milp")]
            else:
                sub = subset_df[(subset_df["budget"] == b) & (subset_df["condition"] == f"saturation_K{target_k}")]
            results_by_budget[b] = sub.sort_values("task_id")
        return results_by_budget

    print("\n=================================================================")
    print("          DEVELOPMENT SET POLICY TUNING (N=65)")
    print("=================================================================")
    dev_policy_metrics = {}
    for p_name, p_fn in policies.items():
        res = evaluate_policy_on_subset(dev_tasks, p_fn)
        recalls = [res[b]["gold_recall_all"].mean() for b in budgets]
        syntax_rates = [res[b]["syntactic_validity"].mean() for b in budgets]
        macro_rec = np.mean(recalls)
        dev_policy_metrics[p_name] = {
            "recalls": recalls,
            "macro_recall": macro_rec,
            "syntax_pct": np.mean(syntax_rates) * 100
        }
        print(f"Policy: {p_name:25s} | 2k: {recalls[0]*100:.2f}%, 4k: {recalls[1]*100:.2f}%, 8k: {recalls[2]*100:.2f}%, 16k: {recalls[3]*100:.2f}% | Macro: {macro_rec*100:.2f}% | Syntax: {np.mean(syntax_rates)*100:.1f}%")

    # Winner on Dev
    best_policy_name = max(dev_policy_metrics.keys(), key=lambda k: dev_policy_metrics[k]["macro_recall"])
    print(f"\n[WINNER ON DEV] {best_policy_name} achieved highest Macro Recall ({dev_policy_metrics[best_policy_name]['macro_recall']*100:.2f}%).")
    print(f"Freezing policy {best_policy_name} for independent Held-Out validation.")

    # 3. Independent Evaluation on Untouched Held-Out Set
    print("\n=================================================================")
    print(f"          INDEPENDENT HELD-OUT VALIDATION (N={len(held_out_tasks)})")
    print("=================================================================")
    held_baseline_res = evaluate_policy_on_subset(held_out_tasks, policies["Static_K60"])
    held_best_res = evaluate_policy_on_subset(held_out_tasks, policies[best_policy_name])

    held_out_analysis = {
        "dev_tasks_count": len(dev_tasks),
        "held_out_tasks_count": len(held_out_tasks),
        "selected_policy": best_policy_name,
        "dev_metrics": dev_policy_metrics,
        "held_out_comparisons": {}
    }

    print("\nHeld-Out Benchmark Results (Static K=60 vs Frozen Policy):")
    for b in budgets:
        s_base = held_baseline_res[b]["gold_recall_all"].reset_index(drop=True)
        s_best = held_best_res[b]["gold_recall_all"].reset_index(drop=True)
        p_stats = compute_paired_stats(s_base, s_best)
        held_out_analysis["held_out_comparisons"][str(b)] = p_stats
        
        base_mean = s_base.mean() * 100
        best_mean = s_best.mean() * 100
        sig_str = "***" if p_stats["p_val"] < 0.001 else ("**" if p_stats["p_val"] < 0.01 else ("*" if p_stats["p_val"] < 0.05 else "n.s."))
        print(f"Budget {b:5d} | Base K=60: {base_mean:.2f}% | Frozen Policy: {best_mean:.2f}% | Delta: {p_stats['mean_diff_pp']:+.2f} pp, 95% CI: [{p_stats['ci_lower_pp']:+.2f}, {p_stats['ci_upper_pp']:+.2f}], dz={p_stats['cohens_dz']:+.2f}, p={p_stats['p_val']:.4e} ({sig_str})")

    out_json = "results/candidate_policy_holdout_validation.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(held_out_analysis, f, indent=2)
    print(f"\n[DONE] Saved hold-out validation results to {out_json}")

if __name__ == "__main__":
    main()

