"""
Generates the authoritative final CSV tables:
1. research/final_ablation_table.csv (Mean performance by condition and budget)
2. research/final_statistical_table.csv (Paired differences, 95% CIs, effect sizes, raw and Holm p-values)
"""

import json
import math
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

def holm_bonferroni(p_values: list) -> list:
    m = len(p_values)
    indexed_p = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * m
    cum_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed_p):
        adj_p = (m - rank) * p
        adj_p = min(1.0, adj_p)
        cum_max = max(cum_max, adj_p)
        adjusted[orig_idx] = round(cum_max, 6)
    return adjusted

def main():
    csv_path = "results/strategic_reset/experiment_ledger.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    # 1. Final Ablation Table CSV
    conds = [
        "A_scoped_bm25", "B_mr_only", "C_mr_containment",
        "D_mr_containment_dep", "E_mrtopos_con_greedy", "F_mrtopos_milp"
    ]
    budgets = [2000, 4000, 8000, 16000]

    ablation_rows = []
    for b in budgets:
        for c in conds:
            sub = df[(df["budget"] == b) & (df["condition"] == c)]
            r_all = sub["gold_recall_all"].mean()
            r_pre = sub["gold_recall_pre_existing"].dropna().mean()
            syms = sub["retained_symbols_count"].mean()
            full_s = sub["retained_full"].mean()
            skel_s = sub["retained_skel"].mean()
            stub_s = sub["retained_stub"].mean()
            syn = sub["syntactic_validity"].mean() * 100
            t_ms = sub["solve_time_ms"].mean()
            tokens = sub["serialized_tokens"].mean()
            comp = sub["is_budget_compliant"].mean() * 100

            ablation_rows.append({
                "budget": b,
                "condition": c,
                "gold_recall_all_pct": round(r_all * 100, 2),
                "gold_recall_pre_existing_pct": round(r_pre * 100, 2),
                "retained_symbols_total": round(syms, 1),
                "retained_full_impls": round(full_s, 1),
                "retained_skeletons": round(skel_s, 1),
                "retained_stubs": round(stub_s, 1),
                "ast_parse_validity_pct": round(syn, 1),
                "serialized_tokens_mean": round(tokens, 1),
                "budget_compliance_pct": round(comp, 1),
                "solve_time_ms": round(t_ms, 2)
            })

    df_abl = pd.DataFrame(ablation_rows)
    out_abl_csv = "research/final_ablation_table.csv"
    df_abl.to_csv(out_abl_csv, index=False)
    print(f"[DONE] Saved {out_abl_csv} ({len(df_abl)} rows).")

    # 2. Final Statistical Table CSV
    transitions = [
        ("A_scoped_bm25", "B_mr_only", "A -> B: Multi-Resolution Representation"),
        ("B_mr_only", "C_mr_containment", "B -> C: AST Precedence Containment"),
        ("C_mr_containment", "D_mr_containment_dep", "C -> D: Topological Dependency Scoring"),
        ("D_mr_containment_dep", "E_mrtopos_con_greedy", "D -> E: Greedy Context Packing"),
        ("E_mrtopos_con_greedy", "F_mrtopos_milp", "E -> F: Exact MILP vs Greedy"),
        ("A_scoped_bm25", "F_mrtopos_milp", "A -> F: Total Net MR-TopoS Advantage")
    ]

    stat_rows = []
    for b in budgets:
        b_pvals = []
        b_records = []
        for c1, c2, desc in transitions:
            s1 = df[(df["budget"] == b) & (df["condition"] == c1)].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
            s2 = df[(df["budget"] == b) & (df["condition"] == c2)].sort_values("task_id")["gold_recall_all"].reset_index(drop=True)
            diff = s2 - s1
            n = len(diff)
            mean_diff = float(diff.mean())
            std_diff = float(diff.std(ddof=1)) if n > 1 else 0.0
            sem = std_diff / math.sqrt(n) if n > 1 else 0.0
            ci_margin = stats.t.ppf(0.975, df=n-1) * sem if n > 1 and sem > 0 else 0.0
            dz = mean_diff / std_diff if std_diff > 1e-9 else 0.0
            
            if std_diff > 1e-9:
                t_stat, p_val = stats.ttest_rel(s2, s1)
            else:
                t_stat, p_val = 0.0, 1.0

            b_pvals.append(float(p_val))
            b_records.append({
                "budget": b,
                "step_transition": f"{c1} -> {c2}",
                "architectural_mechanism": desc,
                "mean_delta_pp": round(mean_diff * 100, 2),
                "ci_lower_pp": round((mean_diff - ci_margin) * 100, 2),
                "ci_upper_pp": round((mean_diff + ci_margin) * 100, 2),
                "effect_size_cohens_dz": round(dz, 4),
                "paired_t_stat": round(float(t_stat), 4),
                "raw_p_value": float(p_val)
            })

        holm_pvals = holm_bonferroni(b_pvals)
        for i, rec in enumerate(b_records):
            rec["holm_adjusted_p_value"] = holm_pvals[i]
            rec["is_significant_holm_05"] = (holm_pvals[i] < 0.05)
            stat_rows.append(rec)

    df_stat = pd.DataFrame(stat_rows)
    out_stat_csv = "research/final_statistical_table.csv"
    df_stat.to_csv(out_stat_csv, index=False)
    print(f"[DONE] Saved {out_stat_csv} ({len(df_stat)} rows).")

if __name__ == "__main__":
    main()

