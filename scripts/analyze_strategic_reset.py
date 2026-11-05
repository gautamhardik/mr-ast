"""
Comprehensive Statistical Analysis for Strategic Reset Experiment Suite.

Analyzes:
1. Factorial Ablation (A -> B -> C -> D -> E -> F) with paired differences, 95% CIs, and p-values.
2. Candidate Pool Saturation (K in {60, 100, 200, 400}) across all budgets.
3. Authentic Aider RepoMap vs MR-TopoS vs Scoped BM25 head-to-head comparison.
4. Syntactic validity and budget compliance verification.

Outputs markdown report and JSON summary:
- results/strategic_reset/statistical_analysis_report.md
- results/strategic_reset/statistical_analysis_summary.json
"""

import json
import math
import os
import sys
import pandas as pd
import numpy as np
from scipy import stats

def compute_paired_stats(series_a: pd.Series, series_b: pd.Series):
    """Computes mean difference, std of diff, 95% CI, and paired t-test p-value."""
    diff = series_b - series_a
    n = len(diff)
    if n == 0:
        return {"mean_diff": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "p_value": 1.0}
    mean_diff = float(diff.mean())
    std_diff = float(diff.std(ddof=1)) if n > 1 else 0.0
    sem = std_diff / math.sqrt(n) if n > 1 else 0.0
    ci_margin = stats.t.ppf(0.975, df=n-1) * sem if n > 1 and sem > 0 else 0.0
    
    # Paired t-test
    if std_diff > 1e-9:
        t_stat, p_val = stats.ttest_rel(series_b, series_a)
    else:
        t_stat, p_val = 0.0, 1.0
        
    return {
        "n": n,
        "mean_diff": round(mean_diff, 4),
        "ci_lower": round(mean_diff - ci_margin, 4),
        "ci_upper": round(mean_diff + ci_margin, 4),
        "p_value": float(p_val)
    }

def main():
    csv_path = "results/strategic_reset/experiment_ledger.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist yet.")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded experiment ledger: {len(df)} rows across {df['task_id'].nunique()} tasks.")

    budgets = sorted(df["budget"].unique())
    tasks = df["task_id"].unique()
    n_tasks = len(tasks)

    report_lines = []
    report_lines.append("# MR-TopoS: Strategic Reset Definitive Statistical Analysis")
    report_lines.append(f"\n**Total Tasks Analyzed:** {n_tasks}")
    report_lines.append(f"**Budgets Evaluated:** {budgets}")
    report_lines.append(f"**Total Executed Ledger Records:** {len(df)}\n")

    summary_data = {
        "total_tasks": n_tasks,
        "budgets": budgets,
        "ablation_table": {},
        "paired_deltas": {},
        "saturation_study": {},
        "aider_comparison": {}
    }

    # =========================================================================
    # 1. FACTORIAL ABLATION ANALYSIS
    # =========================================================================
    report_lines.append("## 1. Factorial Ablation Analysis (Conditions A-F)")
    report_lines.append("A: Scoped BM25 (Baseline)")
    report_lines.append("B: Multi-Resolution Only (No Containment, No Topo)")
    report_lines.append("C: MR + AST Containment (No Topo)")
    report_lines.append("D: MR + AST Containment + Dependency (Full PC-MCKP)")
    report_lines.append("E: Constraint-Aware Greedy Heuristic")
    report_lines.append("F: Exact MILP Context Compiler (MR-TopoS Final)\n")

    # Table of Means
    report_lines.append("### Mean Performance by Condition and Budget")
    report_lines.append("| Budget | Condition | Recall (All) | Recall (Pre-exist) | Retained Symbols | Full | Skel | Stub | Syntax Valid % | Solve Time (ms) |")
    report_lines.append("|---|---|---|---|---|---|---|---|---|---|")

    conds = ["A_scoped_bm25", "B_mr_only", "C_mr_containment", "D_mr_containment_dep", "E_mrtopos_con_greedy", "F_mrtopos_milp"]

    ablation_df = df[df["condition"].isin(conds)]

    for b in budgets:
        summary_data["ablation_table"][str(b)] = {}
        for c in conds:
            sub = ablation_df[(ablation_df["budget"] == b) & (ablation_df["condition"] == c)]
            r_all = sub["gold_recall_all"].mean()
            r_pre = sub["gold_recall_pre_existing"].dropna().mean()
            syms = sub["retained_symbols_count"].mean()
            full_s = sub["retained_full"].mean()
            skel_s = sub["retained_skel"].mean()
            stub_s = sub["retained_stub"].mean()
            syn = sub["syntactic_validity"].mean() * 100
            t_ms = sub["solve_time_ms"].mean()

            summary_data["ablation_table"][str(b)][c] = {
                "recall_all": round(r_all, 4),
                "recall_pre": round(r_pre, 4) if not np.isnan(r_pre) else None,
                "retained_symbols": round(syms, 1),
                "retained_full": round(full_s, 1),
                "retained_skel": round(skel_s, 1),
                "retained_stub": round(stub_s, 1),
                "syntax_pct": round(syn, 1),
                "solve_time_ms": round(t_ms, 2)
            }

            report_lines.append(
                f"| {b} | `{c}` | {r_all*100:.2f}% | {r_pre*100:.2f}% | {syms:.1f} | {full_s:.1f} | {skel_s:.1f} | {stub_s:.1f} | {syn:.1f}% | {t_ms:.2f}ms |"
            )

    # Paired Step-by-Step Deltas
    report_lines.append("\n### Paired Marginal Contributions (Step-by-Step)")
    report_lines.append("| Budget | Transition | Marginal Mechanism | Mean Recall Delta | 95% Confidence Interval | p-value | Significance |")
    report_lines.append("|---|---|---|---|---|---|---|")

    transitions = [
        ("A_scoped_bm25", "B_mr_only", "A -> B: Multi-Resolution Representation"),
        ("B_mr_only", "C_mr_containment", "B -> C: AST Precedence / Containment"),
        ("C_mr_containment", "D_mr_containment_dep", "C -> D: Topological Dependency Scoring"),
        ("D_mr_containment_dep", "E_mrtopos_con_greedy", "D -> E: Greedy Context Packing"),
        ("E_mrtopos_con_greedy", "F_mrtopos_milp", "E -> F: Exact MILP vs Greedy"),
        ("A_scoped_bm25", "F_mrtopos_milp", "A -> F: Total Net MR-TopoS Gain")
    ]

    for b in budgets:
        summary_data["paired_deltas"][str(b)] = {}
        for c1, c2, desc in transitions:
            sub1 = ablation_df[(ablation_df["budget"] == b) & (ablation_df["condition"] == c1)].sort_values("task_id")
            sub2 = ablation_df[(ablation_df["budget"] == b) & (ablation_df["condition"] == c2)].sort_values("task_id")
            
            p_stats = compute_paired_stats(sub1["gold_recall_all"].reset_index(drop=True), 
                                           sub2["gold_recall_all"].reset_index(drop=True))
            
            summary_data["paired_deltas"][str(b)][desc] = p_stats
            sig_str = "***" if p_stats["p_value"] < 0.001 else ("**" if p_stats["p_value"] < 0.01 else ("*" if p_stats["p_value"] < 0.05 else "n.s."))
            p_val_fmt = f"{p_stats['p_value']:.4e}" if p_stats["p_value"] < 0.0001 else f"{p_stats['p_value']:.4f}"
            
            report_lines.append(
                f"| {b} | `{c1}` &rarr; `{c2}` | {desc} | {p_stats['mean_diff']*100:+.2f}% | [{p_stats['ci_lower']*100:+.2f}%, {p_stats['ci_upper']*100:+.2f}%] | {p_val_fmt} | {sig_str} |"
            )

    # =========================================================================
    # 2. CANDIDATE POOL SATURATION STUDY (K = 60, 100, 200, 400)
    # =========================================================================
    report_lines.append("\n## 2. Candidate Pool Saturation Analysis (K in {60, 100, 200, 400})")
    report_lines.append("| Budget | Pool Size K | Recall (All) | Recall (Pre-exist) | Retained Symbols | Solve Time (ms) |")
    report_lines.append("|---|---|---|---|---|---|")

    # Gather K=60 from Condition F, and K=100, 200, 400 from saturation group
    for b in budgets:
        summary_data["saturation_study"][str(b)] = {}
        for k_val in [60, 100, 200, 400]:
            if k_val == 60:
                sub = df[(df["budget"] == b) & (df["condition"] == "F_mrtopos_milp")]
            else:
                sub = df[(df["budget"] == b) & (df["condition"] == f"saturation_K{k_val}")]
            
            r_all = sub["gold_recall_all"].mean()
            r_pre = sub["gold_recall_pre_existing"].dropna().mean()
            syms = sub["retained_symbols_count"].mean()
            t_ms = sub["solve_time_ms"].mean()

            summary_data["saturation_study"][str(b)][f"K_{k_val}"] = {
                "recall_all": round(r_all, 4),
                "recall_pre": round(r_pre, 4) if not np.isnan(r_pre) else None,
                "retained_symbols": round(syms, 1),
                "solve_time_ms": round(t_ms, 2)
            }

            report_lines.append(
                f"| {b} | K = {k_val:3d} | {r_all*100:.2f}% | {r_pre*100:.2f}% | {syms:.1f} | {t_ms:.2f}ms |"
            )

    # Paired Saturation Deltas: Does scaling K increase recall at 8k/16k?
    report_lines.append("\n### Paired Candidate Pool Scaling (K=60 -> K=400)")
    report_lines.append("| Budget | Transition | Mean Recall Delta | 95% Confidence Interval | p-value | Significance |")
    report_lines.append("|---|---|---|---|---|---|")

    summary_data["saturation_paired"] = {}
    for b in budgets:
        summary_data["saturation_paired"][str(b)] = {}
        sub_k60 = df[(df["budget"] == b) & (df["condition"] == "F_mrtopos_milp")].sort_values("task_id")
        for k_val in [100, 200, 400]:
            sub_k = df[(df["budget"] == b) & (df["condition"] == f"saturation_K{k_val}")].sort_values("task_id")
            p_stats = compute_paired_stats(sub_k60["gold_recall_all"].reset_index(drop=True),
                                           sub_k["gold_recall_all"].reset_index(drop=True))
            summary_data["saturation_paired"][str(b)][f"K60_to_K{k_val}"] = p_stats
            sig_str = "***" if p_stats["p_value"] < 0.001 else ("**" if p_stats["p_value"] < 0.01 else ("*" if p_stats["p_value"] < 0.05 else "n.s."))
            p_val_fmt = f"{p_stats['p_value']:.4e}" if p_stats["p_value"] < 0.0001 else f"{p_stats['p_value']:.4f}"
            report_lines.append(
                f"| {b} | K=60 &rarr; K={k_val} | {p_stats['mean_diff']*100:+.2f}% | [{p_stats['ci_lower']*100:+.2f}%, {p_stats['ci_upper']*100:+.2f}%] | {p_val_fmt} | {sig_str} |"
            )


    # =========================================================================
    # 3. AUTHENTIC AIDER REPOMAP BASELINE COMPARISON
    # =========================================================================
    report_lines.append("\n## 3. Authentic Aider RepoMap Baseline Comparison")
    report_lines.append("| Budget | Method | Recall (All) | Recall (Pre-exist) | Retained Symbols | Syntax Valid % | Solve Time (ms) | Compliant % |")
    report_lines.append("|---|---|---|---|---|---|---|---|")

    for b in budgets:
        summary_data["aider_comparison"][str(b)] = {}
        for m_name, c_name in [("Scoped BM25", "A_scoped_bm25"), 
                               ("Aider RepoMap", "aider_repomap"), 
                               ("MR-TopoS (MILP)", "F_mrtopos_milp")]:
            sub = df[(df["budget"] == b) & (df["condition"] == c_name)]
            r_all = sub["gold_recall_all"].mean()
            r_pre = sub["gold_recall_pre_existing"].dropna().mean()
            syms = sub["retained_symbols_count"].mean()
            syn = sub["syntactic_validity"].mean() * 100
            t_ms = sub["solve_time_ms"].mean()
            comp = sub["is_budget_compliant"].mean() * 100

            summary_data["aider_comparison"][str(b)][m_name] = {
                "recall_all": round(r_all, 4),
                "recall_pre": round(r_pre, 4) if not np.isnan(r_pre) else None,
                "retained_symbols": round(syms, 1),
                "syntax_pct": round(syn, 1),
                "solve_time_ms": round(t_ms, 2),
                "compliant_pct": round(comp, 1)
            }

            report_lines.append(
                f"| {b} | {m_name} | {r_all*100:.2f}% | {r_pre*100:.2f}% | {syms:.1f} | {syn:.1f}% | {t_ms:.2f}ms | {comp:.1f}% |"
            )

    # Paired t-test between MR-TopoS and Aider
    report_lines.append("\n### Paired Head-to-Head: MR-TopoS vs Aider RepoMap")
    report_lines.append("| Budget | MR-TopoS Mean Recall | Aider Mean Recall | Mean Difference | 95% CI | p-value | Verdict |")
    report_lines.append("|---|---|---|---|---|---|---|")

    for b in budgets:
        sub_mr = df[(df["budget"] == b) & (df["condition"] == "F_mrtopos_milp")].sort_values("task_id")
        sub_ai = df[(df["budget"] == b) & (df["condition"] == "aider_repomap")].sort_values("task_id")
        p_stats = compute_paired_stats(sub_ai["gold_recall_all"].reset_index(drop=True),
                                       sub_mr["gold_recall_all"].reset_index(drop=True))
        
        sig = "Advantage (p < 0.05)" if p_stats["p_value"] < 0.05 and p_stats["mean_diff"] > 0 else (
            "Parity (p >= 0.05)" if p_stats["p_value"] >= 0.05 else "Disadvantage (p < 0.05)"
        )
        report_lines.append(
            f"| {b} | {sub_mr['gold_recall_all'].mean()*100:.2f}% | {sub_ai['gold_recall_all'].mean()*100:.2f}% | {p_stats['mean_diff']*100:+.2f}% | [{p_stats['ci_lower']*100:+.2f}%, {p_stats['ci_upper']*100:+.2f}%] | {p_stats['p_value']:.4f} | {sig} |"
        )

    # Write Markdown Report
    out_md = "results/strategic_reset/statistical_analysis_report.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"[DONE] Wrote statistical analysis report to {out_md}")

    # Write JSON Summary
    def json_serialize_helper(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    out_json = "results/strategic_reset/statistical_analysis_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, default=json_serialize_helper)
    print(f"[DONE] Wrote summary data to {out_json}")

if __name__ == "__main__":
    main()
