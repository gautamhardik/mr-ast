"""
Matched Held-Out Baseline Evaluation across 66 Tasks.

Evaluates on the EXACT SAME 66 held-out tasks:
1. Selected Dynamic-K Policy (K=60 at 2k, 100 at 4k, 200 at 8k, 400 at 16k)
2. Scoped BM25 (Condition A)
3. Aider-Inspired Static Repository Map Baseline (aider_repomap)
4. Static K=60 Reference (Condition F)

Generates:
- results/heldout_split_manifest.json
- results/matched_heldout_baselines.csv
- results/matched_heldout_summary.json
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

def holm_bonferroni(p_vals):
    m = len(p_vals)
    indexed = sorted(enumerate(p_vals), key=lambda x: x[1])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        adj = min(1.0, (m - rank) * p)
        running_max = max(running_max, adj)
        adjusted[orig_idx] = round(running_max, 6)
    return adjusted

def compute_paired(s_treat: pd.Series, s_ctrl: pd.Series):
    diff = s_treat - s_ctrl
    n = len(diff)
    mean_diff = float(diff.mean())
    std_diff = float(diff.std(ddof=1)) if n > 1 else 0.0
    sem = std_diff / math.sqrt(n) if n > 1 else 0.0
    ci_margin = stats.t.ppf(0.975, df=n-1) * sem if n > 1 and sem > 0 else 0.0
    cohens_dz = mean_diff / std_diff if std_diff > 1e-9 else 0.0
    
    if std_diff > 1e-9:
        t_stat, p_val = stats.ttest_rel(s_treat, s_ctrl)
        try:
            w_stat, w_pval = stats.wilcoxon(s_treat, s_ctrl)
        except Exception:
            w_stat, w_pval = 0.0, 1.0
    else:
        t_stat, p_val = 0.0, 1.0
        w_stat, w_pval = 0.0, 1.0
        
    return {
        "n": n,
        "mean_treat_pct": round(float(s_treat.mean()) * 100, 2),
        "mean_ctrl_pct": round(float(s_ctrl.mean()) * 100, 2),
        "mean_diff_pp": round(mean_diff * 100, 2),
        "ci_lower_pp": round((mean_diff - ci_margin) * 100, 2),
        "ci_upper_pp": round((mean_diff + ci_margin) * 100, 2),
        "cohens_dz": round(cohens_dz, 4),
        "t_stat": round(float(t_stat), 4),
        "raw_pval": float(p_val),
        "wilcoxon_pval": float(w_pval)
    }

def main():
    ledger_path = "results/strategic_reset/experiment_ledger.csv"
    if not os.path.exists(ledger_path):
        print(f"Error: {ledger_path} not found.")
        sys.exit(1)

    df = pd.read_csv(ledger_path)

    # 1. Load tasks and build split
    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]

    commit_to_tasks = defaultdict(list)
    commit_to_repo = {}
    task_info = {}
    for t in tasks:
        c = t.get("base_commit") or t.get("commit") or t["instance_id"]
        commit_to_tasks[c].append(t["instance_id"])
        commit_to_repo[c] = t["repo"]
        task_info[t["instance_id"]] = {
            "task_id": t["instance_id"],
            "repo": t["repo"],
            "base_commit": c
        }

    repo_commits = defaultdict(list)
    for c, repo in commit_to_repo.items():
        repo_commits[repo].append(c)

    random.seed(42)
    dev_tasks = []
    held_out_tasks = []

    for repo, c_list in sorted(repo_commits.items()):
        random.shuffle(c_list)
        split_idx = len(c_list) // 2
        dev_commits = c_list[:split_idx]
        held_commits = c_list[split_idx:]
        for c in dev_commits:
            dev_tasks.extend(commit_to_tasks[c])
        for c in held_commits:
            held_out_tasks.extend(commit_to_tasks[c])

    # Save manifest
    manifest = {
        "split_seed": 42,
        "stratification": "base_commit grouped, repo stratified",
        "dev_set": {
            "count": len(dev_tasks),
            "commits_count": len(set(task_info[tid]["base_commit"] for tid in dev_tasks)),
            "task_ids": sorted(dev_tasks)
        },
        "held_out_set": {
            "count": len(held_out_tasks),
            "commits_count": len(set(task_info[tid]["base_commit"] for tid in held_out_tasks)),
            "tasks": [task_info[tid] for tid in sorted(held_out_tasks)]
        }
    }
    with open("results/heldout_split_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved manifest: {len(dev_tasks)} Dev tasks, {len(held_out_tasks)} Held-Out tasks.")

    # 2. Extract matched records on held-out tasks
    held_ids = set(held_out_tasks)
    held_df = df[df["task_id"].isin(held_ids)].copy()

    budgets = [2000, 4000, 8000, 16000]
    policy_k_map = {2000: 60, 4000: 100, 8000: 200, 16000: 400}

    per_task_records = []
    summary_results = {
        "held_out_tasks_count": len(held_out_tasks),
        "budgets": budgets,
        "methods_evaluated": ["Dynamic_Policy", "Scoped_BM25", "Aider_RepoMap_Baseline", "Static_K60"],
        "means_by_budget": {},
        "comparisons_vs_scoped_bm25": {},
        "comparisons_vs_aider_repomap": {},
        "comparisons_vs_static_k60": {}
    }

    pvals_vs_scoped = []
    pvals_vs_aider = []
    pvals_vs_k60 = []

    for b in budgets:
        # Dynamic policy rows
        target_k = policy_k_map[b]
        if target_k == 60:
            dyn_sub = held_df[(held_df["budget"] == b) & (held_df["condition"] == "F_mrtopos_milp")].sort_values("task_id")
        else:
            dyn_sub = held_df[(held_df["budget"] == b) & (held_df["condition"] == f"saturation_K{target_k}")].sort_values("task_id")

        scoped_sub = held_df[(held_df["budget"] == b) & (held_df["condition"] == "A_scoped_bm25")].sort_values("task_id")
        aider_sub = held_df[(held_df["budget"] == b) & (held_df["condition"] == "aider_repomap")].sort_values("task_id")
        k60_sub = held_df[(held_df["budget"] == b) & (held_df["condition"] == "F_mrtopos_milp")].sort_values("task_id")

        # Verify task alignment
        tasks_dyn = dyn_sub["task_id"].tolist()
        tasks_scoped = scoped_sub["task_id"].tolist()
        tasks_aider = aider_sub["task_id"].tolist()
        assert tasks_dyn == tasks_scoped == tasks_aider, f"Task mismatch at budget {b}"

        s_dyn = dyn_sub["gold_recall_all"].reset_index(drop=True)
        s_scoped = scoped_sub["gold_recall_all"].reset_index(drop=True)
        s_aider = aider_sub["gold_recall_all"].reset_index(drop=True)
        s_k60 = k60_sub["gold_recall_all"].reset_index(drop=True)

        for i, tid in enumerate(tasks_dyn):
            per_task_records.append({
                "task_id": tid,
                "budget": b,
                "target_k": target_k,
                "dynamic_policy_recall": s_dyn.iloc[i],
                "scoped_bm25_recall": s_scoped.iloc[i],
                "aider_repomap_recall": s_aider.iloc[i],
                "static_k60_recall": s_k60.iloc[i],
                "diff_vs_scoped": s_dyn.iloc[i] - s_scoped.iloc[i],
                "diff_vs_aider": s_dyn.iloc[i] - s_aider.iloc[i],
                "diff_vs_static_k60": s_dyn.iloc[i] - s_k60.iloc[i]
            })

        summary_results["means_by_budget"][str(b)] = {
            "dynamic_policy": round(float(s_dyn.mean()) * 100, 2),
            "scoped_bm25": round(float(s_scoped.mean()) * 100, 2),
            "aider_repomap": round(float(s_aider.mean()) * 100, 2),
            "static_k60": round(float(s_k60.mean()) * 100, 2)
        }

        comp_scoped = compute_paired(s_dyn, s_scoped)
        comp_aider = compute_paired(s_dyn, s_aider)
        comp_k60 = compute_paired(s_dyn, s_k60)

        summary_results["comparisons_vs_scoped_bm25"][str(b)] = comp_scoped
        summary_results["comparisons_vs_aider_repomap"][str(b)] = comp_aider
        summary_results["comparisons_vs_static_k60"][str(b)] = comp_k60

        pvals_vs_scoped.append(comp_scoped["raw_pval"])
        pvals_vs_aider.append(comp_aider["raw_pval"])
        pvals_vs_k60.append(comp_k60["raw_pval"])

    # Holm-Bonferroni correction across the 4 budgets for each baseline
    holm_scoped = holm_bonferroni(pvals_vs_scoped)
    holm_aider = holm_bonferroni(pvals_vs_aider)
    holm_k60 = holm_bonferroni(pvals_vs_k60)

    for i, b in enumerate(budgets):
        summary_results["comparisons_vs_scoped_bm25"][str(b)]["holm_pval"] = holm_scoped[i]
        summary_results["comparisons_vs_aider_repomap"][str(b)]["holm_pval"] = holm_aider[i]
        summary_results["comparisons_vs_static_k60"][str(b)]["holm_pval"] = holm_k60[i]

    # Save per-task CSV and summary JSON
    df_per_task = pd.DataFrame(per_task_records)
    df_per_task.to_csv("results/matched_heldout_baselines.csv", index=False)
    with open("results/matched_heldout_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=2)

    print("\n=================================================================")
    print("      MATCHED HELD-OUT RECALL MEANS (66 HELD-OUT TASKS)")
    print("=================================================================")
    for b in budgets:
        m = summary_results["means_by_budget"][str(b)]
        print(f"Budget {b:5d} | Dynamic: {m['dynamic_policy']:5.2f}% | Scoped BM25: {m['scoped_bm25']:5.2f}% | Aider RepoMap: {m['aider_repomap']:5.2f}% | Static K=60: {m['static_k60']:5.2f}%")

    print("\n=================================================================")
    print("      PAIRED COMPARISONS: DYNAMIC POLICY VS BASELINES")
    print("=================================================================")
    print("\n--- VS SCOPED BM25 ---")
    for b in budgets:
        c = summary_results["comparisons_vs_scoped_bm25"][str(b)]
        sig = "***" if c["holm_pval"] < 0.001 else ("**" if c["holm_pval"] < 0.01 else ("*" if c["holm_pval"] < 0.05 else "n.s."))
        print(f"Budget {b:5d} | Delta: {c['mean_diff_pp']:+5.2f} pp [{c['ci_lower_pp']:+5.2f}, {c['ci_upper_pp']:+5.2f}] | dz={c['cohens_dz']:+5.2f} | Raw p={c['raw_pval']:.4e} | Holm p={c['holm_pval']:.4e} ({sig})")

    print("\n--- VS AIDER-INSPIRED REPOMAP BASELINE ---")
    for b in budgets:
        c = summary_results["comparisons_vs_aider_repomap"][str(b)]
        sig = "***" if c["holm_pval"] < 0.001 else ("**" if c["holm_pval"] < 0.01 else ("*" if c["holm_pval"] < 0.05 else "n.s."))
        print(f"Budget {b:5d} | Delta: {c['mean_diff_pp']:+5.2f} pp [{c['ci_lower_pp']:+5.2f}, {c['ci_upper_pp']:+5.2f}] | dz={c['cohens_dz']:+5.2f} | Raw p={c['raw_pval']:.4e} | Holm p={c['holm_pval']:.4e} ({sig})")

    print("\n--- VS STATIC K=60 BASE ---")
    for b in budgets:
        c = summary_results["comparisons_vs_static_k60"][str(b)]
        sig = "***" if c["holm_pval"] < 0.001 else ("**" if c["holm_pval"] < 0.01 else ("*" if c["holm_pval"] < 0.05 else "n.s."))
        print(f"Budget {b:5d} | Delta: {c['mean_diff_pp']:+5.2f} pp [{c['ci_lower_pp']:+5.2f}, {c['ci_upper_pp']:+5.2f}] | dz={c['cohens_dz']:+5.2f} | Raw p={c['raw_pval']:.4e} | Holm p={c['holm_pval']:.4e} ({sig})")

if __name__ == "__main__":
    main()

