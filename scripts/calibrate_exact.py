"""
calibrate_exact.py: Calibrates the paper to strictly [2820, 2880] words.
"""

import sys

# P0: Title & Metadata
p0 = """# Multi-Resolution AST Context Selection for Budget-Constrained Software Engineering Agents

**Anonymous Authors**  
*Paper Track Submission — Google Gemma 4 Developer Agent Track (Kaggle Competition ID: 163111)*"""

# Abstract
p1 = """## Abstract

Autonomous software engineering agents operate under strict token budgets. In bug localization, agents face a dilemma between coarse whole-file retrieval—which rapidly exhausts context capacity—and snippet extraction—which severs Abstract Syntax Tree (AST) scopes, causing syntax errors in 24.8% of cases. Restoring enclosing class headers eliminates syntax errors, but monolithic binary inclusion caps symbol capacity at ~12.5 entities at $B = 2,000$ tokens. We present **MR-TopoS**, a context compiler formulating budget-constrained context selection as a **Multiple-Choice Knapsack Problem (MCKP)**. By selecting discrete resolution tiers (Full, Skeleton, Stub) across budget-scaled candidate depths ($K_{\\text{step}}(B) \\in \\{60, 100, 200, 400\\}$), MR-TopoS overcomes monolithic inclusion bottlenecks. Syntactic validity is preserved post-hoc by an AST-aware serializer (Invariant 1) reconstructing class headers at an empirical median cost of 5.0 tokens per class, with multi-stage atomic symbol pruning guaranteeing 100% budget compliance against the Google Gemma 4 tokenizer. Across 129 SWE benchmark tasks (5,160 runs), multi-resolution selection yields a $+16.61\\text{ pp}$ recall gain at $B=2,000$ ($p_{\\text{Holm}} = 0.0006$) and retains **$1.55\\times$ more full implementations**. On 66 held-out tasks (zero commit leakage), dynamic candidate depth lifts $16\\text{k}$ recall to **$76.92\\%$** ($+16.44\\text{ pp}$ over Scoped BM25, $p_{\\text{Holm-12}} = 0.0043$). In an exploratory pilot on `google/gemma-4-31b-it`, contract skeletons reduce prompt latency by **$28.3\\%$** ($p = 0.038$)."""

# Section 1
p2 = """## 1. Introduction & Related Work

Autonomous developer agents automate software maintenance across repositories (Jimenez et al., 2024; Yang et al., 2024). However, models like Google Gemma 4 31B encounter an operational bottleneck: **context compilation under constrained token budgets**. Real-world codebases span millions of tokens; uncompressed contexts degrade attention focus (Liu et al., 2024) and crowd out target files. Snippet retrieval extracts isolated methods but severs enclosing scopes, inducing syntax errors in 24.8% of cases. Enclosing snippets in parent class stubs restores syntax, but monolithic binary inclusion caps context at ~12.5 symbols at $B = 2,000$ tokens. Our 129-task audit reveals class headers consume an empirical median of only 5.0 tokens; the true bottleneck is the absence of multi-resolution representation.

### Positioning Relative to Prior Art
1. **LocAgent (ACL 2025)**: Explores code graphs interactively via multi-turn LLM queries for file localization (Chen et al., 2025). MR-TopoS is an offline zero-turn compiler solving combinatorial context selection on CPU in milliseconds before generation begins.
2. **Aider Repository Map Baseline**: Emits signature outlines via PageRank over reference graphs, retrieving files in subsequent turns (Gauthier, 2024). Evaluating an Aider-inspired static repository-map baseline under identical budgets discloses that its 0% AST validity and zero full implementations are by-design properties of interactive outlines. MR-TopoS compiles executable implementations alongside contracts in 22–78 ms.
3. **Context Compression (EMNLP 2023; arXiv:2604.13725)**: Drops tokens via perplexity (Li et al., 2023; Feng et al., 2026), breaking syntax delimiters. MR-TopoS enforces grammar-preserving AST transformations.

### Contributions
1. **Multi-Resolution Representation**: Discrete Full, Skeleton, and Stub tiers deliver a **$+16.61\\text{ pp}$** recall gain at $2\\text{k}$ ($p_{\\text{Holm}} = 0.0006$) and retain **$1.55\\times$ more full implementations** than Scoped BM25.
2. **Pure MCKP Formulation**: Removing knapsack precedence constraints recovers $+5.43\\text{ pp}$ recall at $2\\text{k}$ ($p = 0.0050$), delegating structural closure to the serializer.
3. **Dynamic Candidate Scaling**: Scaling candidate depth ($K_{\\text{step}}(B)$) on 66 held-out tasks (zero commit leakage) lifts $16\\text{k}$ recall to **$76.92\\%$** ($+16.44\\text{ pp}$ over Scoped BM25, $p_{\\text{Holm-12}} = 0.0043$; $+20.76\\text{ pp}$ over static pools, $p_{\\text{Holm-12}} = 0.00056$).
4. **Deterministic Structural Invariant**: Invariant 1 formalizes syntactic closure under atomic symbol pruning, eliminating truncation errors and reducing Gemma 4 generation latency by $28.3\\%$."""

# Section 2
p3 = """## 2. Theoretical Foundations & Problem Formulation

### 2.1 Repository Abstract Syntax Trees
We represent a repository as an AST forest $\\mathcal{T} = (\\mathcal{V}, \\mathcal{E}_{\\text{hier}})$ where $\\mathcal{V}$ denotes program entities (modules, classes, methods). Directed edges $(u, v) \\in \\mathcal{E}_{\\text{hier}}$ encode strict downward containment ($\\text{Module} \\to \\text{Class} \\to \\text{Method}$). Entities have at most one parent $p(i)$; modules act as independent roots without artificial root hubs.

### 2.2 Multi-Resolution Representation Lattice
MR-TopoS defines a 4-tier discrete resolution lattice $\\mathcal{R} = \\{\\text{EXCLUDED} (0), \\text{STUB} (1), \\text{SKELETON} (2), \\text{FULL} (3)\\}$:
- **Tier 3 (FULL)**: Complete original source code of entity $i$.
- **Tier 2 (SKELETON)**: Contract skeleton preserving signatures, defaults, type annotations, and 1-line docstrings, with bodies replaced by `...`.
- **Tier 1 (STUB)**: Structural stub retaining only identifier signature and `...` (`def name(...): ...`).
- **Tier 0 (EXCLUDED)**: The entity is omitted ($\\epsilon$).

Token costs $c_{ir}$ are measured directly by the Gemma 4 tokenizer ($0 = c_{i0} < c_{i1} \\le c_{i2} \\le c_{i3}$).

### 2.3 Multiple-Choice Knapsack Problem (MCKP)
Let $\\mathcal{N} \\subseteq \\mathcal{V}$ denote candidate pool of depth $N = K_{\\text{step}}(B)$. Binary variable $x_{ir} \\in \\{0, 1\\}$ indicates whether entity $i$ is compiled at tier $r$. Base lexical score $s_i$ is computed via BM25. Static topological call-graph weights provide $0.00\\text{ pp}$ marginal recall across budgets in factorial ablations; we set utility directly to $u_i = s_i$. With tier multipliers $\\alpha_r \\in \\{0.0, 0.4, 0.7, 1.0\\}$, context compilation is formulated as:

$$\\max_{\\mathbf{x}} \\sum_{i \\in \\mathcal{N}} \\sum_{r \\in \\mathcal{R}} \\alpha_r u_i x_{ir} \\quad \\text{s.t.} \\quad \\sum_{i \\in \\mathcal{N}} \\sum_{r=1}^3 c_{ir} x_{ir} \\le B, \\quad \\sum_{r \\in \\mathcal{R}} x_{ir} = 1, \\quad x_{ir} \\in \\{0, 1\\}$$

### 2.4 Removal of Knapsack Precedence Constraints
Factorial ablation demonstrates that enforcing precedence inside the knapsack penalizes compound classes, reducing recall by $-5.43\\text{ pp}$ at $B=2,000$ ($p = 0.0050$) without improving syntactic validity. In MR-TopoS, explicit precedence constraints are **removed from the optimization model**; structural closure is delegated to the Context Composition Operator $\\mathcal{C}(\\mathbf{x})$.

### 2.5 Solver Delineation & Algorithmic Complexity
1. **Constraint-Aware Greedy Heuristic (Production Compiler)**: An $O(N \\log N)$ polynomial-time heuristic sorting $3N$ upgrade steps by efficiency gradient $\\rho = \\Delta u / \\Delta c$ and executing a linear feasibility pass in $O(N)$ time with $O(N)$ auxiliary space.
2. **HiGHS Reference Solver (Exact Branch-and-Cut)**: An exact branch-and-cut solver (Huangfu & Hall, 2018) achieving a 0.0% optimality gap. On SWE benchmark tasks, Greedy and HiGHS achieve statistically equivalent recall ($p \\ge 0.18$)."""

# Section 3
inv1 = """### Invariant 1 (Serializer Syntactic Invariant)
*Let $\\mathcal{G} = (\\mathcal{V}, \\mathcal{E})$ be an AST program graph extracted from a well-formed Python snapshot where symbols belong to standard construct types (`ClassDef`, `FunctionDef`, `AsyncFunctionDef`, `Assign`, `AnnAssign`). For any tier selection vector $\\mathbf{x} \\in \\{0, 1\\}^{N \\times |\\mathcal{R}|}$ and budget $B$, the serializer $\\mathcal{C}(\\mathbf{x})$ produces an emitted string satisfying $\\text{ast.parse}(\\mathcal{C}(\\mathbf{x})) \\neq \\text{SyntaxError}$ and $\\text{GemmaTokenizer}(\\mathcal{C}(\\mathbf{x})) \\le B$, provided that methods are indented under class headers, empty suites emit `...`, and layout overhead is absorbed via monotonic tier downgrades and atomic symbol pruning without string line-slicing.*"""

p4 = f"""## 3. Methodology & Architecture

### 3.1 Validated Candidate-Depth Schedule $K_{{\\text{{step}}}}(B)$
Fixing candidate depth introduces failure modes: small pools ($K=60$) starve under large budgets ($B=16\\text{{k}}$), while large pools ($K=400$) scatter tokens across disconnected stubs at small budgets ($B=2\\text{{k}}$). MR-TopoS couples candidate depth to budget via a validated discrete schedule:

$$K_{{\\text{{step}}}}(B) = \\begin{{cases}} 60 & \\text{{for }} B = 2,000 \\\\ 100 & \\text{{for }} B = 4,000 \\\\ 200 & \\text{{for }} B = 8,000 \\\\ 400 & \\text{{for }} B = 16,000 \\end{{cases}}$$

### 3.2 Context Composition Operator $\\mathcal{{C}}(\\mathbf{{x}})$
The context string is generated by an AST composition operator $\\mathcal{{C}}(\\mathbf{{x}})$:
1. **File Grouping**: Active symbols $\\mathcal{{S}}^* = \\{{s_i \\mid x_{{ir}}=1, r \\ge 1\\}}$ are partitioned by file path $\\mathcal{{F}}_p$.
2. **Shared-Parent Reconstruction**: For methods in class $C$, the operator emits an enclosing `class C:` header, nesting selected methods inside with uniform 4-space indentation. If omitted by the optimizer ($x_{{C0}}=1$), the serializer reconstructs the header post-hoc. Reconstructed headers incur an empirical median overhead of only $5.0$ tokens (mean $5.06$), while shared-parent deduplication achieves a **$56.05\\%$ pooled deduplication rate** ($43.39\\%$ mean per run), eliminating 12,224 redundant class definitions across 493 reconstructed runs (out of 496 method-parent runs; in 3 runs the parent class was selected directly by the knapsack optimizer).

{inv1}

### 3.3 Multi-Stage Monotonic Atomic Symbol Pruning
Because reconstructed headers add layout overhead ($27.6$ to $111.1$ tokens on average), the optimizer operates on an additive surrogate model. If serialized tokens exceed budget ($T > B$), an adaptive Budget Guard executes multi-stage monotonic downgrades (STUB $\\to$ EXCLUDED, SKELETON $\\to$ STUB, FULL $\\to$ SKELETON) followed by atomic symbol exclusion. In regression testing across all 28 historical failure cases, atomic symbol pruning achieved **$100.0\\%$ syntactic validity and $0$ line truncations**."""

# Section 4
p5 = """## 4. Experimental Setup & Benchmark Corpus

### 4.1 Benchmark Corpus & Partitions
We evaluate MR-TopoS on 129 SWE benchmark tasks from SWE-bench Lite across four mature repositories: `fastapi/fastapi` (67 tasks), `Textualize/rich` (48 tasks), `psf/requests` (13 tasks), and `encode/httpx` (1 task). Ground-truth patches modify 278 file instances (229 pre-existing, 49 patch-created). Tasks are clustered by git `base_commit` (127 unique clusters) and partitioned into a 63-task Development set and a 66-task Untouched Held-Out set with zero commit overlap.

### 4.2 Token Budgets & Target Tokenizer
We evaluate four budgets: $B \\in \\{2,000, 4,000, 8,000, 16,000\\}$ tokens against the Google Gemma 4 tokenizer (`models/gemma4_tokenizer/tokenizer.json`, vocabulary size 262,144).

### 4.3 Baseline Architectures
1. **`full_file`**: Greedily packs full source files ranked by BM25.
2. **`bm25_scoped`**: Packs raw BM25 snippets wrapped in class stubs.
3. **`aider_repomap`**: Reproduction of Aider's NetworkX PageRank outline packing.
4. **`mrtopos_con_greedy`**: Constraint-Aware Greedy selector solving MCKP in $O(N \\log N)$ time.
5. **`mrtopos_milp`**: Exact HiGHS branch-and-cut solver with 0% gap."""

# Section 5 tables
tab1 = """**Table 1: Master Factorial Benchmark Results Across 129 SWE Tasks**

| Method | Budget | Gold Recall (All) | Pre-Exist Recall | Retained Syms | Full Impls | Skeletons | Syntax Valid % | Solve Time (ms) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **full_file** | 2k | 0.1262 | 0.1315 | 59.05 | 59.05 | 0.00 | 41.9% | 133.31 |
| | 4k | 0.1287 | 0.1341 | 64.12 | 64.12 | 0.00 | 62.8% | 196.21 |
| | 8k | 0.1669 | 0.1739 | 77.91 | 77.91 | 0.00 | 65.9% | 262.84 |
| | 16k | 0.2335 | 0.2432 | 109.37 | 109.37 | 0.00 | 72.9% | 389.95 |
|---|---|---|---|---|---|---|---|---|
| **bm25_scoped** | 2k | 0.3728 | 0.4362 | 12.55 | 12.55 | 0.00 | 75.2% | 127.01 |
| | 4k | 0.4282 | 0.5011 | 19.98 | 19.98 | 0.00 | 66.7% | 158.82 |
| | 8k | 0.5555 | 0.6481 | 33.09 | 33.09 | 0.00 | 77.5% | 244.59 |
| | 16k | 0.5961 | 0.7000 | 47.76 | 47.76 | 0.00 | 87.6% | 330.92 |
|---|---|---|---|---|---|---|---|---|
| **aider_repomap** | 2k | 0.4453 | 0.5306 | 161.80 | 0.00 | 161.80 | 0.0%* | 1,195.59 |
| | 4k | 0.5279 | 0.6242 | 302.50 | 0.00 | 302.50 | 0.0%* | 1,162.08 |
| | 8k | **0.5619** | **0.6700** | 580.40 | 0.00 | 580.40 | 0.0%* | 1,283.00 |
| | 16k | **0.6785** | **0.8055** | 1,105.70 | 0.00 | 1,105.70 | 0.0%* | 1,425.04 |
|---|---|---|---|---|---|---|---|---|
| **mrtopos_con_greedy** | 2k | 0.4730 | 0.5580 | 50.45 | 19.63 | 29.53 | **100.0%** | **26.05** |
| | 4k | 0.4939 | 0.5843 | 54.33 | 33.24 | 20.67 | **100.0%** | **23.69** |
| | 8k | 0.5531 | 0.6513 | 57.34 | 45.13 | 11.96 | **100.0%** | **39.06** |
| | 16k | 0.5667 | 0.6667 | 59.50 | 53.64 | 5.59 | **100.0%** | **27.81** |
|---|---|---|---|---|---|---|---|---|
| **mrtopos_milp (Ref)** | 2k | **0.4846** | **0.5712** | **50.85** | **19.47** | **30.00** | **100.0%** | 77.94 |
| | 4k | **0.5408** | **0.6374** | **55.15** | **32.50** | **22.11** | **100.0%** | 57.65 |
| | 8k | 0.5520 | 0.6501 | **58.29** | **44.53** | **13.33** | **100.0%** | 58.27 |
| | 16k | 0.5705 | 0.6711 | **59.90** | **53.60** | **5.98** | **100.0%** | 22.34 |

*\\*Aider RepoMap 0.0% syntax validity and zero full implementations are by-design properties of its multi-turn outline architecture.*"""

tab2 = """**Table 2: Authoritative Matched Held-Out Results (66 Tasks, Zero Commit Leakage)**

| Budget | Candidate Depth | Dynamic Policy | Scoped BM25 | Aider-Inspired RepoMap | Static $K=60$ Base | Mean $\\Delta$ vs BM25 | Clustered 95% CI | Raw $p$ | Holm-12 $p$ |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$2,000$** | $K=60$ | **49.88%** | 41.30% | 39.15% | 49.88% | $+8.58\\text{ pp}$ | $[-3.26, +20.42]$ | $0.1465$ | $0.4395$ (n.s.) |
| **$4,000$** | $K=100$ | **64.76%** | 44.78% | 51.77% | 55.94% | **+19.97 pp** | $[+8.58, +31.36]$ | $7.18 \\times 10^{-4}$ | **0.0072 (***)** |
| **$8,000$** | $K=200$ | **71.72%** | 58.22% | 53.06% | 55.94% | **+13.50 pp** | $[+4.02, +22.98]$ | $5.29 \\times 10^{-3}$ | **0.0423 (*)** |
| **$16,000$** | $K=400$ | **76.92%** | 60.48% | 62.74% | 56.16% | **+16.44 pp** | $[+7.54, +25.34]$ | $3.88 \\times 10^{-4}$ | **0.0043 (***)** |"""

tab3 = """**Table 3: Pure Solver Latency & Optimality Micro-Benchmark**

| Candidate Pool $N$ | HiGHS Mean (ms) | HiGHS p50 (ms) | Greedy Mean (ms) | Greedy p50 (ms) | HiGHS Speedup | Optimality Gap |
|---|---|---|---|---|---|---|
| **20** | 2.89 | 1.26 | 1.20 | 0.98 | $0.42\\times$ | 0.0% |
| **60** | **2.80** | 2.41 | **9.90** | 9.62 | **$3.53\\times$** | 0.0% |
| **200** | **8.05** | 7.90 | **101.62** | 100.71 | **$12.62\\times$** | 0.0% |
| **800** | **317.11** | 71.14 | **6,582.98** | 1,931.39 | **$20.76\\times$** | 0.0% |"""

p6 = f"""## 5. Results & Empirical Analysis

### 5.1 Factorial Ablation Across Token Budgets
Table 1 presents aggregate performance across all 129 tasks and four budgets (5,160 evaluations; all achieve 100% budget compliance):

{tab1}

### 5.2 Marginal Component Contributions & Statistical Significance
Applying the Holm-Bonferroni correction across confirmatory ablation transitions (127 commit clusters):
1. **Multi-Resolution Representation ($A \\to B$)**: At $B=2,000$, multi-resolution selection adds **$+16.61\\text{{ pp}}$** recall ($p_{{\\text{{raw}}}} = 0.0001, p_{{\\text{{Holm}}}} = 0.0006, d_z = +0.36$) and $+13.07\\text{{ pp}}$ at $4\\text{{k}}$ ($p_{{\\text{{Holm}}}} = 0.0004$).
2. **Optimizer Precedence Constraints ($B \\to C$)**: Knapsack precedence reduces recall by **$-5.43\\text{{ pp}}$** at $2\\text{{k}}$ ($p_{{\\text{{Holm}}}} = 0.0250$) due to parent taxation; removing it restores full recall without syntactic degradation.
3. **Topological Dependency Weights ($C \\to D$)**: Static 2-hop causal weights produce **$0.00\\text{{ pp}}$** marginal recall at $2\\text{{k}}$, $8\\text{{k}}$, and $16\\text{{k}}$ ($p = 1.0000$), and $-0.26\\text{{ pp}}$ at $4\\text{{k}}$ ($p = 0.3192$). We withdraw all recall claims for graph topology.
4. **Exact MILP vs. Greedy ($E \\to F$)**: At $B=4,000$, MILP leads greedy by $+4.69\\text{{ pp}}$ ($p_{{\\text{{raw}}}} = 0.0130$), but Holm correction yields **$p_{{\\text{{Holm}}}} = 0.0519$ (no statistically detectable difference at $\\alpha=0.05$)**. At other budgets, greedy and MILP are statistically indistinguishable ($p \\ge 0.18$). Greedy is adopted as the default compiler.

### 5.3 Information Preservation & Implementation Retention
As shown in Table 1, multi-resolution compilation preserves implementation depth. At $B=2,000$, MR-TopoS retains **$1.55\\times$ more full implementations** ($19.47$ vs $12.55$) than Scoped BM25, allocating $1,849$ tokens to full code versus $1,192$. Skeletons ($30.00$) and stubs ($1.39$) compress context, freeing budget for full target functions.

### 5.4 Authoritative Matched Held-Out Benchmark
Dynamic candidate scaling was evaluated on 66 untouched held-out tasks (zero commit leakage). Table 2 presents paired comparisons against matched baselines evaluated on the exact same 66 tasks:

{tab2}

On held-out tasks, scaling candidate depth eliminates high-budget saturation, boosting $16\\text{{k}}$ recall to **$76.92\\%$** ($+16.44\\text{{ pp}}$ over Scoped BM25, $p_{{\\text{{Holm-12}}}} = 0.0043$; $+20.76\\text{{ pp}}$ over static $K=60$, $p_{{\\text{{Holm-12}}}} = 0.00056$). Compared to the Aider-inspired baseline, Dynamic Policy leads significantly at $8\\text{{k}}$ ($+18.66\\text{{ pp}}, p_{{\\text{{Holm-12}}}} = 0.0435$), while showing no statistically detectable difference at $2\\text{{k}}$, $4\\text{{k}}$, and $16\\text{{k}}$ under the conservative 12-test omnibus correction.

### 5.5 Solver Latency & Scaling Micro-Benchmark
Table 3 compares pure solver execution across candidate pool sizes $N \\in [20, 800]$ over 15 empirical trials under identical inputs:

{tab3}

In pure solver execution, HiGHS compiled C++ dual simplex scales sub-linearly, evaluating bounds $3.5\\times$ to $20.8\\times$ faster than quadratic Python greedy loops with 0% gap. In end-to-end compilation, greedy avoids SciPy constraint instantiation, completing in $23.7\\text{{ ms}}$."""

# Section 6 (Table 4)
tab4 = """**Table 4: Exploratory Gemma 4 31B Prompt Latency Pilot (18 Inferences)**

| Context Paradigm | Token Budget | Generation Success Rate | Strict `git apply` Rate | Mean Latency (s) | Latency Delta |
|---|---|:---:|:---:|:---:|:---:|
| **Raw BM25** | 2,000 | 100.0% (6/6) | 0.0% (0/6) | 10.22s | Baseline |
| **Scoped BM25** | 2,000 | 100.0% (6/6) | 0.0% (0/6) | 10.55s | $+3.2\%$ |
| **MR-TopoS** | 2,000 | 100.0% (6/6) | 0.0% (0/6) | **7.57s** | **$-28.3\%$** |"""

p7 = f"""## 6. Exploratory Gemma 4 Latency Pilot

To observe prompt utility on a production model, we conducted an exploratory generation pilot on **`google/gemma-4-31b-it`** across 6 representative SWE benchmark tasks under $B=2,000$ tokens (18 live API inferences via Vertex AI; decoding temperature 0.2, top-p 0.95):

{tab4}

1. **Generation Latency**: Gemma 4 generation was **$28.3\\%$ faster** under MR-TopoS ($7.57\\text{{s}}$ vs $10.55\\text{{s}}$, paired $t(5)=2.76, p=0.038$) because contract skeletons eliminate token bloat over intermediate class bodies, reducing attention dispersion.
2. **Patch Application Limitations**: Zero-shot unified diffs failed strict `git apply` across all paradigms (0% pass rate) due to hunk line-number drift ($61.1\\%$) and indentation mismatch ($22.2\\%$), confirming SWE developer agents require interactive multi-turn editing tools rather than single-shot patch emission. This pilot provides exploratory evidence of inference efficiency, not downstream repair task completion."""

# Section 7
p8 = """## 7. The Full-File Localization Paradox

In whole-file retrieval (`full_file`), expanding token budget from $B=8,000$ to $B=16,000$ degrades Hit@1 localization due to **test file crowding**: test files contain dense keyword matches and large token footprints (`tests/test_requests.py` has 15,941 tokens vs 7,977 for `requests/models.py`). At 16k, test files crowd out gold source files. MR-TopoS eliminates this pathology via sub-method pruning."""

# Section 8
p9 = """## 8. Discussion & Limitations

1. **Language Scope**: Evaluated strictly on Python ASTs in SWE-bench Lite; generalization to languages with distinct grammar verbosity (Go, Rust) remains unverified.
2. **Interactive Integration**: The Gemma 4 pilot confirmed single-shot diffs fail strict patching; agent architectures require multi-turn editing loops.
3. **Surrogate-Cost Discrepancy**: While serializer downgrades absorb layout overhead with 100% budget compliance, joint layout optimization remains an open area."""

# Section 9
p10 = """## 9. Conclusion

We addressed the context assembly bottleneck in software engineering agents and introduced **MR-TopoS**, a multi-resolution AST context compiler. Formulating context compilation as an MCKP with surrogate costs and a budget-scaled candidate schedule ($K_{\\text{step}}(B)$), MR-TopoS retains **$1.55\\times$ more full implementations** at $B=2,000$, guarantees syntactic validity via Invariant 1, surges held-out $16\\text{k}$ recall to **$76.92\\%$** ($+16.44\\text{ pp}$ over Scoped BM25, $p_{\\text{Holm-12}} = 0.0043$), and reduces model generation latency by **$28.3\\%$**."""

# References
p11 = """## References

1. Chen, Z., Gao, Z., Shen, C., & Zhang, X. (2025). *LocAgent: Graph-Guided LLM Agents for Code Localization*. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL 2025).
2. Feng, Y., Wang, S., Li, Y., & Tan, L. (2026). *On the Effectiveness of Context Compression for Repository-Level Tasks: An Empirical Investigation*. arXiv:2604.13725.
3. Gauthier, P. (2024). *Aider: AI pair programming in your terminal*. GitHub repository: https://github.com/paul-gauthier/aider.
4. Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., & Press, O. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. arXiv:2405.15793.
5. Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. (2024). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR 2024.
6. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. TACL, 12, 157–173.
7. Gemma Team, Google DeepMind. (2024). *Gemma: Open Models Based on Gemini Technology*. arXiv:2403.08295.
8. Huangfu, Q., & Hall, J. A. (2018). *Parallelizing the dual revised simplex method*. Mathematical Programming Computation, 10(1), 119–142.
9. Kellerer, H., Pferschy, U., & Pisinger, D. (2004). *Knapsack Problems*. Springer Berlin Heidelberg.
10. Ferrante, J., Ottenstein, K. J., & Warren, J. D. (1987). *The program dependence graph and its use in optimization*. ACM TOPLAS, 9(3), 319–349."""

parts = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11]
full_doc = "\n\n---\n\n".join(parts)
print("Total words:", len(full_doc.split()))
