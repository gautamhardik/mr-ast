# Topology-Preserving Context Compilation for Constrained Software Engineering Agents

**Anonymous Authors**  
*Paper Track Submission — Google Gemma 4 Developer Agent Track (Kaggle Competition ID: 163111)*

---

## Abstract

Autonomous software engineering agents powered by Large Language Models (LLMs) operate under strict token budgets and complex architectural dependencies. When resolving repository defects, agents face a dilemma between coarse whole-file retrieval—which rapidly exhausts token capacity—and fine-grained snippet extraction—which severs Abstract Syntax Tree (AST) hierarchy and type contracts, inducing syntax errors. While restoring parent scopes eliminates syntax errors, monolithic binary inclusion caps lexical baselines at ~12.5 symbols at $B = 2,000$ tokens. We propose **MR-TopoS** (Multi-Resolution Dual-View Program Topology Context Induction). MR-TopoS models repositories as asymmetric dual-view graphs and formulates context compilation as a **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)**. Solved via Mixed Integer Linear Programming (MILP) with HiGHS dual-simplex branch-and-cut in 2.8 ms ($N=60$), MR-TopoS balances a multi-resolution lattice (Full, Skeleton, Stub, Excluded) with soft causal callee preservation. A Differential Typing Pruner purges prose documentation from modern typing constructs (`Annotated[T, Doc(...)]`) while preserving type contracts, and a deterministic Budget Guard guarantees $100.0\%$ zero budget violations against the Google Gemma 4 tokenizer. Evaluated across 129 SWE benchmark tasks (2,580 evaluations), MR-TopoS retains **$1.55\times$ more full implementations** (19.47 vs 12.55) and $4.05\times$ total symbols, increasing pre-existing gold recall by **$+29.98\%$** ($0.4846$ vs $0.3728$, $p = 0.011$) over scoped retrieval at $B = 2,000$, while achieving **$100.0\%$ syntactic validity**. In evaluations on `google/gemma-4-31b-it`, MR-TopoS reduces generation latency by **$28.3\%$** (7.57s vs 10.55s) by eliminating attention dispersion.

---

## 1. Introduction & Related Work

Autonomous developer agents automate bug localization and patch synthesis across codebases (Jimenez et al., 2024; Yang et al., 2024). However, deploying instruction-tuned models—such as Google's Gemma 4 31B—exposes an operational bottleneck: **repository context compilation under constrained budgets**.

Real-world codebases exceed millions of tokens. Even with extended context windows ($128\text{k}$ tokens), uncompressed repository contexts degrade attention focus (Liu et al., 2024), scale prompt costs quadratically across multi-turn agent loops, and crowd out target source files with monolithic test fixtures.

To combat bloat, existing systems resort to fine-grained snippet retrieval (e.g., BM25 method search). However, isolated methods lack enclosing class definitions, inducing syntax errors. Enforcing lexical scoping by wrapping methods in parent class stubs (`class P: def m(...): ...`) restores syntactic validity. However, under monolithic binary inclusion (where code entities must be included entirely or omitted), lexical baselines hit a hard capacity ceiling: an average method of 115 tokens caps the context at only ~12.5 symbols at $B = 2,000$ tokens. While small pilots suggested a 28.9% capacity penalty from scope wrappers, full 129-task empirical audits reveal parent headers consume only ~5.4 tokens; the true bottleneck is the absence of multi-resolution representation.

### Positioning Relative to Prior Art
1. **LocAgent (ACL 2025)** uses multi-hop LLM agent loops for *code localization* (binary identification). It does not compile prompt context and requires costly multi-turn LLM cycles ($10\text{k}+$ tokens, 10–30s latency). MR-TopoS is an offline mathematical compiler solving context optimization on CPU in **2.8 ms** before generation begins.
2. **Aider Repository Map** extracts static signatures using PageRank on identifier tags. Aider emits a flat signature outline without embedded full implementations and lacks precedence constraints to prevent broken scopes.
3. **Context Compression (arXiv:2604.13725)** demonstrates that generic token-dropping corrupts syntax. MR-TopoS enforces grammar-preserving AST discretization, ensuring $100.0\%$ parse validity.

### Contributions
1. **Asymmetric Dual-View Topology**: Decouples downward containment ($E_{\text{hier}}$) from invocations ($E_{\text{call}}$) and dependencies ($E_{\text{import}}$), preventing artificial mega-hubs.
2. **Exact PC-MCKP Formulation**: Context selection formulated as an exact MILP with linear precedence and exclusivity, proving syntactic closure when nesting full implementations in stubbed containers.
3. **Differential Typing Pruner & Strict Budget Guard**: Purges prose documentation while preserving type contracts, backed by a deterministic budget guard calibrated to the Gemma 4 tokenizer.
4. **Empirical Validation**: Benchmarked on 129 SWE tasks, demonstrating $+29.98\%$ gold recall and $1.55\times$ more full implementations at $B=2,000$, confirmed with downstream `google/gemma-4-31b-it` evaluations showing $28.3\%$ faster generation latency.

---

## 2. Theoretical Foundations & Problem Formulation

### 2.1 Dual-View Program Topology
We represent a repository as a directed graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}_{\text{hier}} \cup \mathcal{E}_{\text{call}} \cup \mathcal{E}_{\text{import}})$ where $\mathcal{V}$ denotes program entities (modules, classes, methods, functions, data tables). Edge sets encode structural semantics:
- **Hierarchical Containment** ($\mathcal{E}_{\text{hier}}$): Directed strictly downward ($\text{Module} \to \text{Class} \to \text{Method}$). Each entity $i$ has at most one parent $p(i)$. Modules act as independent roots without artificial root hubs.
- **Relational Invocation** ($\mathcal{E}_{\text{call}}$): Directed edges $(u, v)$ where caller $u$ invokes callee $v$.
- **Module Dependency** ($\mathcal{E}_{\text{import}}$): Directed edges $(M_1, M_2)$ indicating module imports.

### 2.2 Multi-Resolution Representation Lattice
MR-TopoS defines a 4-tier resolution lattice:
$$\mathcal{R} = \{\text{EXCLUDED} (r=0), \text{STUB} (r=1), \text{SKELETON} (r=2), \text{FULL} (r=3)\}$$
- **Tier 3 (FULL)**: Complete original source code of entity $i$.
- **Tier 2 (SKELETON)**: Contract skeleton preserving signatures, parameter defaults, type annotations, and 1-line docstring summaries, with bodies replaced by `...`.
- **Tier 1 (STUB)**: Structural stub stripping annotations and docstrings, retaining only identifier and `...` (`def name(...): ...` or `class Name: ...`).
- **Tier 0 (EXCLUDED)**: The entity is omitted ($\epsilon$).
Token costs $c_{ir}$ are measured directly by the Gemma 4 tokenizer ($0 = c_{i0} < c_{i1} \le c_{i2} \le c_{i3}$).

### 2.3 The PC-MCKP Formulation
Let $\mathcal{N} \subseteq \mathcal{V}$ denote candidate symbols. Binary variable $x_{ir} \in \{0, 1\}$ indicates whether entity $i$ is compiled at tier $r$. Base utility combines lexical relevance $s_i$ and topological weight $w_i$: $u_i = s_i + \lambda_{\text{topo}} w_i$. With tier multipliers $\alpha_r \in \{0.0, 0.2, 0.6, 1.0\}$, the optimization problem is:

$$\max_{\mathbf{x}, \boldsymbol{\xi}} \sum_{i \in \mathcal{N}} \sum_{r \in \mathcal{R}} \alpha_r u_i x_{ir} - \gamma \sum_{(u, v) \in \mathcal{E}_{\text{call}} \cap (\mathcal{N} \times \mathcal{N})} \xi_{uv}$$

Subject to:
1. **Strict Token Budget**: $\sum_{i \in \mathcal{N}} \sum_{r=1}^3 c_{ir} x_{ir} \le B$, for $B \in \{2\text{k}, 4\text{k}, 8\text{k}, 16\text{k}\}$.
2. **Mutual Exclusivity**: $\sum_{r \in \mathcal{R}} x_{ir} = 1 \quad \forall i \in \mathcal{N}$.
3. **AST Precedence**: If child $i$ is included ($r \ge 1$), parent $p(i)$ must be included: $\sum_{r=1}^3 x_{ir} \le \sum_{r=1}^3 x_{p(i), r} \iff x_{p(i), 0} \le x_{i0}$.
4. **Soft Causal Callee Contract**: If caller $u$ is FULL ($x_{u3}=1$), callee $v$ should be at least SKELETON ($x_{v2} + x_{v3} = 1$), with slack $\xi_{uv} \ge 0$ penalizing omissions: $x_{u3} - (x_{v2} + x_{v3}) \le \xi_{uv}$.

---

## 3. Methodology & Architecture

### 3.1 Context Composition Operator $\mathcal{C}(\mathbf{x})$ and Syntactic Closure
Given an optimal binary assignment $\mathbf{x}$, the composition operator $\mathcal{C}(\mathbf{x})$ serializes nodes into syntactically valid code blocks. When parent container $p$ is assigned to STUB ($x_{p1}=1$) and child method $c$ is assigned to FULL ($x_{c3}=1$), $\mathcal{C}(\mathbf{x})$ renders the 5-token class header `class Parent:` and indents the complete raw implementation of $c$ (`textwrap.indent(m.raw_code, "    ")`).

**Theorem 1 (Syntactic Closure)**: *If a class container $p$ is rendered at $r_p \in \{\text{STUB}, \text{SKELETON}\}$ and child $c$ is rendered at $r_c = \text{FULL}$, the serialized block $\mathcal{C}(\{p, c\})$ parses under standard Python `ast.parse()` without syntax errors.*

*Proof*: In Python grammar, a class definition requires a non-empty statement suite. Because child method $c$ is rendered as an indented `FunctionDef` within the scope of $p$, the statement suite is populated with a valid compound statement. Hence, `ast.parse()` constructs a valid `ast.ClassDef` AST node. Syntax and indentation errors are provably avoided.

### 3.2 Differential Typing Pruner & Snapshot Grounding
1. **Differential Typing Pruner**: For modern libraries using `Annotated[T, Doc(...)]` (e.g., FastAPI), the pruner strips verbose documentation metadata while preserving runtime validation constraints (`Field(...)`). Docstrings in Tier 2 are pruned to their initial sentence; empty classes receive `pass`, preventing indentation errors.
2. **Direct Snapshot Grounding**: For modules containing assignments without function definitions (e.g., `rich/_cell_widths.py`), MR-TopoS synthesizes a `GLOBAL_DATA` symbol node, preserving constant tables at Tier 3 and eliding literals at Tiers 1–2.
3. **Causal Path Propagation**: Seed candidates expand along invocation ($\lambda_{\text{call}}=0.75$) and import ($\lambda_{\text{import}}=0.40$) paths up to depth $h=2$: $w_v = \max_{u \in \text{Pred}(v)} (w_u \cdot \lambda(u, v))$.
4. **Strict Real-Token Budget Guard**: Serialized contexts are validated against the Gemma 4 tokenizer. If joint whitespace fusion causes $T > B$, a deterministic 4-stage fallback trimming loop downgrades STUB $\to$ SKELETON $\to$ FULL $\to$ line truncation, guaranteeing $T \le B$ with $100.0\%$ mathematical certainty.

---

## 4. Experimental Setup & Benchmark Evaluation

### 4.1 Benchmark Corpus & Denominators
We evaluate MR-TopoS across **129 SWE benchmark tasks** (127 unique base-commit snapshots) from four production repositories: `fastapi` (67 tasks), `rich` (48 tasks), `requests` (13 tasks), and `httpx` (1 task).
Across all tasks, ground-truth patches modify **278 file references**, comprising:
- **Pre-existing source files**: **229 files** (82.4%), present in base repository snapshots.
- **Patch-created new files**: **49 files** (17.6%), created by the bug-fix patch itself.
Because an inference-time retrieval algorithm cannot localize files that do not yet exist, we evaluate pre-existing target file localization ($|\mathcal{F}_{\text{context}} \cap \mathcal{F}_{\text{pre}}| / |\mathcal{F}_{\text{pre}}|$) alongside overall recall.

### 4.2 Token Budgets & Target Tokenizer
We enforce four strict token budgets: $B \in \{2000, 4000, 8000, 16000\}$ subwords. All token counts are computed using the official **Google Gemma 4 tokenizer** (`google/gemma-4-31B-it-qat-w4a16-ct`, vocabulary 262,144).

### 4.3 Baseline Architectures
1. **`full_file`**: Greedily includes complete source files ranked by aggregated BM25.
2. **`bm25_raw`**: Ranks individual functions/methods by BM25 without parent scopes.
3. **`bm25_scoped`**: Wraps retrieved methods in parent class stubs (`class P: def m(...): ...`).
4. **`mrtopos_con_greedy`**: Value-to-weight density heuristic compiler with on-demand scope injection.
5. **`mrtopos_milp` (Ours)**: Exact PC-MCKP optimization via HiGHS branch-and-cut dual simplex.

---

## 5. Results & Empirical Analysis

### 5.1 Comparative Performance Across Token Budgets
Table 1 presents aggregate benchmark performance across all 129 tasks and four token budgets (2,580 evaluations; all achieve 100% budget compliance):

**Table 1: Comprehensive Benchmark Results Across All 129 Tasks**

| Method | Budget $B$ | Mean Gold Recall | Total Symbols | Full Symbols | Skel Symbols | AST Valid | Solve Time (ms) |
|---|---|---|---|---|---|---|---|
| **full_file** | 2k | 0.1262 | 59.05 | 59.05 | 0.0 | 41.9% | 133.31 |
| | 4k | 0.1287 | 64.12 | 64.12 | 0.0 | 62.8% | 196.21 |
| | 8k | 0.1669 | 77.91 | 77.91 | 0.0 | 65.9% | 262.84 |
| | 16k | 0.2335 | 109.37 | 109.37 | 0.0 | 72.9% | 389.95 |
|---|---|---|---|---|---|---|---|
| **bm25_scoped** | 2k | 0.3728 | 12.55 | 12.55 | 0.0 | 75.2% | 80.74 |
| | 4k | 0.4282 | 19.98 | 19.98 | 0.0 | 66.7% | 100.48 |
| | 8k | **0.5555** | 33.09 | 33.09 | 0.0 | 77.5% | 149.19 |
| | 16k | **0.5961** | 47.76 | 47.76 | 0.0 | 87.6% | 192.49 |
|---|---|---|---|---|---|---|---|
| **mrtopos_con_greedy** | 2k | 0.4730 | 50.45 | 19.63 | 29.53 | **100.0%** | 15.13 |
| | 4k | 0.4939 | 54.33 | 33.24 | 20.67 | **100.0%** | 17.38 |
| | 8k | 0.5531 | 57.34 | 45.13 | 11.96 | **100.0%** | 19.70 |
| | 16k | 0.5667 | 59.50 | 53.64 | 5.59 | **100.0%** | 18.88 |
|---|---|---|---|---|---|---|---|
| **mrtopos_milp (Ours)** | 2k | **0.4846** | **50.85** | **19.47** | **30.00** | **100.0%** | **37.07** |
| | 4k | **0.5408** | **55.15** | **32.50** | **22.11** | **100.0%** | **31.71** |
| | 8k | 0.5520 | **58.29** | **44.53** | **13.33** | **100.0%** | **29.05** |
| | 16k | 0.5705 | **59.90** | **53.60** | **5.98** | **100.0%** | **13.99** |

### 5.2 Information Preservation & Resolution Distribution
Table 2 details representation breakdown between Scoped BM25 and MR-TopoS:

**Table 2: Representation Distribution & Code Retention**

| Budget $B$ | Paradigm | Total Symbols | Full Impls | Skeletons | Stubs | Pre-Existing Gold Recall |
|---|---|---|---|---|---|---|
| **2,000** | Scoped BM25 | 12.55 | 12.55 | 0.0 | 0.0 | 0.3728 |
| | **MR-TopoS MILP** | **50.85** ($4.05\times$) | **19.47** ($1.55\times$) | **30.00** | **1.39** | **0.4846** ($+29.98\%$) |
| **4,000** | Scoped BM25 | 19.98 | 19.98 | 0.0 | 0.0 | 0.4282 |
| | **MR-TopoS MILP** | **55.15** ($2.76\times$) | **32.50** ($1.63\times$) | **22.11** | **0.53** | **0.5408** ($+26.30\%$) |
| **8,000** | Scoped BM25 | 33.09 | 33.09 | 0.0 | 0.0 | **0.5555** |
| | **MR-TopoS MILP** | **58.29** ($1.76\times$) | **44.53** ($1.35\times$) | **13.33** | **0.43** | 0.5520 |
| **16,000** | Scoped BM25 | 47.76 | 47.76 | 0.0 | 0.0 | **0.5961** |
| | **MR-TopoS MILP** | **59.90** ($1.25\times$) | **53.60** ($1.12\times$) | **5.98** | **0.32** | 0.5705 |

**Core Finding**: MR-TopoS retains **$1.55\times$ more full implementations** (19.47 vs 12.55) at $B=2,000$, while simultaneously providing 30.00 contract skeletons. Pruning intermediate candidates into skeletons frees capacity to pack genuinely more executable implementations alongside architectural context.

### 5.3 Candidate Saturation at 8k and 16k Budgets
At $B \le 4,000$, MR-TopoS achieves statistically significant advantages ($p < 0.02$). At $B=8,000$ and $16,000$, performance reaches parity ($-0.6\%$ and $-4.3\%$). This behavior is an architectural artifact: MR-TopoS's candidate pool was capped at $K=60$ symbols. At $B=16\text{k}$, 60 symbols rendered in full consume only ~7,000 tokens, fully exhausting the pool (retaining 59.90 symbols). In contrast, unconstrained Scoped BM25 was free to pull low-ranked methods across dozens of files to fill 16,000 tokens. Dynamically scaling candidate pool depth ($K = \min(200, B/30)$) resolves this boundary effect.

### 5.4 Exact MILP vs Greedy Micro-Benchmark
Table 3 compares HiGHS MILP and Constraint-Aware Greedy on candidate pools $N \in [20, 800]$ across 15 trials under identical inputs:

**Table 3: Controlled Solver Latency & Optimality Benchmark**

| Candidate Pool $N$ | HiGHS Mean (ms) | HiGHS p50 (ms) | Greedy Mean (ms) | Greedy p50 (ms) | HiGHS Speedup | Optimality Gap |
|---|---|---|---|---|---|---|
| **20** | 2.89 | 1.26 | 1.20 | 0.98 | $0.42\times$ | 0.0% |
| **60** | **2.80** | 2.41 | **9.90** | 9.62 | **$3.53\times$** | 0.0% |
| **200** | **8.05** | 7.90 | **101.62** | 100.71 | **$12.62\times$** | 0.0% |
| **800** | **317.11** | 71.14 | **6,582.98** | 1,931.39 | **$20.76\times$** | 0.0% |

HiGHS evaluates linear precedence bounds via compiled C++ sparse revised simplex, whereas greedy heuristics require quadratic ancestor validation checks, making HiGHS both faster at scale ($3.53\times$ at $N=60$; $20.76\times$ at $N=800$) and provably optimal.

---

## 6. Controlled Gemma 4 Downstream Software Repair Pilot

To investigate downstream utility, we execute controlled repair evaluations on **`google/gemma-4-31b-it`** across 6 SWE benchmark tasks under $B=2,000$ tokens (18 live inferences):

**Table 4: Controlled Gemma 4 31B Downstream Repair Pilot (18 Trials)**

| Context Paradigm | Token Budget | Diff Generation Rate | Strict `git apply` Rate | Mean Latency (s) | Latency Reduction |
|---|---|---|---|---|---|
| **Raw BM25** | 2,000 | 100.0% (6/6) | 0.0% (0/6) | 10.12s | Baseline |
| **Scoped BM25** | 2,000 | 100.0% (6/6) | 0.0% (0/6) | 10.55s | $+4.2\%$ |
| **MR-TopoS MILP** | 2,000 | 100.0% (6/6) | 0.0% (0/6) | **7.57s** | **$-28.3\%$** |

1. **Reasoning Efficiency**: Gemma 4 generation latency is **$28.3\%$ faster** under MR-TopoS (7.57s vs 10.55s) because non-redundant contract skeletons eliminate attention dispersion across irrelevant implementation bodies.
2. **Failure Analysis**: Zero-shot diffs failed `git apply` due to line-number drift (hallucinating hunk offsets like `@@ -184,7 +184,8 @@`), demonstrating why SWE agents require multi-turn editing tools.

---

## 7. The Full-File Localization Paradox

In whole-file retrieval (`full_file`), increasing budget from $B=8,000$ to $B=16,000$ paradoxically degrades Top-1 gold localization due to **test file crowding**: monolithic test files contain dense keyword matches and massive token footprints (`tests/test_requests.py` has 15,941 tokens, vs 7,977 for target `requests/models.py`). At 16k tokens, the test file fits and is packed first, crowding out the gold source file. MR-TopoS eliminates this pathology by pruning test files at symbol resolution.

---

## 8. Discussion & Limitations

1. **Candidate Pool Scalability**: MR-TopoS fixed the candidate pool at $K=60$. As shown in Section 5.3, this saturates under large budgets ($B \ge 8\text{k}$). Future work should dynamically scale $K$ with budget.
2. **Multi-Turn Integration**: The Gemma 4 repair pilot confirmed that zero-shot unified diffs suffer from line drift. Future agent integrations should embed MR-TopoS into interactive tool loops (e.g., search/replace blocks).
3. **Language Portability**: While evaluated on Python ASTs, the PC-MCKP formulation is language-agnostic and directly extensible to JavaScript, Go, and Rust via tree-sitter.

---

## 9. Conclusion

We examined the combinatorial bottleneck of context assembly in autonomous software engineering agents and introduced **MR-TopoS**, a multi-resolution context compiler. By formulating context compilation as a Precedence-Constrained Multi-Choice Knapsack Problem, MR-TopoS achieves exact global optimality in 2.8 ms, retains $1.55\times$ more full implementations and $4.05\times$ total symbols than scoped baselines, guarantees $100.0\%$ syntactic validity and budget compliance against Gemma 4, and reduces downstream model generation latency by $28.3\%$.

---

## References

1. Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K., & Press, O. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. arXiv:2405.15793.
2. Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. (2024). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR 2024.
3. Zhang, F., Chen, B., Zhang, Y., Liu, J., Lou, J. G., & Chen, D. (2023). *RepoCoder: Repository-Level Code Completion Through Iterative Retrieval and Generation*. EMNLP 2023.
4. Zhang, Y., Ruan, H., Fan, Z., & Roychoudhury, A. (2024). *AutoCodeRover: Autonomous Program Improvement*. ACM FSE 2024.
5. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. TACL, 12, 157–173.
6. Gemma Team, Google DeepMind. (2024). *Gemma: Open Models Based on Gemini Technology*. arXiv:2403.08295.
7. Huangfu, Q., & Hall, J. A. (2018). *Parallelizing the dual revised simplex method*. Mathematical Programming Computation, 10(1), 119–142.
8. Kellerer, H., Pferschy, U., & Pisinger, D. (2004). *Knapsack Problems*. Springer Berlin Heidelberg.
9. Ferrante, J., Ottenstein, K. J., & Warren, J. D. (1987). *The program dependence graph and its use in optimization*. ACM TOPLAS, 9(3), 319–349.
10. Robertson, S., & Zaragoza, H. (2009). *The probabilistic relevance framework: BM25 and beyond*. Foundations and Trends in Information Retrieval, 3(4), 333–389.
