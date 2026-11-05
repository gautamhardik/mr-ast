import re

def streamline():
    with open("paper/final_submission_candidate.md", "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Section 1 Intro & Positioning & Contributions
    old_sec1 = """Autonomous developer agents automate bug localization and patch synthesis across codebases (Jimenez et al., 2024; Yang et al., 2024). However, deploying instruction-tuned models—such as Google's Gemma 4 31B—exposes an operational bottleneck: **repository context compilation under constrained budgets**. Real-world codebases exceed millions of tokens; uncompressed contexts degrade attention focus (Liu et al., 2024), scale prompt costs quadratically across agent loops, and crowd out target source files with monolithic test fixtures.

Existing systems resort to fine-grained snippet retrieval (e.g., BM25 method search). However, isolated methods lack enclosing class definitions, inducing syntax errors. Enforcing lexical scoping by wrapping methods in parent class stubs (`class P: def m(...): ...`) restores syntactic validity. However, under monolithic binary inclusion, lexical baselines hit a hard capacity ceiling: an average method of 115 tokens caps context at ~12.5 symbols at $B = 2,000$ tokens. While small pilots suggested a 28.9% capacity penalty from scope wrappers, full 129-task empirical audits reveal parent headers consume only ~5.4 tokens; the true bottleneck is the absence of multi-resolution representation.

### Positioning Relative to Prior Art
1. **LocAgent (ACL 2025)** addresses bug localization through iterative agent exploration, using an LLM policy to navigate a heterogeneous code graph across multiple turns (Wang et al., 2025). In contrast, MR-TopoS operates as an offline context compiler, executing exact mathematical optimization on CPU before agent inference begins.
2. **Aider Repository Map** extracts Tree-sitter tags and applies personalized PageRank conditioned on chat context to construct a flat signature outline within a token budget (Gauthier, 2024), providing candidate files separately. MR-TopoS solves a unified PC-MCKP that nests full implementations directly inside skeletonized class containers.
3. **Context Compression (EMNLP 2023; arXiv:2604.13725)** demonstrates prompt compression in natural language by pruning tokens using perplexity or entropy (Li et al., 2023; Jiang et al., 2023). However, in code syntax, token dropping risks severing indentation and delimiter integrity. MR-TopoS performs discrete, grammar-preserving AST transformations, guaranteeing 100.0% parse validity.

### Contributions
1. **Asymmetric Dual-View Topology**: An AST graph decoupling downward containment ($E_{\\text{hier}}$) from invocations ($E_{\\text{call}}$) and dependencies ($E_{\\text{import}}$), eliminating synthetic root hubs.
2. **Exact PC-MCKP Formulation & Composition Operator**: Context selection formulated as an exact MILP with linear precedence and exclusivity, proving syntactic closure when nesting full implementations inside stubbed parent containers.
3. **Differential Typing Pruner & Strict Budget Guard**: Purges prose documentation while preserving type contracts, backed by a deterministic budget guard calibrated to the official Gemma 4 tokenizer.
4. **Empirical & Downstream Validation**: Benchmarked across 129 SWE tasks, demonstrating $+29.98\\%$ gold recall improvement and $1.55\\times$ more full implementations at $B=2,000$, confirmed with downstream `google/gemma-4-31b-it` evaluations showing $28.3\\%$ faster generation latency."""

    new_sec1 = """Autonomous developer agents automate bug localization and repair across codebases (Jimenez et al., 2024; Yang et al., 2024). However, deploying models like Google's Gemma 4 31B exposes an operational bottleneck: **context compilation under constrained budgets**. Real-world repositories exceed millions of tokens; uncompressed contexts degrade attention focus (Liu et al., 2024), inflate inference costs quadratically, and crowd out target source files.

Snippet retrieval (e.g., BM25) extracts isolated methods but severs enclosing scopes, causing syntax errors. Enclosing methods in class stubs (`class P: def m(...): ...`) restores syntax, but monolithic binary inclusion hits a capacity ceiling: an average method of 115 tokens caps context at ~12.5 symbols at $B = 2,000$ tokens. While small pilots suggested a 28.9% penalty from scope wrappers, full 129-task empirical audits reveal class headers consume only ~5.4 tokens; the true bottleneck is the absence of multi-resolution representation.

### Positioning Relative to Prior Art
1. **LocAgent (ACL 2025)** navigates code graphs iteratively using multi-hop LLM agent turns (Wang et al., 2025). MR-TopoS is an offline, zero-turn compiler executing exact optimization on CPU before generation begins.
2. **Aider Repository Map** applies PageRank conditioned on chat state to emit flat signature outlines, retrieving files separately (Gauthier, 2024). MR-TopoS solves a unified PC-MCKP nesting full implementations inside skeletonized class containers.
3. **Context Compression (EMNLP 2023; arXiv:2604.13725)** prunes tokens via perplexity or entropy in natural language (Li et al., 2023; Jiang et al., 2023). In formal code syntax, token-dropping severs indentation and delimiters; MR-TopoS enforces grammar-preserving AST transformations, ensuring 100% parse validity.

### Contributions
1. **Asymmetric Dual-View Topology**: Decouples downward containment ($E_{\\text{hier}}$) from invocations ($E_{\\text{call}}$) and dependencies ($E_{\\text{import}}$), preventing synthetic root hubs.
2. **Exact PC-MCKP Formulation**: Models context compilation as an exact MILP with linear precedence and exclusivity, proving syntactic closure when nesting full methods in stubbed classes.
3. **Differential Typing Pruner & Strict Budget Guard**: Purges prose documentation while preserving type contracts, backed by a deterministic budget guard calibrated to the Gemma 4 tokenizer.
4. **Empirical Validation**: Benchmarked across 129 SWE tasks, demonstrating $+29.98\\%$ gold recall and $1.55\\times$ more full implementations at $B=2,000$, confirmed with downstream `google/gemma-4-31b-it` evaluations showing $28.3\\%$ faster latency."""

    text = text.replace(old_sec1, new_sec1)

    # 2. Section 2.3 PC-MCKP
    old_sec23 = """Let $\\mathcal{N} \\subseteq \\mathcal{V}$ denote candidate symbols. Binary variable $x_{ir} \\in \\{0, 1\\}$ indicates whether entity $i$ is compiled at tier $r$. Base utility combines lexical relevance $s_i$ and topological weight $w_i$: $u_i = s_i + \\lambda_{\\text{topo}} w_i$. With tier multipliers $\\alpha_r \\in \\{0.0, 0.2, 0.6, 1.0\\}$, context compilation is formulated as a Precedence-Constrained Multi-Choice Knapsack Problem (Kellerer et al., 2004):

$$\\max_{\\mathbf{x}, \\boldsymbol{\\xi}} \\sum_{i \\in \\mathcal{N}} \\sum_{r \\in \\mathcal{R}} \\alpha_r u_i x_{ir} - \\gamma \\sum_{(u, v) \\in \\mathcal{E}_{\\text{call}} \\cap (\\mathcal{N} \\times \\mathcal{N})} \\xi_{uv}$$

Subject to:
1. **Strict Token Budget**: $\\sum_{i \\in \\mathcal{N}} \\sum_{r=1}^3 c_{ir} x_{ir} \\le B$, for $B \\in \\{2\\text{k}, 4\\text{k}, 8\\text{k}, 16\\text{k}\\}$.
2. **Mutual Exclusivity**: $\\sum_{r \\in \\mathcal{R}} x_{ir} = 1 \\quad \\forall i \\in \\mathcal{N}$.
3. **AST Precedence**: If child $i$ is included ($r \\ge 1$), parent $p(i)$ must be included: $\\sum_{r=1}^3 x_{ir} \\le \\sum_{r=1}^3 x_{p(i), r} \\iff x_{p(i), 0} \\le x_{i0}$.
4. **Soft Causal Callee Contract**: If caller $u$ is FULL ($x_{u3}=1$), callee $v$ should be at least SKELETON ($x_{v2} + x_{v3} = 1$), with slack $\\xi_{uv} \\ge 0$ penalizing omissions: $x_{u3} - (x_{v2} + x_{v3}) \\le \\xi_{uv}$."""

    new_sec23 = """Let $\\mathcal{N} \\subseteq \\mathcal{V}$ denote candidate symbols. Binary variable $x_{ir} \\in \\{0, 1\\}$ indicates whether entity $i$ is rendered at tier $r$. Base utility combines lexical relevance $s_i$ and topological weight $w_i$: $u_i = s_i + \\lambda_{\\text{topo}} w_i$. With tier weights $\\alpha_r \\in \\{0.0, 0.2, 0.6, 1.0\\}$, compilation is formulated as a PC-MCKP instance (Kellerer et al., 2004):

$$\\max_{\\mathbf{x}, \\boldsymbol{\\xi}} \\sum_{i \\in \\mathcal{N}} \\sum_{r \\in \\mathcal{R}} \\alpha_r u_i x_{ir} - \\gamma \\sum_{(u, v) \\in \\mathcal{E}_{\\text{call}} \\cap (\\mathcal{N} \\times \\mathcal{N})} \\xi_{uv}$$

Subject to:
1. **Budget**: $\\sum_{i \\in \\mathcal{N}} \\sum_{r=1}^3 c_{ir} x_{ir} \\le B$, for $B \\in \\{2\\text{k}, 4\\text{k}, 8\\text{k}, 16\\text{k}\\}$.
2. **Exclusivity**: $\\sum_{r \\in \\mathcal{R}} x_{ir} = 1 \\quad \\forall i \\in \\mathcal{N}$.
3. **AST Precedence**: $\\sum_{r=1}^3 x_{ir} \\le \\sum_{r=1}^3 x_{p(i), r} \\iff x_{p(i), 0} \\le x_{i0}$.
4. **Callee Contract**: Caller $u$ at FULL requires callee $v$ at least SKELETON ($x_{u3} - (x_{v2} + x_{v3}) \\le \\xi_{uv}$)."""

    text = text.replace(old_sec23, new_sec23)

    # 3. Section 3.1 & 3.2 Methodology
    old_sec3 = """Given binary assignment $\\mathbf{x}$, composition operator $\\mathcal{C}(\\mathbf{x})$ serializes nodes into syntactically valid code blocks. When parent container $p$ is assigned to STUB ($x_{p1}=1$) and child method $c$ is assigned to FULL ($x_{c3}=1$), $\\mathcal{C}(\\mathbf{x})$ renders the 5-token class header `class Parent:` and indents the complete raw implementation of $c$ (`textwrap.indent(m.raw_code, "    ")`).

**Theorem 1 (Syntactic Closure)**: *Let $\\mathcal{C}(\\mathbf{x})$ be the serialized context under decision matrix $\\mathbf{x}$. Assuming the base repository parses under `ast.parse()`, that AST precedence holds ($x_{p(i),0} \\le x_{i0}$), and that empty containers render a statement suite (`pass`), then $\\mathcal{C}(\\mathbf{x})$ parses under standard Python `ast.parse()` without `SyntaxError` or `IndentationError`.*

*Proof*: In Python grammar, class definition requires a non-empty statement suite. If child method $c$ is rendered as an indented `FunctionDef` within the scope of $p$, the suite contains a valid compound statement. For multiple children $(c_1, \\dots, c_k)$, nested classes, and decorated methods, relative 4-space indentation is uniformly applied. Hence, `ast.parse()` constructs a valid AST. Syntactic closure holds.

*Syntactic Validity vs. Semantic Preservation*: Syntactic closure guarantees that compiled context is grammatically valid code. It does not imply runtime behavioral equivalence: replacing unselected bodies with `...` alters execution semantics. The compiled string functions as an information-dense prompt representation, not an executable binary.

### 3.2 Differential Typing Pruner & Snapshot Grounding
1. **Differential Typing Pruner**: For modern typing constructs (`Annotated[T, Doc(...)]`), the pruner strips verbose documentation strings while preserving base type $T$ and runtime validation rules (`Field(...)`). Docstrings in Tier 2 are condensed to their initial summary sentence; empty class bodies receive `pass`, preventing `IndentationError`.
2. **Direct Snapshot Grounding**: For modules containing assignments without function definitions (e.g., `rich/_cell_widths.py`), MR-TopoS synthesizes a `GLOBAL_DATA` symbol node, preserving constant tables at Tier 3 and eliding literals at Tiers 1–2.
3. **Causal Path Propagation**: Seed candidates expand along invocation ($\\lambda_{\\text{call}}=0.75$) and import ($\\lambda_{\\text{import}}=0.40$) paths up to depth $h=2$: $w_v = \\max_{u \\in \\text{Pred}(v)} (w_u \\cdot \\lambda(u, v))$.
4. **Strict Real-Token Budget Guard**: Serialized contexts are validated against the Gemma 4 tokenizer. If subword boundary effects across file banners cause joint size to exceed budget ($T > B$), a deterministic fallback trimming loop monotonically reduces entity resolutions in ascending order of (tier, utility)—pruning STUBs to omission, SKELETONs to STUBs, and FULL implementations to SKELETONs—with bottom-line truncation as a strict fail-safe, guaranteeing $T \\le B$ with $100.0\\%$ zero violations."""

    new_sec3 = """Given assignment $\\mathbf{x}$, composition operator $\\mathcal{C}(\\mathbf{x})$ renders nodes into valid code blocks. When parent class $p$ is STUB ($x_{p1}=1$) and child method $c$ is FULL ($x_{c3}=1$), $\\mathcal{C}(\\mathbf{x})$ renders header `class Parent:` and indents method $c$ (`textwrap.indent(m.raw_code, "    ")`).

**Theorem 1 (Syntactic Closure)**: *Let $\\mathcal{C}(\\mathbf{x})$ be the context under assignment $\\mathbf{x}$. Assuming the base snapshot parses under `ast.parse()`, AST precedence holds ($x_{p(i),0} \\le x_{i0}$), and empty containers render `pass`, then $\\mathcal{C}(\\mathbf{x})$ parses under standard Python `ast.parse()` without syntax errors.*

*Proof*: Python class definitions require a non-empty suite. Rendering child method $c$ as an indented `FunctionDef` within $p$ supplies a valid compound statement. For multiple children $(c_1, \\dots, c_k)$, nested classes, and decorators, relative 4-space indentation is preserved. Hence, `ast.parse()` constructs a valid AST. Syntactic closure holds.

*Syntactic Validity vs. Semantic Preservation*: Syntactic closure guarantees grammatically valid code. It does not imply runtime behavioral equivalence: replacing unselected bodies with `...` alters execution semantics. The compiled string functions as an information-dense prompt, not an executable binary.

### 3.2 Differential Typing Pruner & Snapshot Grounding
1. **Differential Typing Pruner**: For `Annotated[T, Doc(...)]`, the pruner strips prose documentation while preserving base type $T$ and validation rules (`Field(...)`). Docstrings in Tier 2 are condensed to one summary sentence; empty class bodies receive `pass`.
2. **Snapshot Grounding**: For modules with assignments without functions (e.g., `rich/_cell_widths.py`), MR-TopoS synthesizes a `GLOBAL_DATA` node, preserving lookup tables at Tier 3 and eliding literals at Tiers 1–2.
3. **Causal Path Propagation**: Seed candidates expand along invocation ($\\lambda_{\\text{call}}=0.75$) and import ($\\lambda_{\\text{import}}=0.40$) paths to depth $h=2$: $w_v = \\max_{u \\in \\text{Pred}(v)} (w_u \\cdot \\lambda(u, v))$.
4. **Strict Budget Guard**: Serialized contexts are validated against the Gemma 4 tokenizer. If boundary effects across banners cause $T > B$, a deterministic fallback loop reduces resolutions in ascending order of (tier, utility)—pruning STUBs to omission, SKELETONs to STUBs, and FULL implementations to SKELETONs—with bottom-line truncation as a fail-safe, guaranteeing $T \\le B$ with $100.0\\%$ zero violations."""

    # 4. Abstract tightening (trim ~35 words)
    old_abstract = """Autonomous software engineering agents operate under strict token budgets and complex architectural dependencies. When resolving repository defects, agents face a dilemma between coarse whole-file retrieval—which rapidly saturates token capacity—and fine-grained snippet extraction—which severs Abstract Syntax Tree (AST) hierarchy and type contracts, inducing syntax errors. While restoring parent scopes eliminates syntax errors, monolithic binary inclusion forces an all-or-nothing trade-off that caps lexical baselines at ~12.5 symbols at $B = 2,000$ tokens. We propose **MR-TopoS** (Multi-Resolution Dual-View Program Topology Context Induction). MR-TopoS models repositories as asymmetric dual-view graphs and formulates context compilation as a **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)**. Solved via Mixed Integer Linear Programming (MILP) with HiGHS dual-simplex branch-and-cut in 2.8 ms ($N=60$), MR-TopoS dynamically balances a multi-resolution lattice (Full, Skeleton, Stub, Excluded) with soft causal callee preservation. A Differential Typing Pruner purges prose documentation from modern typing constructs (`Annotated[T, Doc(...)]`) while preserving type contracts, and a deterministic Budget Guard guarantees $100.0\%$ zero budget violations against the 262,144-vocabulary Google Gemma 4 tokenizer. Evaluated across 129 SWE benchmark tasks (2,580 evaluations), MR-TopoS retains **$1.55\times$ more full implementations** (19.47 vs 12.55) and $4.05\times$ total symbols, increasing macro target file recall across all patch references by **$+29.98\%$** ($0.4846$ vs $0.3728$, $p = 0.011$) and pre-existing gold recall by **$+30.95\%$** ($0.5087$ vs $0.3885$, $p = 0.007$) over scoped retrieval at $B = 2,000$, while achieving **$100.0\%$ syntactic validity**. In evaluations on `google/gemma-4-31b-it`, MR-TopoS reduces generation latency by **$28.3\%$** (7.57s vs 10.55s, $p = 0.038$) by presenting structured contracts rather than unpruned class implementations."""

    new_abstract = """Autonomous software engineering agents operate under strict token budgets and architectural dependencies. When resolving repository defects, agents face a dilemma between coarse whole-file retrieval—which rapidly saturates token capacity—and fine-grained snippet extraction—which severs Abstract Syntax Tree (AST) hierarchy, inducing syntax errors. While restoring parent scopes eliminates syntax errors, monolithic binary inclusion caps lexical baselines at ~12.5 symbols under $B = 2,000$ tokens. We propose **MR-TopoS** (Multi-Resolution Dual-View Program Topology Context Induction). MR-TopoS models repositories as asymmetric dual-view graphs and formulates context compilation as a **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)**. Solved via Mixed Integer Linear Programming (MILP) with HiGHS dual-simplex branch-and-cut in 2.8 ms ($N=60$), MR-TopoS balances a multi-resolution lattice (Full, Skeleton, Stub, Excluded) with soft causal callee preservation. A Differential Typing Pruner purges prose documentation from modern typing constructs (`Annotated[T, Doc(...)]`) while preserving type contracts, and a deterministic Budget Guard guarantees $100.0\%$ zero budget violations against the 262,144-vocabulary Google Gemma 4 tokenizer. Evaluated across 129 SWE benchmark tasks (2,580 evaluations), MR-TopoS retains **$1.55\times$ more full implementations** (19.47 vs 12.55) and $4.05\times$ total symbols, increasing macro target file recall across all patch references by **$+29.98\%$** ($0.4846$ vs $0.3728$, $p = 0.011$) and pre-existing gold recall by **$+30.95\%$** ($0.5087$ vs $0.3885$, $p = 0.007$) over scoped retrieval at $B = 2,000$, with **$100.0\%$ syntactic validity**. In evaluations on `google/gemma-4-31b-it`, MR-TopoS reduces generation latency by **$28.3\%$** (7.57s vs 10.55s, $p = 0.038$)."""

    text = text.replace(old_abstract, new_abstract)

    # 5. Section 4.1 & 5.3 tightening (trim ~40 words)
    old_sec41 = """We evaluate MR-TopoS across **129 SWE benchmark tasks** (127 unique base-commit snapshots) from four production repositories: `fastapi` (67 tasks), `rich` (48 tasks), `requests` (13 tasks), and `httpx` (1 task). Across all tasks, ground-truth patches modify **278 file references**, comprising:
- **Pre-existing source files**: **229 references** (82.4%), present in base repository snapshots.
- **Patch-created new files**: **49 references** (17.6%), created by the bug-fix patch itself.
Because an inference-time retrieval algorithm cannot localize files that do not exist prior to patch application, we evaluate both Macro Recall across all 278 modified-file references ($N=129$) and Macro Recall across retrievable pre-existing references ($N=128$, excluding the single task `fastapi_15661` where no pre-existing target file existed)."""

    new_sec41 = """We evaluate MR-TopoS across **129 SWE tasks** (127 unique base commits) from four repositories: `fastapi` (67 tasks), `rich` (48 tasks), `requests` (13 tasks), and `httpx` (1 task). Across all tasks, patches modify **278 file references**:
- **Pre-existing files**: **229 references** (82.4%), present in base snapshots.
- **Patch-created files**: **49 references** (17.6%), created by bug-fix patches.
Because retrieval cannot localize non-existent files, we report Macro Recall across all 278 references ($N=129$) and retrievable pre-existing references ($N=128$, excluding task `fastapi_15661` where no pre-existing target existed)."""

    text = text.replace(old_sec41, new_sec41)

    # 6. Section 7 tightening (trim ~15 words)
    old_sec7 = """In whole-file retrieval (`full_file`), increasing budget from $B=8,000$ to $B=16,000$ paradoxically degrades Top-1 gold localization due to **test file crowding**: monolithic test files contain dense keyword matches and massive token footprints (`tests/test_requests.py` has 15,941 tokens, vs 7,977 for target `requests/models.py`). At 16k tokens, the test file fits and is packed first, crowding out the gold source file. MR-TopoS eliminates this pathology by pruning test files at symbol resolution."""

    new_sec7 = """In whole-file retrieval (`full_file`), increasing budget from $8\\text{k}$ to $16\\text{k}$ degrades Top-1 gold localization due to **test file crowding**: monolithic test files have dense keyword matches and massive footprints (`tests/test_requests.py` has 15,941 tokens, vs 7,977 for target `requests/models.py`). At 16k, the test file fits and packs first, crowding out gold source files. MR-TopoS eliminates this by pruning test files at symbol resolution."""

    text = text.replace(old_sec7, new_sec7)

    with open("paper/final_submission_candidate.md", "w", encoding="utf-8") as f:
        f.write(text)

    all_words = text.split()
    body_words = text.split("## References")[0].split()
    print(f"Total words: {len(all_words)}")
    print(f"Body words: {len(body_words)}")

if __name__ == "__main__":
    streamline()
