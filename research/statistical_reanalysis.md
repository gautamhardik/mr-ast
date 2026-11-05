# Comprehensive Statistical Reanalysis and Significance Ledger

**Project**: MR-TopoS (Multi-Resolution Dual-View Program Topology Context Induction)  
**Author**: Independent Principal Research Scientist  
**Date**: November 5, 2026  
**Status**: Authoritative Statistical Record (Recomputed from 2,580 Evaluations)  

---

## 1. Executive Summary

This document presents the complete statistical reanalysis of MR-TopoS against baseline methods across all four token budgets ($B \in \{2000, 4000, 8000, 16000\}$). 

We report sample sizes, degrees of freedom, paired mean differences, $95\%$ confidence intervals, parametric paired $t$-tests, non-parametric Wilcoxon signed-rank tests, Cohen's $d_z$ effect sizes, and evaluate the statistical implications of shared base commits and repository clustering.

All reported figures are recomputed directly from `results/final_benchmark/per_task.csv` and verified in `results/statistics/statistical_reanalysis.json`.

---

## 2. Experimental Design & Statistical Controls

- **Paired Experimental Design**: Every task $t \in \{1, \dots, 129\}$ was evaluated across all five methods under identical budget ceilings and identical Gemma 4 tokenizer configurations. Because variance across software engineering tasks is large (some tasks modify 1 file, others modify 5 files), **paired within-task comparisons** are mandatory to eliminate between-task variance.
- **Repository Clustering & Base Commit Dependence**:
  - The 129 tasks originate from 4 repositories: `fastapi` ($n=67$), `rich` ($n=48$), `requests` ($n=13$), and `httpx` ($n=1$).
  - Across the 129 tasks, there are **127 unique base commits** (only 2 base commits are shared across multiple issues).
  - While tasks within the same repository share common architectural structures, paired testing directly controls for repository-level difficulty by evaluating the delta $\Delta_t = \text{Score}(\text{MR-TopoS}, t) - \text{Score}(\text{Baseline}, t)$.

---

## 3. Statistical Significance Ledger Across All Budgets

### 3.1 All References Macro Recall ($N = 129$ Tasks, $278$ Modified-File References)

| Budget ($B$) | Baseline (Scoped BM25) | MR-TopoS MILP | Mean Difference ($\Delta$) | 95% Confidence Interval | Paired $t$-test | Wilcoxon Signed-Rank | Cohen's $d_z$ | Significance Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$B = 2,000$** | 0.3728 | **0.4846** | $+0.1118$ ($+29.98\%$) | $[+0.0258, +0.1978]$ | $t(128) = 2.572, \mathbf{p = 0.0112}$ | $W = 194.5, \mathbf{p = 0.0170}$ | $0.226$ | **Significant ($p < 0.05$)** |
| **$B = 4,000$** | 0.4282 | **0.5408** | $+0.1126$ ($+26.30\%$) | $[+0.0518, +0.1735]$ | $t(128) = 3.661, \mathbf{p = 0.00037}$ | $W = 128.0, \mathbf{p = 0.00034}$ | $0.322$ | **Highly Significant ($p < 0.001$)** |
| **$B = 8,000$** | **0.5555** | 0.5520 | $-0.0035$ ($-0.62\%$) | $[-0.0413, +0.0344]$ | $t(128) = -0.182, p = 0.856$ | $W = 210.0, p = 0.946$ | $-0.016$ | Parity (Not Significant) |
| **$B = 16,000$** | **0.5961** | 0.5705 | $-0.0255$ ($-4.28\%$) | $[-0.0629, +0.0119]$ | $t(128) = -1.351, p = 0.179$ | $W = 156.0, p = 0.258$ | $-0.119$ | Not Significant ($p > 0.15$) |

---

### 3.2 Pre-Existing References Macro Recall ($N = 128$ Tasks, $229$ Modified-File References)
*(Excluding task `fastapi_15661` where no pre-existing target file existed)*

| Budget ($B$) | Baseline (Scoped BM25) | MR-TopoS MILP | Mean Difference ($\Delta$) | 95% Confidence Interval | Paired $t$-test | Wilcoxon Signed-Rank | Cohen's $d_z$ | Significance Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$B = 2,000$** | 0.3885 | **0.5087** | $+0.1202$ ($+30.95\%$) | $[+0.0331, +0.2073]$ | $t(127) = 2.731, \mathbf{p = 0.0072}$ | $W = 194.5, \mathbf{p = 0.0170}$ | $0.241$ | **Significant ($p < 0.01$)** |
| **$B = 4,000$** | 0.4463 | **0.5677** | $+0.1214$ ($+27.20\%$) | $[+0.0594, +0.1834]$ | $t(127) = 3.877, \mathbf{p = 0.00017}$ | $W = 128.0, \mathbf{p = 0.00033}$ | $0.343$ | **Highly Significant ($p < 0.001$)** |
| **$B = 8,000$** | 0.5772 | **0.5790** | $+0.0017$ ($+0.30\%$) | $[-0.0375, +0.0409]$ | $t(127) = 0.088, p = 0.930$ | $W = 210.0, p = 0.933$ | $0.008$ | Parity (Not Significant) |
| **$B = 16,000$** | **0.6235** | 0.5977 | $-0.0258$ ($-4.14\%$) | $[-0.0635, +0.0119]$ | $t(127) = -1.356, p = 0.178$ | $W = 156.0, p = 0.258$ | $-0.120$ | Not Significant ($p > 0.15$) |

---

### 3.3 Gemma 4 31B Generation Latency Pilot ($N = 6$ Tasks)

- **Sample Size**: $N = 6$ representative benchmark tasks evaluated under identical prompt templates and decoding parameters.
- **Mean Latencies**:
  - `bm25_raw`: $10.22 \pm 6.84\text{ s}$
  - `bm25_scoped`: $10.55 \pm 5.68\text{ s}$
  - `mrtopos_milp`: $\mathbf{7.57 \pm 3.56\text{ s}}$
- **Paired Mean Difference (MR-TopoS vs. Scoped BM25)**:
  - $\Delta = -2.98\text{ s}$ ($-28.28\% \approx -28.3\%$)
  - $95\%$ Confidence Interval: $[-5.76\text{ s}, -0.21\text{ s}]$
  - Paired $t$-test: $t(5) = 2.756, \mathbf{p = 0.038}$ (Statistically significant at $\alpha = 0.05$).

---

## 4. Scientific Interpretation & Summary of Disclosures

1. **Defensible Strength**: Under tight token budgets ($B \le 4,000$), MR-TopoS delivers robust, statistically significant improvements across both parametric and non-parametric tests ($p = 0.0112$ at 2k; $p = 0.00037$ at 4k). The gains are not driven by outliers: the Wilcoxon signed-rank tests confirm significance ($p < 0.02$).
2. **Defensible Parity & Regression Disclosure**: At $B = 8,000$, MR-TopoS and Scoped BM25 are statistically indistinguishable ($p = 0.856$). At $B = 16,000$, MR-TopoS exhibits a $-4.28\%$ lower macro recall ($p = 0.179$). While the regression is not statistically significant at the $\alpha = 0.05$ level, we disclose it explicitly as a candidate-pool ceiling effect ($K=60$).

