with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Section 3.1 Proof
old_proof = """*Proof*: In Python grammar, a class definition requires a non-empty statement suite. Because child method $c$ is rendered as an indented `FunctionDef` within the scope of $p$, the statement suite is populated with a valid compound statement. Hence, `ast.parse()` constructs a valid `ast.ClassDef` AST node. Syntax and indentation errors are provably avoided."""

new_proof = """*Proof*: Python class definitions require a non-empty suite. Rendering child method $c$ as an indented `FunctionDef` within parent $p$ populates the suite with a valid compound statement. Hence, `ast.parse()` constructs a valid `ClassDef` AST node without syntax errors."""

text = text.replace(old_proof, new_proof)

# Section 1 introductory paragraph
old_s1_intro = """Autonomous developer agents automate bug localization and patch synthesis across software repositories (Jimenez et al., 2024; Yang et al., 2024). However, deploying models like Google's Gemma 4 31B exposes an operational bottleneck: **context compilation under strict token budgets**. Real-world repositories exceed millions of tokens; uncompressed contexts degrade attention focus (Liu et al., 2024), scale inference costs quadratically across agent turns, and crowd out target source files.

Snippet retrieval (e.g., BM25) extracts isolated methods but severs enclosing scopes, inducing syntax errors. Wrapping methods in parent class stubs (`class P: def m(...): ...`) restores syntax, but monolithic binary inclusion caps context at ~12.5 symbols at $B = 2,000$ tokens. While early pilots hypothesized a 28.9% scope-wrapping penalty, 129-task audits reveal class headers consume only ~5.4 tokens; the true bottleneck is the lack of multi-resolution representation."""

new_s1_intro = """Autonomous developer agents automate bug localization and patch synthesis across repositories (Jimenez et al., 2024; Yang et al., 2024). However, deploying models like Google's Gemma 4 31B exposes an operational bottleneck: **context compilation under constrained token budgets**. Codebases exceed millions of tokens; uncompressed contexts degrade attention focus (Liu et al., 2024), scale costs quadratically across turns, and crowd out target source files.

Snippet retrieval (e.g., BM25) extracts isolated methods but severs enclosing scopes, inducing syntax errors. Enclosing methods in class stubs (`class P: def m(...): ...`) restores syntax, but monolithic binary inclusion caps context at ~12.5 symbols under $B = 2,000$ tokens. While early pilots hypothesized a 28.9% scope penalty, 129-task audits reveal class headers consume only ~5.4 tokens; the true bottleneck is the lack of multi-resolution representation."""

text = text.replace(old_s1_intro, new_s1_intro)

# Section 5.1 significance note
old_sig = """*Statistical Significance*: At $B=2,000$, MR-TopoS MILP improves Macro All Recall by $+29.98\%$ ($t(128)=2.57, p=0.011$; Wilcoxon $p=0.017$) and Pre-Existing Recall by $+30.95\%$ ($t(127)=2.73, p=0.007$; Wilcoxon $p=0.017$). At $B=4,000$, gains remain highly significant ($p < 0.001$). At $B=8,000$ and $16,000$, performance reaches statistical parity ($p = 0.856$ and $p = 0.179$)."""

new_sig = """*Statistical Significance*: At $B=2,000$, MR-TopoS MILP improves Macro All Recall by $+29.98\%$ ($t(128)=2.57, p=0.011$; Wilcoxon $p=0.017$) and Pre-Existing Recall by $+30.95\%$ ($t(127)=2.73, p=0.007$; Wilcoxon $p=0.017$). At $B=4,000$, gains remain significant ($p < 0.001$). At $B=8,000$ and $16,000$, performance reaches statistical parity ($p = 0.856$ and $p = 0.179$)."""

text = text.replace(old_sig, new_sig)

# Abstract tightening
old_abs = """While restoring parent scopes eliminates syntax errors, monolithic binary inclusion forces an all-or-nothing trade-off that caps lexical baselines at ~12.5 symbols under $B = 2,000$ tokens. We propose **MR-TopoS** (Multi-Resolution Dual-View Program Topology Context Induction). MR-TopoS models repositories as asymmetric dual-view graphs and formulates context compilation as a **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)**. Solved via Mixed Integer Linear Programming (MILP) with HiGHS dual-simplex branch-and-cut in 2.8 ms ($N=60$), MR-TopoS dynamically balances a multi-resolution lattice (Full, Skeleton, Stub, Excluded) with soft causal callee preservation. A Differential Typing Pruner purges prose documentation from modern typing constructs (`Annotated[T, Doc(...)]`) while preserving type contracts, and a deterministic Budget Guard guarantees $100.0\%$ zero budget violations against the 262,144-vocabulary Google Gemma 4 tokenizer. Evaluated across 129 SWE benchmark tasks (2,580 evaluations), MR-TopoS retains **$1.55\times$ more full implementations** (19.47 vs 12.55) and $4.05\times$ total symbols, increasing macro target file recall across all patch references by **$+29.98\%$** ($0.4846$ vs $0.3728$, $p = 0.011$) and pre-existing gold recall by **$+30.95\%$** ($0.5087$ vs $0.3885$, $p = 0.007$) over scoped retrieval at $B = 2,000$, while achieving **$100.0\%$ syntactic validity**. In evaluations on `google/gemma-4-31b-it`, MR-TopoS reduces generation latency by **$28.3\%$** (7.57s vs 10.55s, $p = 0.038$) by presenting structured contracts rather than unpruned class implementations."""

new_abs = """While restoring parent scopes eliminates syntax errors, monolithic binary inclusion caps lexical baselines at ~12.5 symbols under $B = 2,000$ tokens. We propose **MR-TopoS** (Multi-Resolution Dual-View Program Topology Context Induction). MR-TopoS models repositories as asymmetric dual-view graphs and formulates context compilation as a **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)**. Solved via Mixed Integer Linear Programming (MILP) with HiGHS dual-simplex branch-and-cut in 2.8 ms ($N=60$), MR-TopoS balances a multi-resolution lattice (Full, Skeleton, Stub, Excluded) with soft causal callee preservation. A Differential Typing Pruner purges prose documentation from typing constructs (`Annotated[T, Doc(...)]`) while preserving type contracts, backed by a deterministic Budget Guard guaranteeing zero budget violations against the 262,144-vocabulary Google Gemma 4 tokenizer. Evaluated across 129 SWE benchmark tasks (2,580 evaluations), MR-TopoS retains **$1.55\times$ more full implementations** (19.47 vs 12.55) and $4.05\times$ total symbols, increasing macro target file recall across all patch references by **$+29.98\%$** ($0.4846$ vs $0.3728$, $p = 0.011$) and pre-existing gold recall by **$+30.95\%$** ($0.5087$ vs $0.3885$, $p = 0.007$) over scoped retrieval at $B = 2,000$, with **$100.0\%$ syntactic validity**. In evaluations on `google/gemma-4-31b-it`, MR-TopoS reduces generation latency by **$28.3\%$** (7.57s vs 10.55s, $p = 0.038$)."""

text = text.replace(old_abs, new_abs)

words = text.split()
print("Final total word count:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved candidate.")

