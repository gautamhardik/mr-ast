# Benchmark Localization Recall Denominator Reconciliation

**Project**: MR-TopoS (Multi-Resolution Dual-View Program Topology Context Induction)  
**Author**: Independent Principal Research Scientist  
**Date**: November 5, 2026  
**Status**: Exhaustively Recomputed from Raw Benchmark Data  

---

## 1. Executive Summary & Root-Cause Analysis

In previous drafts and audit summaries, an egregious reporting defect occurred regarding ground-truth localization metrics:
- The manuscript cited **0.4846** (MR-TopoS) and **0.3728** (Scoped BM25) at $B=2,000$ as "pre-existing gold recall".
- In an intermediate audit document (`benchmark_reconciliation.md`), the values **0.5883** and **0.4526** were reported as "achievable pre-existing gold recall".

### Forensic Reconciliation:
1. **The 0.4846 and 0.3728 Metrics**: These represent the **Macro Recall across ALL 278 modified-file references** across all 129 SWE-bench Lite tasks, which includes 49 files newly created by the bug-fix patches.
2. **The 0.5883 and 0.4526 Artifact**: An intermediate report erroneously estimated pre-existing recall by multiplying the overall macro recall by the scalar ratio of denominators:
   $$0.4846 \times \frac{278}{229} = 0.5883, \quad 0.3728 \times \frac{278}{229} = 0.4526$$
   This scalar multiplication is statistically invalid: it assumed that gold hits were uniformly distributed and that no patch-created files affected individual task denominators.
3. **The True Ground-Truth Recomputation**: Performing an exact task-by-task recomputation from `results/final_benchmark/per_task.csv` reveals the true Macro Recall on pre-existing files is **0.5087** for MR-TopoS vs. **0.3885** for Scoped BM25 ($+30.95\%$ relative advantage).

This document establishes the authoritative, mathematically rigorous ledger of all localization metrics.

---

## 2. Benchmark Corpus Denominators

Across the 129 SWE-bench Lite tasks (spanning `fastapi`, `rich`, `requests`, and `httpx`), unified git diffs modify **278 file references**:

| Category | Reference Count | Percentage of References | Unique File Paths | Description |
|---|:---:|:---:|:---:|---|
| **Pre-Existing Files ($\mathcal{F}_{\text{pre}}$)** | **229** | $82.4\%$ | 68 | Present in base repository snapshots prior to patch application. Indexable by AST parsers. |
| **Patch-Created Files ($\mathcal{F}_{\text{new}}$)** | **49** | $17.6\%$ | 45 | Newly created by the bug-fix PR (e.g., new test modules). Not present in snapshot. |
| **Total Modified References ($\mathcal{F}_{\text{all}}$)** | **278** | $100.0\%$ | 113 | Sum of all modified-file references across all 129 tasks. |

### Task Distribution by Target Type:
- **Pre-Existing Only (118 tasks)**: Every modified file in the patch already existed in the base snapshot.
- **Mixed Tasks (10 tasks)**: Patch modified at least one pre-existing file and created at least one new file (e.g., modified `fastapi/routing.py` and created `tests/test_issue_1234.py`).
- **Patch-Created Only (1 task)**: `fastapi_15661` modified ONLY a newly created test file (`tests/test_tutorial/test_sql_databases/test_tutorial002.py`). For this task, $|\mathcal{F}_{\text{pre}}| = 0$.

---

## 3. Metric Definitions & Zero-Denominator Conventions

Let $\mathcal{F}_{\text{selected}, t}$ denote the set of source files included in the compiled context for task $t$, and $\mathcal{F}_{\text{gold}, t}$ denote the ground-truth modified files.

### 3.1 Macro Recall
The unweighted arithmetic mean of task-level recall scores across all $T$ tasks:
$$\text{MacroRecall} = \frac{1}{T} \sum_{t=1}^T \text{Recall}_t, \quad \text{where } \text{Recall}_t = \frac{|\mathcal{F}_{\text{selected}, t} \cap \mathcal{F}_{\text{target}, t}|}{|\mathcal{F}_{\text{target}, t}|}$$

### 3.2 Micro Recall
The aggregate recall computed across all benchmark file references globally:
$$\text{MicroRecall} = \frac{\sum_{t=1}^T |\mathcal{F}_{\text{selected}, t} \cap \mathcal{F}_{\text{target}, t}|}{\sum_{t=1}^T |\mathcal{F}_{\text{target}, t}|}$$

### 3.3 Task-Level Zero-Denominator Handling for $\mathcal{F}_{\text{pre}}$
For task `fastapi_15661`, $|\mathcal{F}_{\text{pre}}| = 0$. We evaluate two formal conventions:
1. **Convention A (Conditioned on Pre-Existing Target, $N=128$ tasks)**: Exclude tasks where no pre-existing target file exists ($|\mathcal{F}_{\text{pre}}| = 0$). This evaluates retrieval capability strictly when a retrievable target exists.
2. **Convention B (Zero-Penalty Macro, $N=129$ tasks)**: Define $\text{Recall}_t = 0.0$ when $|\mathcal{F}_{\text{pre}}| = 0$.

---

## 4. Comprehensive Empirical Results Across All Budgets

The following table presents the audited results recomputed directly from the 2,580 evaluations in `results/final_benchmark/per_task.csv`:

| Budget ($B$) | Method | Macro Recall All ($N=129$, $278$ refs) | Micro Recall All ($N=278$ refs) | Macro Recall Pre Conv A ($N=128$) | Macro Recall Pre Conv B ($N=129$) | Micro Recall Pre ($N=229$ refs) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **$B = 2,000$** | **full_file** | 0.1262 | 0.0863 | 0.1315 | 0.1305 | 0.1048 |
| | **bm25_raw** | 0.3515 | 0.2446 | 0.3663 | 0.3635 | 0.2969 |
| | **bm25_scoped** | 0.3728 | 0.2554 | 0.3885 | 0.3854 | 0.3100 |
| | **mrtopos_con_greedy** | 0.4730 | 0.3777 | 0.4970 | 0.4931 | 0.4585 |
| | **mrtopos_milp** | **0.4846** | **0.3849** | **0.5087** | **0.5047** | **0.4672** |
| | *Relative Adv (MILP vs Scoped)* | *+29.98%* | *+50.70%* | *+30.95%* | *+30.95%* | *+50.71%* |
| **$B = 4,000$** | **full_file** | 0.1287 | 0.0971 | 0.1341 | 0.1331 | 0.1179 |
| | **bm25_raw** | 0.4379 | 0.3237 | 0.4564 | 0.4528 | 0.3930 |
| | **bm25_scoped** | 0.4282 | 0.3237 | 0.4463 | 0.4428 | 0.3930 |
| | **mrtopos_con_greedy** | 0.4939 | 0.3921 | 0.5204 | 0.5164 | 0.4760 |
| | **mrtopos_milp** | **0.5408** | **0.4173** | **0.5677** | **0.5633** | **0.5066** |
| | *Relative Adv (MILP vs Scoped)* | *+26.30%* | *+28.92%* | *+27.20%* | *+27.21%* | *+28.91%* |
| **$B = 8,000$** | **full_file** | 0.1669 | 0.1259 | 0.1739 | 0.1725 | 0.1528 |
| | **bm25_raw** | 0.5400 | 0.4029 | 0.5611 | 0.5567 | 0.4891 |
| | **bm25_scoped** | **0.5555** | 0.4101 | 0.5772 | 0.5728 | 0.4978 |
| | **mrtopos_con_greedy** | 0.5531 | **0.4317** | **0.5801** | **0.5756** | **0.5240** |
| | **mrtopos_milp** | 0.5520 | 0.4281 | 0.5790 | 0.5745 | 0.5197 |
| | *Relative Adv (MILP vs Scoped)* | *-0.62%* | *+4.39%* | *+0.31%* | *+0.30%* | *+4.40%* |
| **$B = 16,000$** | **full_file** | 0.2335 | 0.1727 | 0.2432 | 0.2414 | 0.2096 |
| | **bm25_raw** | 0.5872 | 0.4388 | 0.6142 | 0.6095 | 0.5328 |
| | **bm25_scoped** | **0.5961** | **0.4532** | **0.6235** | **0.6186** | **0.5502** |
| | **mrtopos_con_greedy** | 0.5667 | 0.4424 | 0.5938 | 0.5891 | 0.5371 |
| | **mrtopos_milp** | 0.5705 | 0.4460 | 0.5977 | 0.5930 | 0.5415 |
| | *Relative Adv (MILP vs Scoped)* | *-4.28%* | *-1.59%* | *-4.14%* | *-4.14%* | *-1.58%* |

---

## 5. Statistical Rigor and Findings

1. **At Tight Budgets ($B \le 4,000$)**:
   - Under both All References ($N=129$) and Pre-Existing References ($N=128$), MR-TopoS achieves statistically significant improvements ($p < 0.02$ at 2k; $p < 0.001$ at 4k).
   - Under Micro Recall (total hits / total gold files), MR-TopoS retains **107 out of 229 pre-existing files** ($46.72\%$) at $B=2,000$ compared to Scoped BM25's **71 out of 229 files** ($31.00\%$), a **$+50.71\%$ relative increase**.
2. **At High Budgets ($B \ge 8,000$)**:
   - Macro recall reaches parity at $B=8,000$ ($0.5520$ vs $0.5555$, $p = 0.856$).
   - At $B=16,000$, Scoped BM25 achieves higher macro recall ($0.5961$ vs $0.5705$, a $-4.28\%$ difference), though not statistically significant at $\alpha = 0.05$ ($p = 0.179$).
3. **Mandatory Manuscript Corrections**:
   - In Abstract and Results: Label 0.4846 and 0.3728 as **Macro Recall across all patch-modified file references** ($N=129$ tasks).
   - Explicitly cite Pre-Existing Macro Recall: **0.5087 vs. 0.3885** ($+30.95\%$, $p = 0.0072$).
   - Never use the fabricated 0.5883 / 0.4526 scaled numbers.

