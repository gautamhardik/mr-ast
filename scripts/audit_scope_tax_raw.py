"""
Deep Falsification Audit of the Scope Tax.
Analyzes:
1. Exact task-level symbol counts: raw vs scoped across all 129 tasks and 4 budgets.
2. Parent class wrapper token overhead: how many tokens does 'class P:\n' actually add per method?
3. Frequency of parent class duplication vs deduplication.
4. Total scope overhead as % of context budget.
5. Direct comparison to the 9-task pilot.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from transformers import AutoTokenizer

sys.path.insert(0, os.path.abspath("."))

def audit_scope_tax():
    df = pd.read_csv("results/final_benchmark/per_task.csv")
    tok = AutoTokenizer.from_pretrained("models/gemma4_tokenizer", local_files_only=True)
    
    results = {}
    
    for b in [2000, 4000, 8000, 16000]:
        df_b = df[df["budget"] == b]
        raw = df_b[df_b["method"] == "bm25_raw"].set_index("task_id")
        scoped = df_b[df_b["method"] == "bm25_scoped"].set_index("task_id")
        
        common = raw.index.intersection(scoped.index)
        
        raw_syms = raw.loc[common, "retained_symbols_count"]
        scoped_syms = scoped.loc[common, "retained_symbols_count"]
        
        diff = raw_syms - scoped_syms # positive means raw retained more
        
        # Percent difference in means
        mean_raw = raw_syms.mean()
        mean_scoped = scoped_syms.mean()
        pct_diff = (mean_raw - mean_scoped) / mean_raw * 100 if mean_raw > 0 else 0
        
        # Distribution of diffs
        raw_gt_scoped = int((diff > 0).sum())
        raw_eq_scoped = int((diff == 0).sum())
        raw_lt_scoped = int((diff < 0).sum())
        
        results[b] = {
            "mean_raw_symbols": round(float(mean_raw), 3),
            "mean_scoped_symbols": round(float(mean_scoped), 3),
            "mean_difference": round(float(diff.mean()), 3),
            "percent_difference": round(float(pct_diff), 3),
            "tasks_raw_gt_scoped": raw_gt_scoped,
            "tasks_raw_eq_scoped": raw_eq_scoped,
            "tasks_raw_lt_scoped": raw_lt_scoped,
            "max_symbol_loss": int(diff.max()),
            "min_symbol_loss": int(diff.min()),
            "p25_diff": float(np.percentile(diff, 25)),
            "p50_diff": float(np.percentile(diff, 50)),
            "p75_diff": float(np.percentile(diff, 75))
        }
        
    # Analyze actual token overhead of 'class Parent:\n    '
    sample_classes = ["Request", "Response", "APIRoute", "Console", "Text", "ProgressBar", "Session", "HTTPConnection"]
    overhead_tokens = [len(tok.encode(f"class {c}:\n    ", add_special_tokens=False)) for c in sample_classes]
    
    results["token_overhead_analysis"] = {
        "sample_class_headers": sample_classes,
        "overhead_tokens_per_class": overhead_tokens,
        "mean_overhead_tokens": float(np.mean(overhead_tokens)),
        "min_overhead_tokens": int(np.min(overhead_tokens)),
        "max_overhead_tokens": int(np.max(overhead_tokens))
    }
    
    # Check 9-task pilot comparison
    pilot_csv = "results/phase3/structural_baseline_comparison.csv"
    if os.path.exists(pilot_csv):
        pilot_df = pd.read_csv(pilot_csv)
        p2k = pilot_df[pilot_df["budget"] == 2000]
        p_raw = p2k[p2k["method"] == "raw_bm25"]["retained_symbols_count"].mean()
        p_scoped = p2k[p2k["method"] == "scoped_bm25"]["retained_symbols_count"].mean()
        results["pilot_9task_comparison"] = {
            "pilot_raw_symbols": round(float(p_raw), 2),
            "pilot_scoped_symbols": round(float(p_scoped), 2),
            "pilot_pct_loss": round(float((p_raw - p_scoped) / p_raw * 100), 2)
        }
        
    out_file = "results/scope_tax_falsification.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Scope tax falsification analysis written to {out_file}")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    audit_scope_tax()

