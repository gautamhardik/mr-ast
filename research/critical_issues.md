# Critical Issues Report: MR-TopoS Independent Evidence Audit

**Audit Date**: November 5, 2026  
**Auditor**: Independent Adversarial Research Audit & Antigravity Autonomous Agent  
**Target Submission**: Google Gemma 4 Developer Agent Paper Track (Kaggle Competition ID: `163111`)

---

## Executive Summary of Audit Findings

An exhaustive, evidence-first audit was conducted on all codebase components, scripts, per-task benchmark CSVs, statistical computations, and manuscripts for MR-TopoS. While the core algorithm, multi-resolution model, Differential Typing Pruner, and 100% budget compliance against the official Gemma 4 tokenizer are verified and robust, the audit revealed **six critical issues** ranging from manuscript word count violations and synthetic runtime scaling claims to metric methodological flaws and statistical overreach.

---

## Detailed Critical Issues

### Issue 1: Manuscript Exceeds Competition Word Limit
- **Severity**: HIGH (Disqualification Risk)
- **Evidence**: `paper/final_draft.md`
- **Measured Word Count**:
  - Total Words: **4,467 words**
  - Prose Words: **3,486 words**
  - Body Words (excluding References): **4,242 words**
  - Body Prose Words (excluding References): **3,261 words**
- **Competition Rule**: Maximum 3,000 words.
- **Root Cause**: Extensive exposition, repetitive contributions, verbose figure descriptions, and expanded methodology text in `paper/final_draft.md`.
- **Required Action**: Author `paper/final_draft_revised.md` strictly capped at $\le 3,000$ total words while preserving all supported methodology, mathematics, and empirical evidence.

---

### Issue 2: Fabricated / Synthetic Solver Scaling Claims (Figure 3 & Section 5.3)
- **Severity**: HIGH (Scientific Integrity)
- **Evidence**: `scripts/generate_paper_figures.py` (lines 60–62), `paper/final_draft.md` (lines 254–257).
- **Audit Findings**:
  - `generate_paper_figures.py` plotted hardcoded constants:
    `milp_times = [1.8, 4.1, 7.2, 14.5, 31.0, 68.2]`
    `greedy_times = [2.5, 14.2, 38.6, 122.0, 315.0, 598.0]`
  - No experimental benchmark script or raw execution logs generated these numbers.
  - In the actual 129-task benchmark (`results/final_benchmark/aggregate.csv`), on standard candidate pools ($N \approx 60$), the constraint-aware greedy baseline was **faster** than HiGHS MILP for $B \le 8,000$:
    - $B=2,000$: Greedy = $15.13\text{ ms}$, MILP = $37.07\text{ ms}$ (Greedy is $2.4\times$ faster).
    - $B=4,000$: Greedy = $17.38\text{ ms}$, MILP = $31.71\text{ ms}$ (Greedy is $1.8\times$ faster).
    - $B=8,000$: Greedy = $19.70\text{ ms}$, MILP = $29.05\text{ ms}$ (Greedy is $1.5\times$ faster).
    - $B=16,000$: Greedy = $18.88\text{ ms}$, MILP = $13.99\text{ ms}$ (MILP is $1.35\times$ faster).
- **Required Action**: Withdraw the claims of "$3.5\times$ and $8.8\times$ runtime advantage". Accurately report that HiGHS MILP solves within $14–37\text{ ms}$ per task, and justify HiGHS on **provable mathematical global optimality** and **zero precedence violations**, not on raw speed over greedy heuristics. Update Figure 3 or replace it with an empirical solver distribution.

---

### Issue 3: "Scope Tax" 28.9% Drop Origin Mismatch
- **Severity**: MEDIUM (Empirical Precision)
- **Evidence**: `results/phase3/structural_baseline_comparison.csv` vs `results/final_benchmark/aggregate.csv`.
- **Audit Findings**:
  - The claim that wrapping methods in class stubs causes a "28.9% drop in retained symbols (from 22.8 to 16.2 symbols)" originated in the 9-task pilot study from Phase 3 (`results/phase3/structural_baseline_comparison.csv`: raw = $22.78$, scoped = $16.22$, $(22.78-16.22)/22.78 = 28.8\%$).
  - In the full 129-task benchmark (`results/final_benchmark/aggregate.csv`), at $B=2,000$:
    - `bm25_raw` mean symbols = **12.51**
    - `bm25_scoped` mean symbols = **12.55** (negligible difference in symbol count, $+0.3\%$).
  - However, MR-TopoS retained **50.85 symbols** at $B=2,000$, which is **$4.05\times$ more symbols** than scoped BM25 ($12.55$).
- **Required Action**: Clearly attribute the 28.9% symbol penalty to the Phase 3 pilot evaluation, and report the true 129-task aggregate behavior: while raw and scoped BM25 both saturate at ~12.5 symbols, MR-TopoS dramatically expands symbol capacity to 50.85 symbols ($4.05\times$ advantage) through multi-resolution stubbing.

---

### Issue 4: Methodological Flaw in Hit@K Evaluation
- **Severity**: HIGH (Metric Validity)
- **Evidence**: `scripts/run_final_benchmark.py` (lines 310–313).
- **Audit Findings**:
  - The script computed Hit@1, Hit@5, Hit@10 by slicing an unordered Python set:
    ```python
    selected_files_list = list(selected_files)
    hit_1 = 1 if any(f in gold_set for f in selected_files_list[:1]) else 0
    ```
  - Because `selected_files` is a `set()`, its iteration order is arbitrary (dict hash-dependent).
  - In MR-TopoS, where 10–20 files contribute symbols to the context, slicing the arbitrary set resulted in an artificially low Hit@1 ($0.0078$, $<1\%$).
  - Conversely, the previous summary report reported fabricated Hit@1 numbers ($17.83\%$ and $23.26\%$) copied from historical phase files.
- **Required Action**: Document this metric flaw transparently. Explain why Hit@K computed over an unordered set of compiled files is unranked. Rely primarily on **Mean Gold File Recall**, which is set-based, robust, and unaffected by iteration order.

---

### Issue 5: Statistical Significance Overreach
- **Severity**: MEDIUM (Statistical Soundness)
- **Evidence**: `results/statistics/paired_comparisons.csv`, `results/audit_summary.json`.
- **Audit Findings**:
  - The claim that "all paired differences across all budgets are statistically significant ($t(128) = 6.42, p < 10^{-4}$)" is incorrect.
  - Actual paired t-test results between MR-TopoS MILP and Scoped BM25 on Gold File Recall:
    - $B=2,000$: Mean diff = $+0.1118$ ($+29.98\%$), $t(128) = 2.57$, $p = 0.0112$ (**Significant, $p < 0.05$**).
    - $B=4,000$: Mean diff = $+0.1126$ ($+26.30\%$), $t(128) = 3.66$, $p = 0.00037$ (**Significant, $p < 0.001$**).
    - $B=8,000$: Mean diff = $-0.0035$ ($-0.6\%$), $t(128) = -0.18$, $p = 0.8562$ (**Not Significant**).
    - $B=16,000$: Mean diff = $-0.0255$ ($-4.3\%$), $t(128) = -1.35$, $p = 0.1790$ (**Not Significant**).
- **Required Action**: Retract the universal significance claim. State clearly that MR-TopoS provides a statistically significant recall advantage in **constrained budget regimes ($B \le 4,000$ tokens)**. Under generous budgets ($B \ge 8,000$), whole-method lexical retrieval achieves equivalent file coverage because context saturation is no longer binding.

---

### Issue 6: Gemma 4 Repair Inference Was NOT EXECUTED
- **Severity**: HIGH (Factuality)
- **Evidence**: `results/gemma_repair/aggregate.csv`, `results/gemma_repair/per_task.csv`.
- **Audit Findings**:
  - Every row in `results/gemma_repair/per_task.csv` records:
    `model_execution_status: HARDWARE_CONSTRAINED_NO_L4_GPU`
    `model_execution_note: Gemma 4 31B W4A16 requires 4x NVIDIA L4 GPUs running vLLM; host has 0 CUDA GPUs`
  - While test patch application and gold patch application were successfully verified on disk (`TEST_PATCH_APPLIED`, `GOLD_PATCH_APPLIED`), zero LLM inference was executed.
- **Required Action**: Explicitly classify Gemma 4 repair inference as **NOT EXECUTED**. Do not claim or imply any downstream repair pass rate in the paper. Present the work strictly as context compilation and structural retrieval, providing `experiments/gemma_repair/` as a verified reproduction harness for cloud evaluation.

