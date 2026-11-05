# MR-TopoS Phase 3 Benchmark: Experimental Protocol & Control Specification

## 1. Objective and Scope

This document specifies the experimental protocol, benchmark dataset, evaluation metrics, and strict leakage controls governing the Phase 3 empirical evaluation of **MR-TopoS** (Multi-Resolution Dual-View Program Topology Context Induction).

The benchmark addresses the primary research question:
> *Does topological multi-resolution skeletonization optimized via exact Precedence-Constrained Multi-Choice Knapsack (PC-MCKP) improve bug localization coverage and context quality under fixed token budgets compared to Whole-File and BM25 snippet baselines?*

---

## 2. Benchmark Dataset & Environmental Controls

### 2.1. Task Inventory
The benchmark comprises **129 realistic software engineering tasks** from the official SWE-Gemma dataset spanning four production Python codebases:

| Repository | GitHub Source | Total Tasks | Unique Base Commits | Mean Files / Snapshot | Mean Symbols / Snapshot |
|:---|:---|:---:|:---:|:---:|:---:|
| **FastAPI** | `fastapi/fastapi` | 67 | 67 | 1,181.3 | 6,113.5 |
| **Rich** | `Textualize/rich` | 48 | 47 | 196.4 | 2,031.6 |
| **Requests** | `psf/requests` | 13 | 12 | 36.1 | 711.6 |
| **HTTPX** | `encode/httpx` | 1 | 1 | 45.0 | 887.0 |
| **Total** | — | **129** | **127** | — | — |

*Note: All 127 unique pre-patch repository snapshot archives (`DATA/snapshots/*.tgz`) were directly parsed in-memory, ensuring 100% snapshot fidelity for every historical base commit.*

### 2.2. Token Budget Regimes
To rigorously test context compilation under varying capacity constraints, all four methods are evaluated across four matched token budgets:
- **2,000 tokens** (Severe constraint: typical of small sub-agent call budgets or low-capacity models)
- **4,000 tokens** (Moderate constraint: standard prompt budget for fast agent iterations)
- **8,000 tokens** (Generous constraint: standard context slice for frontier models)
- **16,000 tokens** (High capacity: representative of extended context windows)

### 2.3. Tokenizer Convention
- **Primary Tokenizer**: Google Gemma 256k SentencePiece BPE tokenizer (`alpindale/gemma-2b`, vocabulary size 256,000).
- **Secondary Reference Tokenizer**: ModernBERT WordPiece tokenizer (`answerdotai/ModernBERT-base`, vocabulary size 50,368).
- **Tokenization Protocol**: Subwords are counted directly with `add_special_tokens=False` to ensure exact parity across all methods without artificial padding overhead.

---

## 3. Evaluated Methods

All methods operate on the exact same snapshot AST graph and issue description:

### 1. Full-File Context Baseline (`full_file`)
- **Strategy**: Files are ranked descending by aggregating BM25 scores of their constituent symbols against the task problem statement.
- **Selection**: Whole source files are greedily packed into the context in rank order until the token budget $B$ is reached. Files that exceed remaining capacity are excluded.
- **Syntactic Validity**: 100% (whole files are valid Python modules).
- **Hypothesized Weakness**: Coarse granularity; large files (e.g., 2,000-line modules) exhaust the budget rapidly, starving other relevant files from entering the context.

### 2. BM25 Snippet Context Baseline (`bm25`)
- **Strategy**: Individual symbol functions and classes are ranked descending by raw BM25 score against the problem statement.
- **Selection**: Top-ranking symbol implementations are greedily packed into the context until budget $B$ is reached.
- **Syntactic Validity**: Low under tight budgets. Because selection is unconstrained, methods are selected without their enclosing classes or modules, resulting in orphaned methods and broken syntactic scopes.

### 3. MR-TopoS with Constraint-Aware Greedy Selection (`mrtopos_con_greedy`)
- **Strategy**: Uses identical lexical scores $s_v$ plus topological causal path weights $w_v$ from symptom seeds.
- **Selection**: Greedily upgrades symbols across four resolution tiers (Excluded, Stub, Skeleton, Full) by marginal bundle density $\rho = \Delta v_{\text{bundle}} / \Delta c_{\text{bundle}}$.
- **Precedence Guarantee**: When a child method is selected, all unselected ancestor containers are automatically bundled at minimum viable tier (`STUB`), guaranteeing **0 precedence violations**.

### 4. MR-TopoS with Exact MILP Selection (`mrtopos_milp`)
- **Strategy**: Formulates the multi-resolution context compilation as an exact Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP).
- **Selection**: Solved to global optimality using the HiGHS branch-and-cut solver (`scipy.optimize.milp`).
- **Guarantees**: 0 precedence violations, optimal global trade-off between lexical relevance and causal dependency contracts, with sub-second solve latency.

---

## 4. Evaluation Metrics

### Localization Metrics
- **Recall@1, Recall@5, Recall@10**: Proportion of tasks where at least one ground-truth modified file appears in the top $K$ ranked entities.
- **Mean Reciprocal Rank (MRR)**: $\frac{1}{|T|} \sum_{t \in T} \frac{1}{\text{rank}_t}$ where $\text{rank}_t$ is the 1-indexed rank of the first gold modified file.
- **Gold-File Coverage**: $\frac{|R_t \cap G_t|}{|G_t|}$ where $R_t$ is the set of files present in the constructed context and $G_t$ is the set of ground-truth modified files.

### Context Quality Metrics
- **Tokens Used**: Actual tokens consumed by the compiled context under the Gemma 256k tokenizer.
- **Budget Utilization (%)**: $\frac{\text{Tokens Used}}{B} \times 100\%$.
- **Syntactic Precedence Violations**: Count of methods included in context whose enclosing class is absent (`ResolutionTier.EXCLUDED`).
- **Structural Validity**: Binary indicator (1 if 0 precedence violations; 0 if any orphaned methods exist).
- **Symbol Distribution**: Count of symbols retained at FULL, SKELETON, and STUB resolutions.
- **Solve Runtime (ms)**: Wall-clock latency of context selection.

---

## 5. Strict Experimental Controls & Gold Quarantine

1. **Zero Information Leakage**: Neither the retriever, nor the causal path extractor, nor the MILP optimizer has access to `patch`, `test_patch`, or post-patch commit artifacts.
2. **Pre-Existing File Normalization**: Tasks where patches created brand-new files *ex nihilo* (`@@ -0,0 ... @@`) are audited separately in failure analysis, as pre-patch retrieval cannot locate files that did not exist on disk prior to the patch.
3. **Paired Comparisons**: All four methods are executed on the exact same task instances under identical seeds, budgets, and hardware configurations, eliminating cross-run variance.

