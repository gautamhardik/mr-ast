"""
Reconcile Held-Out Splits and Compute Authoritative Matched Baselines.

Root cause analysis:
- Split 1 (evaluate_holdout_candidate_policy.py): iterated over repo_commits.items()
- Split 2 (compute_matched_heldout_baselines.py): iterated over sorted(repo_commits.items())
Because random.shuffle() was called in different order, random seed 42 partitioned different tasks.

This script:
1. Reconstructs both splits exactly.
2. Compares task IDs, repos, and base commits.
3. Computes matched baseline recall across 2k, 4k, 8k, 16k for both splits.
4. Computes paired tests (Student's t and Wilcoxon) with task-level and commit-clustered CIs.
5. Computes Holm-Bonferroni corrections under:
   - Family 1: 4 tests per baseline (within-family)
   - Family 2: 12 tests omnibus (across all 3 baselines x 4 budgets)
6. Establishes Split 1 as authoritative and documents the withdrawal of Split 2.
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

def compute_paired(s_treat: pd.Series, s_ctrl: pd.Series, cluster_ids: pd.Series = None):
    diff = s_treat - s_ctrl
    n = len(diff)
    mean_diff = float(diff.mean())
    std_diff = float(diff.std(ddof=1)) if n > 1 else 0.0
    sem = std_diff / math.sqrt(n) if n > 1 else 0.0
    ci_margin_task = stats.t.ppf(0.975, df=n-1) * sem if n > 1 and sem > 0 else 0.0
    cohens_dz = mean_diff / std_diff if std_diff > 1e-9 else 0.0
    
    # Commit-clustered standard error calculation
    if cluster_ids is not None:
        cluster_df = pd.DataFrame({"diff": diff, "cluster": cluster_ids})
        cluster_means = cluster_df.groupby("cluster")["diff"].mean()
        n_clusters = len(cluster_means)
        cluster_std = float(cluster_means.std(ddof=1)) if n_clusters > 1 else 0.0
        cluster_sem = cluster_std / math.sqrt(n_clusters) if n_clusters > 1 else 0.0
        ci_margin_cluster = stats.t.ppf(0.975, df=n_clusters-1) * cluster_sem if n_clusters > 1 and cluster_sem > 0 else 0.0
    else:
        n_clusters = n
        ci_margin_cluster = ci_margin_task

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
        "n_tasks": n,
        "n_clusters": n_clusters,
        "mean_treat_pct": round(float(s_treat.mean()) * 100, 2),
        "mean_ctrl_pct": round(float(s_ctrl.mean()) * 100, 2),
        "mean_diff_pp": round(mean_diff * 100, 2),
        "ci_lower_task_pp": round((mean_diff - ci_margin_task) * 100, 2),
        "ci_upper_task_pp": round((mean_diff + ci_margin_task) * 100, 2),
        "ci_lower_cluster_pp": round((mean_diff - ci_margin_cluster) * 100, 2),
        "ci_upper_cluster_pp": round((mean_diff + ci_margin_cluster) * 100, 2),
        "cohens_dz": round(cohens_dz, 4),
        "t_stat": round(float(t_stat), 4),
        "raw_pval": float(p_val),
        "wilcoxon_pval": float(w_pval)
    }

def main():
    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]

    commit_to_tasks = defaultdict(list)
    commit_to_repo = {}
    task_to_commit = {}
    for t in tasks:
        c = t.get("base_commit") or t.get("commit") or t["instance_id"]
        commit_to_tasks[c].append(t["instance_id"])
        commit_to_repo[c] = t["repo"]
        task_to_commit[t["instance_id"]] = c

    # 1. Reconstruct Split 1 (Script 1)
    repo_commits1 = defaultdict(list)
    for c, repo in commit_to_repo.items():
        repo_commits1[repo].append(c)

    random.seed(42)
    dev1, held1 = [], []
    for repo, c_list in repo_commits1.items():
        c_copy = list(c_list)
        random.shuffle(c_copy)
        split_idx = len(c_copy) // 2
        for c in c_copy[:split_idx]: dev1.extend(commit_to_tasks[c])
        for c in c_copy[split_idx:]: held1.extend(commit_to_tasks[c])

    # 2. Reconstruct Split 2 (Script 2)
    repo_commits2 = defaultdict(list)
    for c, repo in commit_to_repo.items():
        repo_commits2[repo].append(c)

    random.seed(42)
    dev2, held2 = [], []
    for repo, c_list in sorted(repo_commits2.items()):
        c_copy = list(c_list)
        random.shuffle(c_copy)
        split_idx = len(c_copy) // 2
        for c in c_copy[:split_idx]: dev2.extend(commit_to_tasks[c])
        for c in c_copy[split_idx:]: held2.extend(commit_to_tasks[c])

    df = pd.read_csv("results/strategic_reset/experiment_ledger.csv")
    budgets = [2000, 4000, 8000, 16000]
    policy_k = {2000: 60, 4000: 100, 8000: 200, 16000: 400}

    def evaluate_split(held_task_list, split_name):
        held_df = df[df["task_id"].isin(held_task_list)].copy()
        held_df["base_commit"] = held_df["task_id"].map(task_to_commit)
        
        means = {}
        comp_scoped = {}
        comp_aider = {}
        comp_k60 = {}
        
        pvals_scoped = []
        pvals_aider = []
        pvals_k60 = []

        per_task_rows = []

        for b in budgets:
            k = policy_k[b]
            if k == 60:
                dyn = held_df[(held_df["budget"] == b) & (held_df["condition"] == "F_mrtopos_milp")].sort_values("task_id")
            else:
                dyn = held_df[(held_df["budget"] == b) & (held_df["condition"] == f"saturation_K{k}")].sort_values("task_id")
            
            k60 = held_df[(held_df["budget"] == b) & (held_df["condition"] == "F_mrtopos_milp")].sort_values("task_id")
            bm25 = held_df[(held_df["budget"] == b) & (held_df["condition"] == "A_scoped_bm25")].sort_values("task_id")
            aider = held_df[(held_df["budget"] == b) & (held_df["condition"] == "aider_repomap")].sort_values("task_id")

            s_dyn = dyn["gold_recall_all"].reset_index(drop=True)
            s_k60 = k60["gold_recall_all"].reset_index(drop=True)
            s_bm25 = bm25["gold_recall_all"].reset_index(drop=True)
            s_aider = aider["gold_recall_all"].reset_index(drop=True)
            clusters = dyn["base_commit"].reset_index(drop=True)

            for i in range(len(dyn)):
                per_task_rows.append({
                    "split": split_name,
                    "task_id": dyn["task_id"].iloc[i],
                    "base_commit": clusters.iloc[i],
                    "budget": b,
                    "target_k": k,
                    "dynamic_recall": s_dyn.iloc[i],
                    "scoped_bm25_recall": s_bm25.iloc[i],
                    "aider_repomap_recall": s_aider.iloc[i],
                    "static_k60_recall": s_k60.iloc[i]
                })

            means[str(b)] = {
                "dynamic": round(float(s_dyn.mean()) * 100, 2),
                "scoped_bm25": round(float(s_bm25.mean()) * 100, 2),
                "aider_repomap": round(float(s_aider.mean()) * 100, 2),
                "static_k60": round(float(s_k60.mean()) * 100, 2)
            }

            c_sc = compute_paired(s_dyn, s_bm25, clusters)
            c_ai = compute_paired(s_dyn, s_aider, clusters)
            c_60 = compute_paired(s_dyn, s_k60, clusters)

            comp_scoped[str(b)] = c_sc
            comp_aider[str(b)] = c_ai
            comp_k60[str(b)] = c_60

            pvals_scoped.append(c_sc["raw_pval"])
            pvals_aider.append(c_ai["raw_pval"])
            pvals_k60.append(c_60["raw_pval"])

        # Within-family Holm (m=4)
        holm_sc_4 = holm_bonferroni(pvals_scoped)
        holm_ai_4 = holm_bonferroni(pvals_aider)
        holm_60_4 = holm_bonferroni(pvals_k60)

        for i, b in enumerate(budgets):
            comp_scoped[str(b)]["holm_pval_family4"] = holm_sc_4[i]
            comp_aider[str(b)]["holm_pval_family4"] = holm_ai_4[i]
            comp_k60[str(b)]["holm_pval_family4"] = holm_60_4[i]

        # Omnibus family Holm (m=12 across all 3 baselines x 4 budgets)
        all_12_pvals = pvals_scoped + pvals_aider + pvals_k60
        all_12_holm = holm_bonferroni(all_12_pvals)
        for i, b in enumerate(budgets):
            comp_scoped[str(b)]["holm_pval_omnibus12"] = all_12_holm[i]
            comp_aider[str(b)]["holm_pval_omnibus12"] = all_12_holm[4 + i]
            comp_k60[str(b)]["holm_pval_omnibus12"] = all_12_holm[8 + i]

        return {
            "means": means,
            "vs_scoped_bm25": comp_scoped,
            "vs_aider_repomap": comp_aider,
            "vs_static_k60": comp_k60,
            "per_task_rows": per_task_rows
        }

    res1 = evaluate_split(held1, "Split_1_Original_Authoritative")
    res2 = evaluate_split(held2, "Split_2_Superseded_Secondary")

    # Save authoritative per-task CSV and summary JSON
    df_auth = pd.DataFrame(res1["per_task_rows"])
    df_auth.to_csv("results/heldout_authoritative_matched_baselines.csv", index=False)

    comparison_doc = {
        "reconciliation_summary": {
            "root_cause": "Split 1 used repo_commits.items() while Split 2 used sorted(repo_commits.items()), causing random.shuffle(seed=42) to process repos in a different order.",
            "overlap_task_count": len(set(held1).intersection(set(held2))),
            "differing_task_count": len(set(held1).symmetric_difference(set(held2))) // 2,
            "authoritative_split": "Split 1 (Original Frozen Split from evaluate_holdout_candidate_policy.py)",
            "superseded_split": "Split 2 (Accidental secondary sort in compute_matched_heldout_baselines.py)"
        },
        "authoritative_split_1": {
            "tasks_count": len(held1),
            "means": res1["means"],
            "vs_scoped_bm25": res1["vs_scoped_bm25"],
            "vs_aider_repomap": res1["vs_aider_repomap"],
            "vs_static_k60": res1["vs_static_k60"]
        },
        "superseded_split_2": {
            "tasks_count": len(held2),
            "means": res2["means"],
            "vs_scoped_bm25": res2["vs_scoped_bm25"],
            "vs_aider_repomap": res2["vs_aider_repomap"],
            "vs_static_k60": res2["vs_static_k60"]
        }
    }

    with open("results/heldout_reconciliation_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison_doc, f, indent=2)

    # Print Reconciliation Table
    print("==========================================================================================")
    print("           HELD-OUT RECONCILIATION TABLE: SPLIT 1 (AUTH) VS SPLIT 2 (SUPERSEDED)")
    print("==========================================================================================")
    print(f"{'Budget':<8} | {'Method':<20} | {'Split 1 (Authoritative)':<25} | {'Split 2 (Superseded)':<25}")
    print("-" * 88)
    for b in budgets:
        m1 = res1["means"][str(b)]
        m2 = res2["means"][str(b)]
        print(f"{b:<8} | {'Dynamic Policy':<20} | {m1['dynamic']:>6.2f}%                    | {m2['dynamic']:>6.2f}%")
        print(f"{'':<8} | {'Scoped BM25':<20} | {m1['scoped_bm25']:>6.2f}%                    | {m2['scoped_bm25']:>6.2f}%")
        print(f"{'':<8} | {'Aider RepoMap':<20} | {m1['aider_repomap']:>6.2f}%                    | {m2['aider_repomap']:>6.2f}%")
        print(f"{'':<8} | {'Static K=60':<20} | {m1['static_k60']:>6.2f}%                    | {m2['static_k60']:>6.2f}%")
        print("-" * 88)

    print("\n==========================================================================================")
    print("     AUTHORITATIVE STATISTICAL SIGNIFICANCE (SPLIT 1: ORIGINAL 66 HELD-OUT TASKS)")
    print("==========================================================================================")
    for baseline, comp_key in [("Scoped BM25", "vs_scoped_bm25"), ("Aider RepoMap", "vs_aider_repomap"), ("Static K=60", "vs_static_k60")]:
        print(f"\n--- DYNAMIC POLICY VS {baseline.upper()} ---")
        for b in budgets:
            c = res1[comp_key][str(b)]
            sig4 = "***" if c["holm_pval_family4"] < 0.001 else ("**" if c["holm_pval_family4"] < 0.01 else ("*" if c["holm_pval_family4"] < 0.05 else "n.s."))
            sig12 = "***" if c["holm_pval_omnibus12"] < 0.001 else ("**" if c["holm_pval_omnibus12"] < 0.01 else ("*" if c["holm_pval_omnibus12"] < 0.05 else "n.s."))
            print(f"B={b:5d} | Delta: {c['mean_diff_pp']:+5.2f} pp | Task 95% CI: [{c['ci_lower_task_pp']:+5.2f}, {c['ci_upper_task_pp']:+5.2f}] | Cluster 95% CI: [{c['ci_lower_cluster_pp']:+5.2f}, {c['ci_upper_cluster_pp']:+5.2f}]")
            print(f"        | dz={c['cohens_dz']:+5.2f} | Raw p={c['raw_pval']:.4e} | Holm-4 p={c['holm_pval_family4']:.4e} ({sig4}) | Holm-12 p={c['holm_pval_omnibus12']:.4e} ({sig12})")

if __name__ == "__main__":
    main()

