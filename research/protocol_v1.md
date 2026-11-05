# MR-TopoS Research Protocol (v1.0 — Frozen)

**Track**: Google Gemma 4 Developer Agent Paper Track (Kaggle Competition 163111)  
**Document Status**: FROZEN PRIOR TO BENCHMARK EXECUTION  
**Effective Date**: November 5, 2026  
**Auditor Standard**: Independent Adversarial Scientific Protocol

---

## 1. Problem Formulation & Research Objectives

Autonomous software engineering agents operating with open-weights language models (specifically `google/gemma-4-31b-it-qat-w4a16-ct`) face severe operational trade-offs during repository-level bug localization and repair. While large models possess nominal context windows of up to 32k tokens, running multi-turn agent loops, sub-agent tool calls, and high-frequency code edits mandates tight per-turn context budgets (e.g., 2,000 to 8,000 tokens) to avoid KV-cache memory exhaustion and inference slowdowns.

Under constrained token budgets, existing repository context induction strategies fail:
1. **Whole-File Selection**: Suffers from budget starvation. A single 2,000-line module (e.g., `fastapi/routing.py`) monopolizes the budget, preventing related caller, callee, or test modules from being included.
2. **Lexical Snippet Retrieval (BM25)**: Suffers from catastrophic structural fragmentation. Individual functions or methods are extracted as orphaned code blocks lacking their enclosing class declarations, module scopes, and type decorators.
3. **Naive Scope Restoration (Scoped BM25)**: Incurs a severe "scope tax." Wrapping retrieved methods in whole class definitions rapidly consumes tokens, crowding out other relevant candidate symbols.

### Primary Research Questions & Formal Hypotheses

| Research Question | Scientific Hypothesis | Null Hypothesis ($H_0$) | Measured Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **RQ1: Structural Compression** | Multi-resolution AST representations (Stubs and Skeletons) can preserve enclosing lexical scope at $\ge 70\%$ lower token cost than verbatim class definitions. | Multi-resolution stubs provide no statistically significant token savings over raw code or fail syntactic parsing. | Token reduction $\ge 60\%$ with $100\%$ `ast.parse` validity across all 4 benchmark repositories. |
| **RQ2: Context Selection under Budget** | By optimizing across discrete resolution tiers via PC-MCKP, MR-TopoS preserves significantly more relevant symbols and gold files under strict token budgets than Scoped BM25 and Whole-File baselines. | MR-TopoS achieves equal or fewer retained candidate symbols and equal or lower gold coverage than Scoped BM25 under identical token limits. | Statistically significant increase ($p < 0.05$) in retained candidate symbols and gold file coverage at $B \in \{2\text{k}, 4\text{k}\}$. |
| **RQ3: Downstream Agent Utility** | Providing Gemma 4 with syntactically valid, topology-preserving context reduces patch syntax errors and increases verified task resolution rate compared to fragmented raw snippets. | Context topology has no effect on patch syntax validity or downstream pytest resolution rate. | Measurable improvement in valid patch rate or task resolution rate on the controlled repair pilot. |
| **RQ4: Optimization Value (MILP vs. Greedy)** | Exact branch-and-cut MILP achieves lower solve latency at scale and eliminates syntactic precedence violations without the bundle-recalculation overhead of constraint-aware greedy. | Exact MILP is slower, yields negligible objective improvement, or fails to scale compared to greedy selection. | MILP latency $\le 10\text{ ms}$ on $N=60$, with $0$ precedence violations and $\ge 2\times$ speedup over greedy at $N \ge 400$. |

---

## 2. Benchmark Dataset & Environmental Controls

### 2.1. Benchmark Inventory
The evaluation dataset is the official SWE-Gemma benchmark comprising **129 software repair tasks** across four production Python repositories:
- **FastAPI** (`fastapi/fastapi`): 67 tasks across 67 historical base commits (mean 1,181 files / snapshot).
- **Rich** (`Textualize/rich`): 48 tasks across 47 base commits (mean 196 files / snapshot).
- **Requests** (`psf/requests`): 13 tasks across 12 base commits (mean 36 files / snapshot).
- **HTTPX** (`encode/httpx`): 1 task across 1 base commit (45 files / snapshot).

### 2.2. Evaluation Partitions
To prevent iterative tuning on evaluation data:
- **Development Partition ($N=16$ tasks)**: Stratified sample (6 FastAPI, 6 Rich, 3 Requests, 1 HTTPX) utilized strictly for engineering validation, unit testing, and tokenizer calibration.
- **Held-Out Evaluation Partition ($N=129$ tasks)**: All benchmark tasks evaluated once under the frozen protocol and reported without selective cherry-picking.

### 2.3. Matched Token Budgets & Strict Enforcement
All methods are evaluated under four strict token budgets:
- **$B = 2,000$ tokens** (Severe constraint)
- **$B = 4,000$ tokens** (Moderate agent turn budget)
- **$B = 8,000$ tokens** (Standard context slice)
- **$B = 16,000$ tokens** (Generous window)

> [!IMPORTANT]
> **Strict Budget Compliance Invariant**:
> The token budget applies to the **final serialized context string** sent to the language model.
> If $\text{count}(\text{serialized\_context}) > B$, the context is strictly REJECTED as a violation. No over-budget context is ever accepted as a valid run.

---

## 3. Official Tokenizer Specification

- **Target Model**: `google/gemma-4-31B-it-qat-w4a16-ct`
- **Vocabulary Size**: Exactly **262,144** subwords ($2^{18}$).
- **Tokenizer Instance**: `AutoTokenizer.from_pretrained("models/gemma4_tokenizer")`.
- **Counting Convention**: Token counts are evaluated with `add_special_tokens=False` directly on serialized UTF-8 strings. The exact same tokenizer instance is used by the AST builder, candidate compilers, and post-serialization compliance validators.

---

## 4. Evaluated Methods & Strict Controls

All methods operate on the identical task input ($t[\text{problem\_statement}]$) and pre-patch repository snapshot tarball:

1. **`full_file` (Whole-File Baseline)**:
   - Aggregates symbol BM25 scores by file. Greedily packs whole files in descending relevance order until budget $B$.
2. **`bm25_raw` (Raw Snippet Baseline)**:
   - Packs individual symbol implementations in descending BM25 score order until budget $B$. Methods are emitted without enclosing class/module headers.
3. **`bm25_scoped` (Fair Structural Baseline)**:
   - Identical BM25 candidate ranking. Whenever a method is selected, its parent class declaration is restored as an AST stub (`class C: ...`), ensuring enclosing lexical scope.
4. **`mrtopos_con_greedy` (MR-TopoS Constraint-Aware Greedy)**:
   - Multi-resolution selection across Stub, Skeleton, and Full tiers using marginal bundle utility density $\Delta v / \Delta c$, bundling parent stubs to guarantee 0 precedence violations.
5. **`mrtopos_milp` (MR-TopoS Exact MILP)**:
   - Formulates PC-MCKP as an integer linear program solved via HiGHS branch-and-cut in `scipy.optimize.milp`.

### Strict Quarantine Controls
- **Zero Gold Leakage**: Neither the retriever, nor graph builders, nor knapsack compilers have access to `patch`, `test_patch`, or post-patch commit files.
- **Candidate Pool Isolation**: Candidates are retrieved purely from BM25 scoring over snapshot symbols. Candidate limits evaluated: $K=60$ (primary), $K=100$, and $K=200$ (ablation).

---

## 5. Metric Formulations & Denominators

Let $T$ denote the benchmark task set ($|T| = 129$), $G_t$ the set of ground-truth modified files, and $R_t$ the set of files present in compiled context:

1. **Assembled-Context Syntactic Validity**:
   $$\text{Valid}(t) = \begin{cases} 1 & \text{if } \text{ast.parse}(\text{serialized\_context}_t) \text{ succeeds} \\ 0 & \text{otherwise} \end{cases}$$
2. **Parent-Scope Preservation**:
   $$\text{ScopePreserved}(t) = \frac{\sum_{m \in \text{Methods}_t} \mathbb{I}(\text{parent}(m) \in \text{Context}_t)}{|\text{Methods}_t|}$$
3. **Macro Gold-File Coverage**:
   $$\text{MacroCov} = \frac{1}{|T|} \sum_{t \in T} \frac{|R_t \cap G_t|}{|G_t|}$$
4. **Micro Gold-File Coverage (Pre-Existing Files)**:
   $$\text{MicroCov}_{\text{pre}} = \frac{\sum_{t \in T} |R_t \cap G_t^{\text{pre}}|}{\sum_{t \in T} |G_t^{\text{pre}}|} \quad (\text{Denominator: } 229 \text{ pre-existing files})$$
5. **Macro Hit@K**:
   $$\text{Hit@}K = \frac{1}{|T|} \sum_{t \in T} \mathbb{I}(\exists f \in R_t[:K] \cap G_t)$$
6. **Mean Reciprocal Rank (MRR)**:
   $$\text{MRR} = \frac{1}{|T|} \sum_{t \in T} \frac{1}{\text{rank}_t} \quad (\text{rank}_t = \min \{ r \mid R_t[r-1] \in G_t \}, \text{ or } 0 \text{ if no gold file})$$
7. **Budget Utilization**:
   $$\text{Util}(t) = \frac{\text{Tokens}(\text{serialized\_context}_t)}{B} \times 100\%$$
8. **Compilation Latency (ms)**:
   Wall-clock time from candidate scoring to final string serialization.

---

## 6. Protocol Freeze Sign-Off

The experimental conditions, mathematical formulations, tokenizer models, and metric denominators defined in this document are frozen. All benchmark scripts and evaluations must adhere to this specification.

