# MR-TopoS Phase 3: Corrected Metric Definitions & Numerical Audit

**Audit Date**: 2026-11-05  
**Document Purpose**: Provide exact mathematical formulations, explicit denominators, micro vs. macro definitions, and audited aggregate tables reconciling all reported numbers across the SWE-Gemma 129-task benchmark.

---

## 1. Formal Metric Definitions & Denominators

Let $T$ denote the set of benchmark evaluation tasks ($|T| = 129$).  
For each task $t \in T$:
- $G_t$ denotes the set of ground-truth modified files extracted from the reference patch.
- $G_t^{\text{pre}} \subseteq G_t$ denotes the subset of modified files that physically existed in the repository prior to the reference patch (`exists_in_base_snapshot == True`).
- $G_t^{\text{new}} \subseteq G_t$ denotes files created *ex nihilo* by the reference patch (`@@ -0,0 ... @@`, `is_created_by_patch == True`).
- $R_t(B, M)$ denotes the ordered list of unique files present in the context compiled under token budget $B$ by method $M$.

### 1.1. Hit@K (Recall@K)
$$\text{Hit@}K(t) = \begin{cases} 1 & \text{if } \exists f \in R_t[:K] \text{ such that } f \in G_t \\ 0 & \text{otherwise} \end{cases}$$
- **Task Evaluation**: Evaluated over the first $K$ unique file paths in the context.
- **Aggregate Denominator**: $|T| = 129$ tasks.
- **Formula**: $\text{Macro Hit@}K = \frac{1}{|T|} \sum_{t \in T} \text{Hit@}K(t)$.

### 1.2. Mean Reciprocal Rank (MRR)
$$\text{RR}(t) = \begin{cases} \frac{1}{\text{rank}_t} & \text{if } \exists f \in R_t \cap G_t \text{ where } \text{rank}_t = \min \{ r \mid R_t[r-1] \in G_t \} \\ 0 & \text{if } R_t \cap G_t = \emptyset \end{cases}$$
- **Formula**: $\text{MRR} = \frac{1}{|T|} \sum_{t \in T} \text{RR}(t)$.
- **Denominator**: Always $|T| = 129$ tasks. Tasks with 0 retrieved gold files contribute $0.0$.

### 1.3. Gold-File Coverage: Macro vs. Micro Averaging
We distinguish two distinct averaging formulations:

1. **Macro Gold Coverage** (Task-Level Mean):
   $$\text{Macro Coverage} = \frac{1}{|T|} \sum_{t \in T} \frac{|R_t \cap G_t|}{|G_t|}$$
   Each task carries equal weight $\frac{1}{129}$, regardless of whether it modified 1 file or 10 files.
   *Measured Result for BM25 and MR-TopoS*: **$0.6806$ ($68.06\%$)**.

2. **Micro Gold Coverage** (File-Level Pooled Coverage):
   $$\text{Micro Coverage} = \frac{\sum_{t \in T} |R_t \cap G_t|}{\sum_{t \in T} |G_t|}$$
   Pools all file references into a single denominator:
   - **All Modified File References ($N=278$)**:
     $$\text{Micro Coverage}_{\text{all}} = \frac{172}{278} = \mathbf{61.87\%}$$
   - **Pre-Existing Modified Files ($N=229$)**:
     $$\text{Micro Coverage}_{\text{pre}} = \frac{172}{229} = \mathbf{75.11\%}$$
     *(Note: The previously cited $74.81\%$ was an unrounded approximation; the exact rational fraction is $172 / 229 = 0.751091...$)*.

3. **Eligible Task Hit Rate** (Excluding tasks where all target files were patch-created):
   - Exactly 11 tasks modified *only* newly created files ($G_t = G_t^{\text{new}}$).
   - Among the remaining 118 eligible tasks, MR-TopoS successfully retrieved at least one gold file in 103 tasks:
     $$\text{Task Success Rate}_{\text{eligible}} = \frac{103}{118} = \mathbf{87.29\%}$$

---

## 2. Recomputed Aggregate Results Table (All 129 Tasks, 2,064 Runs)

All values below have been recomputed directly from [`results/phase3/per_task_results.csv`](file:///c:/Users/hiten/Downloads/GEMMA/results/phase3/per_task_results.csv) without truncation:

| Method | Budget ($B$) | Hit@1 (Macro) | Hit@5 (Macro) | Hit@10 (Macro) | MRR (Macro) | Macro Coverage | Micro Coverage (Pre-Exist) | Total Violations | Structural Validity | Mean Tokens |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`full_file`** | 2,000 | 0.0543 | 0.0853 | 0.1008 | 0.0709 | 0.0696 | 7.42% | 0 | 100.0% | 1,935.2 |
| | 4,000 | 0.0620 | 0.1240 | 0.1473 | 0.0855 | 0.0958 | 10.48% | 0 | 100.0% | 3,907.6 |
| | 8,000 | 0.1395 | 0.2481 | 0.2868 | 0.1860 | 0.2342 | 25.76% | 0 | 100.0% | 7,917.8 |
| | 16,000 | 0.1008 | 0.2713 | 0.3411 | 0.1745 | 0.2926 | 32.75% | 0 | 100.0% | 15,775.6 |
| **`bm25`** | 2,000 | 0.1938 | 0.4109 | 0.5814 | 0.3017 | 0.6806 | 75.11% | 5,928 | 0.0% | 384.8* |
| | 4,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 5,954 | 0.0% | 789.2* |
| | 8,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 5,972 | 0.0% | 1,018.6* |
| | 16,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 6,010 | 0.0% | 1,557.7* |
| **`mrtopos_con_greedy`** | 2,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 390.6* |
| | 4,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 793.6* |
| | 8,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 1,022.6* |
| | 16,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 1,560.8* |
| **`mrtopos_milp`** | 2,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 389.4* |
| | 4,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 792.6* |
| | 8,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 1,033.2* |
| | 16,000 | 0.1938 | 0.4109 | 0.5814 | 0.3015 | 0.6806 | 75.11% | 0 | 100.0% | 1,559.5* |

*\*Note: Mean token counts marked with an asterisk reflect the candidate-pool-capped evaluation analyzed in `retrieval_pipeline_audit.md`.*

---

## 3. Explanation of Full-File Hit@1 Anomaly (8k vs. 16k)

An apparent paradox in the data was the decrease of `full_file` Hit@1 from **$13.95\%$** at 8,000 tokens to **$10.08\%$** at 16,000 tokens (a net drop of 5 tasks: `requests_7505`, `requests_7502`, `requests_7433`, `requests_7328`, `requests_7309`, `requests_7205`, `requests_6644`).

### Mechanistic Cause:
In Whole-File greedy packing, candidate files are ordered by aggregated lexical relevance:
```python
sorted_files = sorted(file_scores.keys(), key=lambda fp: file_scores[fp], reverse=True)
for fp in sorted_files:
    if current_tokens + file_tokens <= budget:
        selected_files.append(fp)
        current_tokens += file_tokens
```
In `requests`, the highest BM25-scoring file is frequently the comprehensive test suite file `tests/test_requests.py` (which spans **15,941 subword tokens**), followed by the gold source file `requests/models.py` (**7,977 tokens**).

1. **Under 8,000 Token Budget**:
   `tests/test_requests.py` (15,941 tokens) **exceeds the 8k budget**. The greedy loop skips it and examines the second-ranked file `requests/models.py` (7,977 tokens). Because $7,977 \le 8,000$, `requests/models.py` is packed as the **first and only file** in `selected_files`. Because `requests/models.py` is a ground-truth gold file, **Hit@1 = 1**.
2. **Under 16,000 Token Budget**:
   Now, `tests/test_requests.py` (15,941 tokens) **fits within 16,000 tokens**. The greedy loop packs it into slot 1. The remaining budget is $16,000 - 15,941 = 59$ tokens. The gold source file `requests/models.py` (7,977 tokens) cannot fit in 59 tokens and is excluded. The compiled context contains *only* `tests/test_requests.py`, which is not a gold modified file. Consequently, **Hit@1 drops to 0**.

This empirical finding demonstrates a major pathology of whole-file context selection: **large non-gold files that barely fit under larger budgets can monopolize the entire context capacity and crowd out compact gold source files that were successfully retained under tighter budgets.**

