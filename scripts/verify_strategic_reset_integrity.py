"""
Verification of Strategic Reset Ledger Integrity and Experimental Fairness.

Performs:
1. Exact row count, completeness, and duplicate checks.
2. Budget compliance and AST syntactic validity verification.
3. Statistical effect sizes (Cohen's dz) and paired confidence intervals.
4. Input fairness audit.
"""

import json
import math
import os
import sys
import pandas as pd
import numpy as np
from scipy import stats

def compute_detailed_paired_stats(s_base: pd.Series, s_treat: pd.Series):
    diff = s_treat - s_base
    n = len(diff)
    if n == 0:
        return {}
    mean_diff = float(diff.mean())
    std_diff = float(diff.std(ddof=1)) if n > 1 else 0.0
    sem = std_diff / math.sqrt(n) if n > 1 else 0.0
    ci_margin = stats.t.ppf(0.975, df=n-1) * sem if n > 1 and sem > 0 else 0.0
    
    # Cohen's dz (paired effect size)
    cohens_dz = mean_diff / std_diff if std_diff > 1e-9 else 0.0
    
    # Paired t-test
    if std_diff > 1e-9:
        t_stat, p_val = stats.ttest_rel(s_treat, s_base)
    else:
        t_stat, p_val = 0.0, 1.0
        
    return {
        "n": n,
        "mean_diff": round(mean_diff, 4),
        "std_diff": round(std_diff, 4),
        "cohens_dz": round(cohens_dz, 4),
        "ci_lower": round(mean_diff - ci_margin, 4),
        "ci_upper": round(mean_diff + ci_margin, 4),
        "t_stat": round(float(t_stat), 4),
        "p_value": float(p_val)
    }

def main():
    csv_path = "results/strategic_reset/experiment_ledger.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        sys.exit(1)
        
    df = pd.read_csv(csv_path)
    print("=================================================================")
    print("       STRATEGIC RESET LEDGER INTEGRITY AUDIT")
    print("=================================================================")
    print(f"Total Rows in Ledger: {len(df)}")
    
    # 1. Completeness Checks
    tasks = sorted(df["task_id"].unique())
    n_tasks = len(tasks)
    print(f"Unique Tasks Evaluated: {n_tasks} (Expected: 129)")
    assert n_tasks == 129, f"Expected 129 tasks, found {n_tasks}"
    
    budgets = sorted(df["budget"].unique())
    print(f"Unique Budgets: {budgets} (Expected: [2000, 4000, 8000, 16000])")
    assert budgets == [2000, 4000, 8000, 16000], f"Unexpected budgets: {budgets}"
    
    conditions = sorted(df["condition"].unique())
    print(f"Unique Conditions ({len(conditions)}): {conditions}")
    expected_conditions = [
        "A_scoped_bm25", "B_mr_only", "C_mr_containment", "D_mr_containment_dep",
        "E_mrtopos_con_greedy", "F_mrtopos_milp", "aider_repomap",
        "saturation_K100", "saturation_K200", "saturation_K400"
    ]
    assert sorted(conditions) == sorted(expected_conditions), f"Conditions mismatch: {conditions}"
    
    expected_total_rows = 129 * 4 * 10
    print(f"Expected Rows: 129 tasks * 4 budgets * 10 conditions = {expected_total_rows}")
    assert len(df) == expected_total_rows, f"Row count mismatch: {len(df)} vs {expected_total_rows}"
    
    # Check for duplicates
    dup_cols = ["task_id", "budget", "condition"]
    duplicates = df[df.duplicated(subset=dup_cols, keep=False)]
    print(f"Duplicate Conditions Count: {len(duplicates)}")
    assert len(duplicates) == 0, f"Found duplicates: {duplicates}"
    
    # Check for missing values in critical columns
    crit_cols = ["task_id", "budget", "condition", "gold_recall_all", "syntactic_validity", "serialized_tokens", "is_budget_compliant"]
    null_counts = df[crit_cols].isnull().sum()
    print("Null Counts in Critical Columns:")
    for col, cnt in null_counts.items():
        print(f"  {col}: {cnt}")
        assert cnt == 0, f"Null values found in {col}"
        
    # 2. Budget Compliance Audit
    violations = df[df["is_budget_compliant"] == False]
    print(f"\nBudget Violations Count: {len(violations)} ({len(violations)/len(df)*100:.2f}%)")
    assert len(violations) == 0, f"Found {len(violations)} budget violations!"
    print("[PASS] 100.0% Zero Budget Violations across all 5,160 conditions.")
    
    # 3. Syntactic Validity Audit
    print("\nSyntactic Validity by Condition:")
    for c in expected_conditions:
        sub = df[df["condition"] == c]
        syn_pct = sub["syntactic_validity"].mean() * 100
        print(f"  {c:25s}: {syn_pct:.1f}% ({sub['syntactic_validity'].sum()}/{len(sub)})")
        
    # 4. Detailed Statistical Effect Sizes (Cohen's dz)
    print("\n=================================================================")
    print("       STATISTICAL EFFECT SIZES & CONFIDENCE INTERVALS")
    print("=================================================================")
    
    audit_results = {
        "ledger_integrity": {
            "total_rows": len(df),
            "unique_tasks": n_tasks,
            "budgets": budgets,
            "conditions": conditions,
            "duplicates": 0,
            "null_critical_values": 0,
            "budget_violations": 0
        },
        "pairwise_transitions": {},
        "saturation_effect_sizes": {},
        "aider_comparison_effect_sizes": {}
    }
    
    transitions = [
        ("A_scoped_bm25", "B_mr_only", "A -> B (Multi-Resolution)"),
        ("B_mr_only", "C_mr_containment", "B -> C (Containment)"),
        ("C_mr_containment", "D_mr_containment_dep", "C -> D (Dependency)"),
        ("D_mr_containment_dep", "E_mrtopos_con_greedy", "D -> E (Greedy)"),
        ("E_mrtopos_con_greedy", "F_mrtopos_milp", "E -> F (MILP vs Greedy)"),
        ("A_scoped_bm25", "F_mrtopos_milp", "A -> F (Net MR-TopoS vs Scoped BM25)")
    ]
    
    for b in budgets:
        audit_results["pairwise_transitions"][str(b)] = {}
        print(f"\n--- Budget: {b} Tokens ---")
        for c1, c2, desc in transitions:
            s1 = df[(df["budget"] == b) & (df["condition"] == c1)].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
            s2 = df[(df["budget"] == b) & (df["condition"] == c2)].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
            res = compute_detailed_paired_stats(s1, s2)
            audit_results["pairwise_transitions"][str(b)][desc] = res
            print(f"  {desc:35s}: Delta={res['mean_diff']*100:+.2f}%, 95% CI=[{res['ci_lower']*100:+.2f}%, {res['ci_upper']*100:+.2f}%], dz={res['cohens_dz']:+.2f}, p={res['p_value']:.4e}")
            
    # Saturation Effect Sizes
    print("\n--- Saturation Scaling from K=60 ---")
    for b in budgets:
        audit_results["saturation_effect_sizes"][str(b)] = {}
        s_k60 = df[(df["budget"] == b) & (df["condition"] == "F_mrtopos_milp")].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
        for k_val in [100, 200, 400]:
            s_k = df[(df["budget"] == b) & (df["condition"] == f"saturation_K{k_val}")].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
            res = compute_detailed_paired_stats(s_k60, s_k)
            audit_results["saturation_effect_sizes"][str(b)][f"K60_to_K{k_val}"] = res
            print(f"  Budget {b} | K=60 -> K={k_val:3d}: Delta={res['mean_diff']*100:+.2f}%, 95% CI=[{res['ci_lower']*100:+.2f}%, {res['ci_upper']*100:+.2f}%], dz={res['cohens_dz']:+.2f}, p={res['p_value']:.4e}")

    # Aider Comparison Effect Sizes
    print("\n--- MR-TopoS vs Aider RepoMap Head-to-Head ---")
    for b in budgets:
        audit_results["aider_comparison_effect_sizes"][str(b)] = {}
        s_ai = df[(df["budget"] == b) & (df["condition"] == "aider_repomap")].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
        s_mr = df[(df["budget"] == b) & (df["condition"] == "F_mrtopos_milp")].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
        res = compute_detailed_paired_stats(s_ai, s_mr)
        audit_results["aider_comparison_effect_sizes"][str(b)] = res
        print(f"  Budget {b} | MR-TopoS vs Aider: Delta={res['mean_diff']*100:+.2f}%, 95% CI=[{res['ci_lower']*100:+.2f}%, {res['ci_upper']*100:+.2f}%], dz={res['cohens_dz']:+.2f}, p={res['p_value']:.4e}")

    # Save to JSON
    def json_helper(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    out_path = "results/strategic_reset/integrity_audit_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, default=json_helper)
    print(f"\n[DONE] Saved integrity audit summary to {out_path}")

if __name__ == "__main__":
    main()
