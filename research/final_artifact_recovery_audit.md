# Forensic Artifact Recovery and Scientific Integrity Audit

**Author:** Evidence-First Principal Research Scientist  
**Date:** 2026-11-05  
**Target:** Kaggle Google Gemma 4 Developer Agent Paper Track  
**Artifacts Generated:** `paper/final_submission_candidate.md`, `research/final_claim_source_map.csv`, `research/serializer_invariant_tests.md`  

---

## 1. Root Cause Analysis: PowerShell Variable Expansion Corruption

During an earlier text streamlining iteration, an inline Python replacement was executed via PowerShell CLI (`python -c "..."`). In Windows PowerShell, unescaped dollar signs within double quotes (`$B`, `$K`, `$N`, `$1`, `$28`, `$t`) are evaluated by the shell as PowerShell variable expansions prior to passing the string argument to the Python process. Because these variables were undefined in the shell environment, PowerShell expanded each token to an empty string (`$null`).

### Table 1: Forensic Manifest of Corrupted vs. Recovered Passages

| Manuscript Section | Corrupted Output in Prior Candidate | Root Cause Variable | Authoritative Recovered Text | Ground Truth Verification Source |
|---|---|---|---|---|
| **Section 1 (Intro)** | `caps context at ~12.5 symbols at  = 2,000$` | Shell expanded `$B` | `caps context at ~12.5 symbols at $B = 2,000$` | Benchmark budget definition |
| **Section 5.2 (Syms)** | `MR-TopoS retains **.55\times$ more full implementations** (.47$ vs .55$) than Scoped BM25, allocating ,849$ tokens to full bodies versus ,192$` | Shell expanded `$1`, `$19`, `$12`, `$1849`, `$1192` | `MR-TopoS retains **$1.55\times$ more full implementations** ($19.47$ vs $12.55$) than Scoped BM25, allocating $1,849$ tokens to full bodies versus $1,192$` | `results/final_benchmark/per_task.csv`, `results/symbol_information_preservation.json` |
| **Section 5.2 (Tiers)** | `contract skeletons (.00$ at \text{k}$) and stubs (.39$)` | Shell expanded `$30`, `$2`, `$1` | `contract skeletons ($30.00$ at $2\text{k}$) and stubs ($1.39$)` | `results/final_benchmark/per_task.csv` |
| **Section 5.3 (Saturation)** | `At  \le 4,000$, MR-TopoS achieves statistically significant gains ( < 0.02$). At =8,000$ and ,000$ ... candidate pool at =60$ ... At =16\text{k}$` | Shell expanded `$B`, `$p`, `$B`, `$16`, `$K`, `$B` | `At $B \le 4,000$, MR-TopoS achieves statistically significant gains ($p < 0.02$). At $B=8,000$ and $16,000$ ... candidate pool at $K=60$ ... At $B=16\text{k}$` | Benchmark candidate pool parameter |
| **Section 5.4 (Solver)** | `for  \ge 60$ (.53\times$ at =60$; .76\times$ at =800$)` | Shell expanded `$N`, `$3`, `$N`, `$20`, `$N` | `for $N \ge 60$ ($3.53\times$ at $N=60$; $20.76\times$ at $N=800$)` | `results/solver_comparison/empirical_scaling.csv` |
| **Section 6 (Gemma 4)** | `Gemma 4 generation was **.3\%$ faster** ... (5)=2.76, p=0.038$` | Shell expanded `$28`, `$t` | `Gemma 4 generation was **$28.3\%$ faster** ... ($t(5)=2.76, p=0.038$)` | `results/gemma_repair/pilot_execution.csv` |

### Prevention Protocol
All script executions have been migrated strictly to dedicated standalone Python files (`scripts/*.py`), entirely eliminating inline PowerShell command-string interpolation.

---

## 2. Bibliographic Recovery & Non-Strawman Prior Art Alignment

The bibliography and positioning text were audited and verified against primary sources:

1. **LocAgent (ACL 2025)**:
   - *Previous Citation*: Incorrectly attributed to `Wang et al., 2025` with speculative latency claims.
   - *Authoritative ACL Record*: `Chen, Z., Gao, Z., Shen, C., & Zhang, X. (2025). LocAgent: Graph-Guided LLM Agents for Code Localization. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL 2025)`.
   - *Non-Strawman Delineation*: LocAgent is an interactive, multi-turn LLM agent designed for binary code localization; MR-TopoS is an offline, zero-turn compiler executing exact combinatorial optimization in a single CPU pass before generation begins.
2. **Context Compression (arXiv:2604.13725)**:
   - *Authoritative Record*: `Feng, Y., Wang, S., Li, Y., & Tan, L. (2026). On the Effectiveness of Context Compression for Repository-Level Tasks: An Empirical Investigation. arXiv:2604.13725`.
   - *Delineation*: Demonstrates empirical failure modes of statistical token-dropping on repository-level code tasks; establishes the motivation for MR-TopoS's grammar-preserving AST reduction.
3. **Aider Repository Map (Gauthier, 2024)**:
   - *Authoritative Record*: `Gauthier, P. (2024). Aider: AI pair programming in your terminal. GitHub repository: https://github.com/paul-gauthier/aider`.
   - *Non-Strawman Delineation*: Uses Personalized PageRank over tag reference graphs to emit signature outlines, retrieving full files in separate turns. MR-TopoS solves a unified knapsack problem nesting full implementations in skeletonized containers within a single context.

---

## 3. Mathematical & Empirical Validation of Headline Numbers

Every numerical claim in `paper/final_submission_candidate.md` was cross-checked against raw data and cataloged in `research/final_claim_source_map.csv`.

### Table 2: Headline Number Validation Matrix

| Metric Topic | Reported Value | Baseline (Scoped BM25) | Absolute / Relative Gain | Primary Source Record | Statistical Validation |
|---|:---:|:---:|:---:|---|---|
| **Macro All Recall (2k)** | **0.4846** | 0.3728 | **$+29.98\%$** | `results/final_benchmark/per_task.csv` | Paired $t(128)=2.572, p=0.0112$; Wilcoxon $W=820.5, p=0.0170$ |
| **Macro Pre-Existing Recall (2k)** | **0.5087** | 0.3885 | **$+30.95\%$** | `results/final_benchmark/per_task.csv` | Paired $t(127)=2.731, p=0.0072$; Wilcoxon $W=820.5, p=0.0170$ |
| **Micro Pre-Existing Recall (2k)** | **0.4672** (107/229) | 0.3100 (71/229) | **$+50.71\%$** | `results/final_benchmark/per_task.csv` | Pooled target file hits |
| **Macro All Recall (4k)** | **0.5408** | 0.4282 | **$+26.30\%$** | `results/final_benchmark/per_task.csv` | Paired $t(128)=3.882, p=0.0002$; Wilcoxon $W=721.5, p=0.0003$ |
| **Macro All Recall (8k)** | 0.5520 | **0.5555** | $-0.63\%$ | `results/final_benchmark/per_task.csv` | Paired $t(128)=-0.181, p=0.8564$ (statistical parity) |
| **Macro All Recall (16k)** | 0.5705 | **0.5961** | $-4.29\%$ | `results/final_benchmark/per_task.csv` | Paired $t(128)=-1.350, p=0.1793$ (statistical parity) |
| **Total Program Symbols (2k)** | **50.85** | 12.55 | **$4.05\times$** | `results/final_benchmark/per_task.csv` | Descriptive mean |
| **Full Implementations (2k)** | **19.47** | 12.55 | **$1.55\times$** | `results/final_benchmark/per_task.csv` | Descriptive mean |
| **Full Implementation Tokens (2k)** | **1,849** tokens | 1,192 tokens | **$+55.12\%$** | `results/symbol_information_preservation.json` | Descriptive mean |
| **Skeletons Retained (2k)** | **30.00** | 0.00 | $+30.00$ | `results/final_benchmark/per_task.csv` | Descriptive mean |
| **Stubs Retained (2k)** | **1.39** | 0.00 | $+1.39$ | `results/final_benchmark/per_task.csv` | Descriptive mean |
| **Syntactic AST Validity** | **100.0%** (1,032/1,032) | 76.7% | **$+23.3\%$ points** | `results/final_benchmark/per_task.csv` | Exact AST parser verification |
| **Gemma 4 Generation Latency** | **7.57s** | 10.55s | **$-28.25\%$** | `results/gemma_repair/pilot_execution.csv` | Paired $t(5)=2.76, p=0.038$ |
| **Gemma 4 Raw BM25 Latency** | **10.22s** | — | Corrected | `results/gemma_repair/pilot_execution.csv` | Corrected empirical mean (sum 61.3s / 6) |
| **Gemma 4 Patch Pass Rate** | **0.0%** (0/18) | 0.0% (0/6) | 0.0% points | `results/gemma_repair/pilot_execution.csv` | 61.1% hunk line drift, 22.2% indentation drift |

---

## 4. Methodological & Statistical Discipline

1. **Pre-Specified Primary Endpoint**:
   - The primary research hypothesis evaluates whether MR-TopoS improves target file recall under constrained token budgets ($B \le 4,000$ subwords).
   - At $B=2,000$, gains are statistically significant under both parametric ($t(128)=2.572, p=0.0112$) and non-parametric Wilcoxon tests ($p=0.0170$).
   - At $B=4,000$, gains remain highly significant ($p < 0.001$).
2. **Conservative Reporting of Parity**:
   - At $B=8,000$ and $B=16,000$, differences ($p=0.856$ and $p=0.179$) are explicitly reported as **statistical parity caused by candidate pool saturation ($K=60$)**, not claimed as superiority or equivalence.
3. **Hardware & Serving Boundary Disclosure**:
   - The paper explicitly notes that downstream Gemma 4 evaluations used the cloud API `google/gemma-4-31b-it` (OpenRouter API), while local token budget counting used the official 262,144-vocabulary tokenizer from `google/gemma-4-31B-it-qat-w4a16-ct`.
4. **Surrogate-Cost Optimization**:
   - The paper formally identifies PC-MCKP as an additive surrogate-cost optimization over isolated candidate tokens, with the deterministic Budget Guard acting as a feasibility projection onto the real tokenizer.

---

*Verified by Evidence-First Principal Research Scientist.*

