"""
Multiple-Testing Correction and Commit-Aware Uncertainty Analysis.

Computes:
1. Exact recall differences in percentage points (pp).
2. Holm-Bonferroni step-down adjusted p-values across all confirmatory ablation comparisons.
3. Cluster-robust standard errors grouped by base commit.
4. Paired confidence intervals and Cohen's dz.
"""

import json
import math
import os
import sys
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

def holm_bonferroni(p_values: list) -> list:
    """Computes step-down Holm-Bonferroni adjusted p-values."""
    m = len(p_values)
    # Sort with original indices
    indexed_p = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    cum_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed_p):
        adj_p = (m - rank) * p
        adj_p = min(1.0, adj_p)
        cum_max = max(cum_max, adj_p)
        adjusted[orig_idx] = round(cum_max, 6)
    return adjusted

def compute_cluster_robust_diff(s_base: pd.Series, s_treat: pd.Series, clusters: pd.Series):
    """Computes mean difference and cluster-robust standard error using clustered OLS."""
    diff = s_treat - s_base
    n = len(diff)
    df_cluster = pd.DataFrame({"diff": diff, "const": 1.0, "cluster": clusters})
    
    # Fit OLS with clustered SE
    model = sm.OLS(df_cluster["diff"], df_cluster["const"])
    res = model.fit(cov_type="cluster", cov_kwds={"groups": df_cluster["cluster"]})
    
    mean_diff = float(res.params["const"])
    cluster_se = float(res.bse["const"])
    t_stat = float(res.tvalues["const"])
    cluster_pval = float(res.pvalues["const"])
    
    # Paired regular stats
    std_diff = float(diff.std(ddof=1)) if n > 1 else 0.0
    regular_sem = std_diff / math.sqrt(n) if n > 1 else 0.0
    regular_pval = float(stats.ttest_rel(s_treat, s_base)[1]) if std_diff > 1e-9 else 1.0
    cohens_dz = mean_diff / std_diff if std_diff > 1e-9 else 0.0
    
    # 95% CI based on cluster robust SE
    crit_val = stats.t.ppf(0.975, df=len(clusters.unique()) - 1)
    ci_lower = mean_diff - crit_val * cluster_se
    ci_upper = mean_diff + crit_val * cluster_se
    
    return {
        "n": n,
        "n_clusters": int(len(clusters.unique())),
        "mean_diff_pp": round(mean_diff * 100, 2),
        "cluster_se_pp": round(cluster_se * 100, 2),
        "cluster_ci_lower_pp": round(ci_lower * 100, 2),
        "cluster_ci_upper_pp": round(ci_upper * 100, 2),
        "regular_sem_pp": round(regular_sem * 100, 2),
        "cohens_dz": round(cohens_dz, 4),
        "raw_pval": regular_pval,
        "cluster_pval": cluster_pval
    }

def main():
    csv_path = "results/strategic_reset/experiment_ledger.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # Load tasks to get base commits
    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]
    task_to_commit = {t["instance_id"]: t.get("base_commit") or t.get("commit") or t["instance_id"] for t in tasks}

    df["base_commit"] = df["task_id"].map(task_to_commit)

    budgets = [2000, 4000, 8000, 16000]

    transitions = [
        ("A_scoped_bm25", "B_mr_only", "A -> B: Multi-Resolution Representation"),
        ("B_mr_only", "C_mr_containment", "B -> C: AST Precedence Containment"),
        ("C_mr_containment", "D_mr_containment_dep", "C -> D: Dependency Scoring (lambda=0.5)"),
        ("D_mr_containment_dep", "E_mrtopos_con_greedy", "D -> E: Greedy Context Packing"),
        ("E_mrtopos_con_greedy", "F_mrtopos_milp", "E -> F: Exact MILP vs Greedy"),
        ("A_scoped_bm25", "F_mrtopos_milp", "A -> F: Total Net MR-TopoS Advantage")
    ]

    all_comparisons = []

    for b in budgets:
        for c1, c2, desc in transitions:
            s1 = df[(df["budget"] == b) & (df["condition"] == c1)].sort_values("task_id")
            s2 = df[(df["budget"] == b) & (df["condition"] == c2)].sort_values("task_id")
            clusters = s1["base_commit"].reset_index(drop=True)
            
            res = compute_cluster_robust_diff(s1["gold_recall_all"].reset_index(drop=True),
                                              s2["gold_recall_all"].reset_index(drop=True),
                                              clusters)
            res["budget"] = b
            res["transition"] = f"{c1} -> {c2}"
            res["description"] = desc
            all_comparisons.append(res)

    # Apply Holm-Bonferroni correction within budget families (6 hypotheses per budget)
    print("=================================================================")
    print("      MULTIPLE-TESTING CORRECTION & COMMIT-AWARE STATS")
    print("=================================================================")

    summary_records = []
    for b in budgets:
        b_comps = [c for c in all_comparisons if c["budget"] == b]
        raw_pvals = [c["raw_pval"] for c in b_comps]
        cluster_pvals = [c["cluster_pval"] for c in b_comps]
        
        holm_raw = holm_bonferroni(raw_pvals)
        holm_cluster = holm_bonferroni(cluster_pvals)
        
        print(f"\n--- Budget: {b} Tokens (Family-Wise Error Rate Control across 6 tests) ---")
        for i, c in enumerate(b_comps):
            c["holm_raw_pval"] = holm_raw[i]
            c["holm_cluster_pval"] = holm_cluster[i]
            summary_records.append(c)
            
            sig_raw = "***" if c["holm_raw_pval"] < 0.001 else ("**" if c["holm_raw_pval"] < 0.01 else ("*" if c["holm_raw_pval"] < 0.05 else "n.s."))
            sig_cluster = "***" if c["holm_cluster_pval"] < 0.001 else ("**" if c["holm_cluster_pval"] < 0.01 else ("*" if c["holm_cluster_pval"] < 0.05 else "n.s."))
            
            print(f"  {c['description']:42s} | Delta={c['mean_diff_pp']:+6.2f} pp | Cluster 95% CI=[{c['cluster_ci_lower_pp']:+6.2f}, {c['cluster_ci_upper_pp']:+6.2f}] | dz={c['cohens_dz']:+5.2f} | Raw p={c['raw_pval']:.4f} (Holm: {c['holm_raw_pval']:.4f}, {sig_raw}) | Clustered p={c['cluster_pval']:.4f} (Holm: {c['holm_cluster_pval']:.4f}, {sig_cluster})")

    out_file = "results/multiple_testing_statistical_summary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary_records, f, indent=2)
    print(f"\n[DONE] Saved statistical summary to {out_file}")

if __name__ == "__main__":
    main()

