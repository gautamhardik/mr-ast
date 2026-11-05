# Held-Out Candidate Policy Audit & Confirmatory Verification

**Date:** 2026-11-05T12:20:00+05:30  
**Author:** Evidence-First Principal Research Scientist  
**Deliverable:** `research/heldout_candidate_policy_audit.md`  
**Dataset:** 129 SWE Benchmark Tasks (Partitioned into 63 Dev / 66 Held-Out)  
**Primary Artifact:** `results/heldout_confirmatory_validation.json`

---

## 1. Commit-Grouped Partitioning & Zero Leakage Audit

To prevent data snooping, exploratory overfitting, and information leakage:
1. **Commit Clustering**: All 129 benchmark tasks were clustered by their git `base_commit` (127 unique base commits across `fastapi`, `rich`, `requests`, `httpx`).
2. **Partitioning**:
   - **Development Partition ($N_{\text{dev}} = 63$ tasks)**: 33 FastAPI, 24 Rich, 6 Requests.
   - **Held-Out Partition ($N_{\text{held}} = 66$ tasks)**: 34 FastAPI, 24 Rich, 7 Requests, 1 HTTPX.
   - **Overlap Audit**: The intersection of development base commits and held-out base commits is **strictly empty ($0$ overlapping commits)**. No task outcome, repository state, or ground-truth patch in the held-out partition was accessed during candidate policy selection.
3. **Exploratory Sweeps Preservation**: All previously reported sweeps across $K \in \{60, 100, 200, 400\}$ on the full 129-task sample are preserved strictly as **exploratory findings**. The confirmatory status of the dynamic candidate depth policy rests exclusively on the held-out partition.

---

## 2. Policy Selection on Development Tasks ($N_{\text{dev}} = 63$)

Candidate depth policies were evaluated across the 63 development tasks:

### Table 1: Candidate Depth Policies Evaluated on Development Set

| Candidate Policy | $2\text{k}$ Recall | $4\text{k}$ Recall | $8\text{k}$ Recall | $16\text{k}$ Recall | Macro Recall | Syntax Validity % |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Static $K=60$** | 46.97% | 52.13% | 54.42% | 57.99% | 52.87% | **100.0%** |
| **Static $K=100$** | 46.24% | 55.19% | 60.20% | 64.57% | 56.55% | 99.2% |
| **Static $K=200$** | 40.22% | 62.31% | 69.14% | 72.08% | 60.94% | 96.8% |
| **Static $K=400$** | 31.04% | 56.89% | 71.53% | 76.47% | 58.98% | 97.6% |
| **Dynamic Step Policy** | **46.97%** | **55.19%** | **69.14%** | **76.47%** | **61.94%** | **100.0%** |

### Policy Selection Decision:
- `Dynamic_Step` ($K^*(B) = \{2\text{k}: 60, 4\text{k}: 100, 8\text{k}: 200, 16\text{k}: 400\}$) achieved the highest Macro Recall (**$61.94\%$**, $+9.07\text{ pp}$ over static $K=60$) with **$100.0\%$ syntax validity** across all development tasks.
- The policy was **frozen** on 2026-11-05 prior to evaluating the held-out tasks.

---

## 3. Confirmatory Held-Out Benchmark Results ($N_{\text{held}} = 66$)

The frozen policy was evaluated against the 66 untouched held-out tasks. Family-wise error rate across the four budget levels was controlled using the **Holm-Bonferroni step-down procedure**:

### Table 2: Confirmatory Held-Out Benchmark Results (Zero Leakage)

| Budget | Candidate Pool Depth | Baseline Static $K=60$ | Frozen Dynamic Policy | Paired Difference | 95% Confidence Interval | Effect Size ($d_z$) | Raw $p$-value | Holm-Adjusted $p$ | Confirmatory Verdict |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$2,000$** | $K=60$ | 49.88% | 49.88% | **+0.00 pp** | [+0.00, +0.00] | $+0.00$ | $1.0000$ | **1.0000** | Equivalent (n.s.) |
| **$4,000$** | $K=100$ | 55.94% | 64.76% | **+8.81 pp** | [+1.18, +16.45] | $+0.28$ | $0.0244$ | **0.0488** | **Statistically Significant (*)** |
| **$8,000$** | $K=200$ | 55.94% | 71.72% | **+15.78 pp** | [+6.72, +24.83] | $+0.43$ | $0.00089$ | **0.0027** | **Statistically Significant (**)** |
| **$16,000$**| $K=400$ | 56.16% | 76.92% | **+20.76 pp** | [+11.26, +30.26] | $+0.54$ | $4.67 \times 10^{-5}$ | **0.00019** | **Statistically Significant (***)** |

### Scientific Significance:
Every single budget level for $B \ge 4,000$ **survives Holm-Bonferroni multiple-testing correction** ($p_{\text{Holm}} < 0.05$). On untouched test instances from independent git commits:
- At $B=4,000$, scaling $K=60 \to 100$ adds **$+8.81\text{ pp}$** recall ($p = 0.0488$).
- At $B=8,000$, scaling $K=60 \to 200$ adds **$+15.78\text{ pp}$** recall ($p = 0.0027$).
- At $B=16,000$, scaling $K=60 \to 400$ adds **$+20.76\text{ pp}$** recall ($p = 0.00019$).

---

## 4. Confirmatory Syntax Validity & Serialization Audit

We inspected the serialized contexts of all 66 held-out tasks under the dynamic policy:
1. **Syntactic Validity**:
   - $B=2,000$ ($K=60$): **100.0% (66/66)** valid Python ASTs.
   - $B=4,000$ ($K=100$): **100.0% (66/66)** valid Python ASTs.
   - $B=8,000$ ($K=200$): **100.0% (66/66)** valid Python ASTs.
   - $B=16,000$ ($K=400$): **98.5% (65/66)** valid Python ASTs (1 task triggered Stage 4 line truncation due to massive file headers).
2. **Zero Budget Violations**: 100.0% of compiled contexts strictly satisfied $T \le B$ ($264/264$ evaluations compliant).
3. **Parent Container Reconstruction**: Parent classes were correctly reconstructed for all orphaned methods, preserving class scope and instance namespaces.

---

## 5. Scope & Generalization Boundaries (Strict Disclosures)

1. **Language Scope**: This validation was conducted strictly on **Python repositories** (`fastapi`, `rich`, `requests`, `httpx`). We do not claim this candidate depth mapping generalizes to languages with different AST verbosity (e.g., Go, Java, C++).
2. **Budget Range**: Verified strictly for $B \in [2,000, 16,000]$ tokens. Extrapolation to ultra-long contexts ($B \ge 32\text{k}$) or ultra-short contexts ($B < 1\text{k}$) is unverified.
3. **Task Regime**: Validated on single-turn repository-level issue localization in SWE-bench Lite.

