# Comprehensive Experimental Design: Context Induction for Developer Agents

**Author:** Antigravity Research Team (Adversarial Audit Group)  
**Date:** November 5, 2026  
**Document:** `audit/topospec_experimental_design.md`  
**Target:** Google - The Gemma 4 Developer Agent Paper Track  
**Status:** Approved Experimental Specification  

---

## 1. Experimental Objectives

The purpose of this experimental design is to rigorously evaluate whether structured, graph-and-AST-conditioned context compilation produces superior developer agent performance compared to traditional retrieval and flat truncation baselines, under strictly matched token budgets.

We eliminate all historical flaws of U-GRACE by enforcing:
1. **Strictly Matched Token Budgets:** Every method must compile its context into identical token caps $B \in \{2048, 4096, 8192, 16384\}$.
2. **Standard Non-Tautological Metrics:** Relevant File Recall, Relevant Symbol Recall, Syntactic Parse Validity, and SWE-bench Pass@1.
3. **Repository-Stratified Analysis:** Disaggregated reporting across FastAPI ($N=67$), Rich ($N=48$), Requests ($N=13$), and HTTPX ($N=1$).
4. **Deterministic Reproducibility:** Fixed random seeds, exact snapshot extraction, and open-source metric harnesses.

---

## 2. Experimental Baselines (6-Way Protocol)

Every baseline receives identical inputs: the issue `problem_statement` and the repository snapshot at `base_commit`.

```
                    ┌────────────────────────────┐
                    │ Issue Problem Statement    │
                    └─────────────┬──────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ M1: Full-File    │    │ M2: BM25 Lexical │    │ M3: BM25 +       │
│ Concatenation    │    │ File Retrieval   │    │ Truncation       │
└──────────────────┘    └──────────────────┘    └──────────────────┘
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ M4: Flat AST     │    │ M5: Pure Graph   │    │ M6: MR-TopoS     │
│ Skeletonization  │    │ Neighborhood     │    │ (Proposed)       │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### Baseline Definitions:

1. **M1: Full-File Concatenation (Unconstrained Upper Bound / Baseline)**
   - Concatenates the top-$k$ retrieved files in their entirety without modification. If the token count exceeds budget $B$, hard-truncates at the character boundary.
2. **M2: Standard BM25 File Retrieval**
   - Retrieves files ranked by Okapi BM25 scores on repository source code. Includes only as many complete files as fit within budget $B$ (no partial file truncation).
3. **M3: BM25 with Ordinary Window Truncation**
   - Retrieves top BM25 files and extracts fixed-line windows (e.g., 50 lines centered around the highest scoring BM25 match) to pack as many partial snippets as possible into budget $B$.
4. **M4: AST Skeletonization Without Graph (Agentless-Style)**
   - Takes top BM25 candidate files and replaces all function and method bodies with `...`, retaining class declarations, type signatures, and docstrings. Packs skeletonized files sequentially into budget $B$.
5. **M5: Pure Graph Neighborhood Without Skeletonization (LocAgent-Style Subgraph)**
   - Takes seed symbols matched by BM25, performs 1-hop and 2-hop call graph expansion, and includes the full implementation text of all traversed nodes until budget $B$ is exhausted.
6. **M6: MR-TopoS (Proposed Dual-View Multi-Resolution Knapsack)**
   - Constructs a Dual-View Program Topology (Syntactic AST Hierarchy + Call Graph).
   - Solves the Steiner Subgraph Multi-Choice Knapsack Problem (MCKP) to dynamically assign resolution tiers (Tier 0: Stub, Tier 1: Cleaned Contract Skeleton, Tier 2: Full Body) subject to $\sum \text{Cost}(v, r_v) \le B$.

---

## 3. Evaluation Metrics & Formal Formulations

### 3.1 Token Consumption & Compression Efficiency
* **Context Tokens ($T$):** The exact number of tokens in the compiled prompt context, measured using the official Gemma 4 tokenizer (`gemma-tokenizer`).
* **Compression Ratio ($\rho$):**
  $$\rho = 1 - \frac{T}{T_{\text{full\_repo}}}$$
  where $T_{\text{full\_repo}}$ is the token count of all source files in the active repository.

### 3.2 Retrieval & Context Preservation Metrics
* **Relevant File Recall@B ($\text{R}_{\text{file}}@B$):**
  $$\text{R}_{\text{file}}@B = \frac{|\mathcal{F}_{\text{context}} \cap \mathcal{F}_{\text{patch}}|}{|\mathcal{F}_{\text{patch}}|}$$
  where $\mathcal{F}_{\text{context}}$ is the set of files present in the context, and $\mathcal{F}_{\text{patch}}$ is the set of ground-truth modified files.
* **Relevant Symbol Recall@B ($\text{R}_{\text{sym}}@B$):**
  $$\text{R}_{\text{sym}}@B = \frac{|\mathcal{S}_{\text{context}} \cap \mathcal{S}_{\text{patch}}|}{|\mathcal{S}_{\text{patch}}|}$$
  where $\mathcal{S}_{\text{patch}}$ is the set of functions/classes directly modified in the ground-truth patch, and $\mathcal{S}_{\text{context}}$ are symbols included at Resolution Tier 1 or Tier 2.
* **Interface Contract Preservation Rate ($\text{ICPR}$):**
  The percentage of caller-callee invocation edges $(u, v)$ in the ground-truth execution path where the callee's interface contract is intact in the context.

### 3.3 Downstream Agent Performance (End-to-End)
* **Syntactic Patch Validity ($\text{SPV}$):**
  $$\text{SPV} = \frac{\sum_{i=1}^N \mathbf{1}[\text{Patch } P_i \text{ is a valid unidiff and parses under } \texttt{git apply}]}{N}$$
* **Test Pass Rate / Issue Resolution (Pass@1):**
  $$\text{Pass@1} = \frac{\sum_{i=1}^N \mathbf{1}[\text{All FAIL\_TO\_PASS tests pass and PASS\_TO\_PASS tests pass}]}{N}$$
  Measured in an isolated containerized evaluation environment matching SWE-bench protocols.

### 3.4 Operational Cost & Latency
* **Compilation Latency ($\tau_{\text{comp}}$):** Wall-clock time (milliseconds) to parse ASTs, solve the MCKP knapsack, and assemble the prompt.
* **Inference Cost ($\$_{\text{inf}}$):** Monetary cost calculated from input prompt tokens and generated patch tokens using standard API tier pricing.

---

## 4. Matched Token Budget Conditions

Experiments will be conducted across four operational budget regimes:
1. **$B = 2,048$ tokens (Ultra-Constrained):** Simulates edge environments and small local models where prompt space is severely restricted.
2. **$B = 4,096$ tokens (Standard Agent Budget):** Standard developer agent window allocation for multi-turn dialogue.
3. **$B = 8,192$ tokens (High-Capacity Budget):** Recommended baseline for Gemma 4 developer agent architectures.
4. **$B = 16,384$ tokens (Expanded Context Window):** Tests the asymptote where context compaction transitions into information saturation.

---

## 5. Statistical Rigor & Hypothesis Testing

### 5.1 Repository-Stratified Evaluation
Results will be reported in stratified format:
* **Cohort 1 (Web Framework):** FastAPI ($N = 67$, High modularity, isolated tutorial files).
* **Cohort 2 (Terminal UI Engine):** Rich ($N = 48$, Dense inter-procedural call graph, high connectivity).
* **Cohort 3 (HTTP Client):** Requests ($N = 13$, Compact legacy architecture).
* **Cohort 4 (Qualitative Case Study):** HTTPX ($N = 1$).

### 5.2 Hypothesis Testing Protocol
To demonstrate that MR-TopoS is statistically superior to baselines M1–M5:
* **Continuous Metrics ($\text{R}_{\text{file}}$, $\text{R}_{\text{sym}}$, $T$):** Two-sided Paired Wilcoxon Signed-Rank Test with significance threshold $\alpha = 0.01$.
* **Discrete Success (Pass@1):** McNemar’s Test on paired binomially distributed task outcomes.
* **Confidence Intervals:** 95% empirical bootstrap confidence intervals computed over $B = 1,000$ resamples.

---

## 6. Execution Roadmap & Verification Gates

```
Phase 1: Metric & Tokenizer Freeze ────► Phase 2: Offline Context Compilation
                                                   │
Phase 4: Statistical Significance  ◄──── Phase 3: Model Patch Generation (Gemma)
```

1. **Gate 1 (Offline Compilation Verification):**
   Verify that all 6 baselines compile contexts within exact token budgets ($\le B$) for all 129 tasks, and that output text is 100% syntactically valid Python.
2. **Gate 2 (Symbol Recall Verification):**
   Verify that symbol-level ground truth tags are extracted without data leakage (no lookahead into `patch` during retrieval).
3. **Gate 3 (Downstream Generation Verification):**
   Ensure Gemma 4 model inference uses fixed temperature ($T = 0.2$), deterministic sampling, and logs raw responses to disk.

