import re

def optimize_word_count():
    with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
        text = f.read()

    # Section 1 intro streamlining
    old_intro = """Autonomous developer agents automate software maintenance across repositories (Jimenez et al., 2024; Yang et al., 2024). However, models like Google Gemma 4 encounter an operational bottleneck: **context compilation under constrained token budgets**. Uncompressed contexts degrade attention (Liu et al., 2024). Whole-file retrieval exhausts token budgets, while snippet extraction severs scopes, inducing syntax errors in 24.8% of cases. Enclosing snippets in parent stubs restores syntax, but monolithic inclusion caps context at ~12.5 symbols at $B = 2,000$ tokens. While class headers consume a median of 5.0 tokens, agents lack multi-resolution representations."""
    new_intro = """Autonomous developer agents automate software maintenance across repositories (Jimenez et al., 2024; Yang et al., 2024). Under constrained token budgets, uncompressed contexts degrade attention (Liu et al., 2024). Whole-file retrieval rapidly exhausts token capacity, while snippet extraction severs AST scopes, causing syntax errors in 24.8% of cases. Monolithic snippet enclosure restores syntax but caps context at ~12.5 symbols at $B = 2,000$ tokens. Although parent class headers require a median of only 5.0 tokens, agents lack multi-resolution context representations."""

    # Section 2.2 lattice streamlining
    old_lat = """MR-TopoS defines a 4-tier discrete resolution lattice $\\mathcal{R} = \\{\\text{EXCLUDED} (0), \\text{STUB} (1), \\text{SKELETON} (2), \\text{FULL} (3)\\}$:
- **Tier 3 (FULL)**: Complete original source code.
- **Tier 2 (SKELETON)**: Contract skeleton preserving signatures, annotations, and docstrings (`...` bodies).
- **Tier 1 (STUB)**: Structural stub retaining identifier signature (`def name(...): ...`).
- **Tier 0 (EXCLUDED)**: Omitted ($\\epsilon$).
Token costs $c_{ir}$ are measured directly by the Gemma 4 tokenizer ($0 = c_{i0} < c_{i1} \\le c_{i2} \\le c_{i3}$)."""
    new_lat = """MR-TopoS defines a 4-tier discrete resolution lattice $\\mathcal{R} = \\{\\text{EXCLUDED} (0), \\text{STUB} (1), \\text{SKELETON} (2), \\text{FULL} (3)\\}$: Tier 3 (FULL) retains complete original source; Tier 2 (SKELETON) preserves signatures, annotations, and docstrings with `...` bodies; Tier 1 (STUB) retains identifier signatures; Tier 0 (EXCLUDED) is omitted ($\\epsilon$). Token costs $c_{ir}$ are measured via the Gemma 4 tokenizer ($0 = c_{i0} < c_{i1} \\le c_{i2} \\le c_{i3}$)."""

    # Section 3.2 serializer streamlining
    old_s32 = """Context is compiled via the AST operator $\\mathcal{C}(\\mathbf{x})$:
1. **File Grouping**: Active symbols $\\mathcal{S}^* = \\{s_i \\mid x_{ir}=1, r \\ge 1\\}$ are partitioned by file path.
2. **Shared-Parent Reconstruction**: Emits enclosing `class C:` headers for member methods, nesting methods with 4-space indentation. If omitted by the optimizer ($x_{C0}=1$), the serializer reconstructs headers post-hoc. Reconstructed headers incur a median overhead of 5.0 tokens (mean $5.06$), with a **$56.05\\%$ pooled deduplication rate** ($43.39\\%$ mean per run), eliminating 12,224 redundant definitions across 493 reconstructed runs (out of 496 method-parent runs; in 3 runs the parent was chosen directly by the knapsack optimizer)."""
    new_s32 = """Context is compiled via the AST operator $\\mathcal{C}(\\mathbf{x})$:
1. **File Grouping**: Active symbols $\\mathcal{S}^* = \\{s_i \\mid x_{ir}=1, r \\ge 1\\}$ are partitioned by file path.
2. **Shared-Parent Reconstruction**: Emits enclosing `class C:` headers with 4-space indentation. If omitted by the optimizer ($x_{C0}=1$), headers are reconstructed post-hoc at a median cost of 5.0 tokens (mean $5.06$), achieving a **$56.05\\%$ pooled deduplication rate** ($43.39\\%$ mean per run) and eliminating 12,224 redundant definitions across 493 reconstructed runs (out of 496 method-parent runs; in 3 runs the parent was selected directly by the knapsack optimizer)."""

    # Section 3.3 pruning streamlining
    old_s33 = """Because layout adds non-linear tokens ($27.6$ to $111.1$ tokens on average), the optimizer operates on an additive surrogate model. While the initial serializer achieved 99.46% syntax validity across 5,160 factorial runs (with 28 truncations under uncoupled high-$K$ saturation pools), the updated multi-stage atomic symbol pruner achieved **100.0% syntactic validity across the 516-run parent audit** and resolved all 28 historical truncation cases without line-slicing."""
    new_s33 = """Because layout adds non-linear tokens ($27.6$ to $111.1$ tokens on average), the optimizer uses an additive surrogate model. While the initial serializer achieved 99.46% syntax validity across 5,160 factorial runs (with 28 truncations under uncoupled high-$K$ saturation sweeps), the updated atomic symbol pruner achieved **100.0% syntax validity across the 516-run parent audit** and resolved all 28 historical truncation cases without line-slicing."""

    # Section 5.3 streamlining
    old_s53 = """At $B=2,000$, MR-TopoS retains **$1.55\\times$ more full implementations** ($19.47$ vs $12.55$) than Scoped BM25, allocating $1,849$ tokens to full code versus $1,192$. Skeletons ($30.00$) and stubs ($1.39$) compress context, freeing budget for target functions."""
    new_s53 = """At $B=2,000$, MR-TopoS retains **$1.55\\times$ more full implementations** ($19.47$ vs $12.55$) than Scoped BM25, allocating $1,849$ tokens to full code versus $1,192$. Skeletons ($30.00$) and stubs ($1.39$) compress surrounding context, freeing token budget for target functions."""

    # Section 5.4 streamlining
    old_s54 = """Scaling candidate depth eliminates saturation, lifting $16\\text{k}$ recall to **$76.92\\%$** ($+16.44\\text{ pp}$ over Scoped BM25, $p_{\\text{Holm-12}} = 0.0043$; $+20.76\\text{ pp}$ over static $K=60$, $p_{\\text{Holm-12}} = 0.00056$). Dynamic Policy leads Aider RepoMap at $8\\text{k}$ ($+18.66\\text{ pp}, p_{\\text{Holm-12}} = 0.0435$), with no statistically detectable difference at other budgets under omnibus correction."""
    new_s54 = """Dynamic candidate scaling eliminates saturation, lifting $16\\text{k}$ recall to **$76.92\\%$** ($+16.44\\text{ pp}$ over Scoped BM25, $p_{\\text{Holm-12}} = 0.0043$; $+20.76\\text{ pp}$ over static $K=60$, $p_{\\text{Holm-12}} = 0.00056$). Dynamic Policy outperforms Aider RepoMap at $8\\text{k}$ ($+18.66\\text{ pp}, p_{\\text{Holm-12}} = 0.0435$), with no statistically detectable difference at other budgets under omnibus correction."""

    # Section 6 pilot streamlining
    old_s6 = """2. **Patch Application Limitations**: Zero-shot unified diffs failed strict `git apply` across all paradigms (0% pass rate) due to hunk line-number drift ($61.1\\%$) and indentation mismatch ($22.2\\%$), confirming SWE agents require interactive multi-turn editing tools. This pilot provides exploratory evidence of inference efficiency, not downstream repair completion."""
    new_s6 = """2. **Patch Application Limitations**: Zero-shot diffs failed strict `git apply` across all paradigms (0% pass rate) due to line-number drift ($61.1\\%$) and indentation mismatch ($22.2\\%$), confirming SWE agents require interactive editing tools. This pilot provides preliminary latency evidence, not downstream repair verification."""

    reps = [
        (old_intro, new_intro),
        (old_lat, new_lat),
        (old_s32, new_s32),
        (old_s33, new_s33),
        (old_s53, new_s53),
        (old_s54, new_s54),
        (old_s6, new_s6)
    ]

    for o, n in reps:
        if o not in text:
            print("Failed to find block:", repr(o[:40]))
            return
        text = text.replace(o, n)

    w = len(text.split())
    print("New word count:", w)
    with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Saved!")

if __name__ == '__main__':
    optimize_word_count()
