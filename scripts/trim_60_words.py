with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Section 4.1
old_s41 = """### 4.1 Benchmark Corpus & Denominators
We evaluate MR-TopoS across **129 SWE benchmark tasks** (127 unique base-commit snapshots) from four production repositories: `fastapi` (67 tasks), `rich` (48 tasks), `requests` (13 tasks), and `httpx` (1 task).
Across all tasks, ground-truth patches modify **278 file references**, comprising:
- **Pre-existing source files**: **229 files** (82.4%), present in base repository snapshots.
- **Patch-created new files**: **49 files** (17.6%), created by the bug-fix patch itself.
Because an inference-time retrieval algorithm cannot localize files that do not yet exist, we evaluate pre-existing target file localization ($|\\mathcal{F}_{\\text{context}} \\cap \\mathcal{F}_{\\text{pre}}| / |\\mathcal{F}_{\\text{pre}}|$) alongside overall recall."""

new_s41 = """### 4.1 Benchmark Corpus & Denominators
We evaluate MR-TopoS across **129 SWE tasks** (127 unique base commits) from four repositories: `fastapi` (67 tasks), `rich` (48 tasks), `requests` (13 tasks), and `httpx` (1 task). Ground-truth patches modify **278 file references**:
- **Pre-existing files**: **229 references** (82.4%), present in base snapshots.
- **Patch-created files**: **49 references** (17.6%), created by bug fixes.
Because retrieval cannot localize non-existent files, we report Macro Recall across all 278 references ($N=129$) and pre-existing references ($N=128$, excluding task `fastapi_15661` which had zero base targets)."""

text = text.replace(old_s41, new_s41)

# 2. Section 1 Contributions
old_contrib = """### Contributions
1. **Asymmetric Dual-View Topology**: Decouples downward containment ($E_{\\text{hier}}$) from invocations ($E_{\\text{call}}$) and dependencies ($E_{\\text{import}}$), preventing artificial mega-hubs.
2. **Exact PC-MCKP Formulation**: Context selection formulated as an exact MILP with linear precedence and exclusivity, proving syntactic closure when nesting full implementations in stubbed containers.
3. **Differential Typing Pruner & Strict Budget Guard**: Purges prose documentation while preserving type contracts, backed by a deterministic budget guard calibrated to the Gemma 4 tokenizer.
4. **Empirical Validation**: Benchmarked on 129 SWE tasks, demonstrating $+29.98\\%$ gold recall and $1.55\\times$ more full implementations at $B=2,000$, confirmed with downstream Gemma 4 31B evaluations showing $28.3\\%$ faster generation."""

new_contrib = """### Contributions
1. **Asymmetric Dual-View Topology**: Decouples containment ($E_{\\text{hier}}$) from calls ($E_{\\text{call}}$) and imports ($E_{\\text{import}}$), preventing synthetic root hubs.
2. **Exact PC-MCKP Formulation**: Formulates context selection as an exact MILP with linear precedence, proving syntactic closure when nesting full methods in stubbed containers.
3. **Differential Typing Pruner & Budget Guard**: Purges prose documentation while preserving type contracts, backed by a deterministic budget guard for the Gemma 4 tokenizer.
4. **Empirical Validation**: Benchmarked on 129 SWE tasks, demonstrating $+29.98\\%$ gold recall and $1.55\\times$ more full implementations at $B=2,000$, confirmed by downstream Gemma 4 31B evaluations showing $28.3\\%$ faster generation."""

text = text.replace(old_contrib, new_contrib)

# 3. Section 2.2
old_s22 = """### 2.2 Multi-Resolution Representation Lattice
MR-TopoS defines a 4-tier resolution lattice $\\mathcal{R} = \\{\\text{EXCLUDED}(0), \\text{STUB}(1), \\text{SKELETON}(2), \\text{FULL}(3)\\}$:
- **Tier 3 (FULL)**: Complete implementation body and all docstrings ($c_{i3}$ tokens).
- **Tier 2 (SKELETON)**: Type annotations, pruned signatures, 1-line docstring summary, elided bodies ($c_{i2} \\approx 0.15 c_{i3}$).
- **Tier 1 (STUB)**: Qualified definition header only (`def f(...): ...`) for syntactic scoping ($c_{i1} \\approx 0.05 c_{i3}$).
- **Tier 0 (EXCLUDED)**: Omitted entirely ($c_{i0} = 0$)."""

new_s22 = """### 2.2 Multi-Resolution Representation Lattice
MR-TopoS defines a 4-tier resolution lattice $\\mathcal{R} = \\{\\text{EXCLUDED}(0), \\text{STUB}(1), \\text{SKELETON}(2), \\text{FULL}(3)\\}$:
- **Tier 3 (FULL)**: Complete implementation body and docstrings ($c_{i3}$ tokens).
- **Tier 2 (SKELETON)**: Pruned signature, 1-line docstring summary, elided bodies ($c_{i2} \\approx 0.15 c_{i3}$).
- **Tier 1 (STUB)**: Definition header only (`def f(...): ...`) for scoping ($c_{i1} \\approx 0.05 c_{i3}$).
- **Tier 0 (EXCLUDED)**: Omitted entirely ($c_{i0} = 0$)."""

text = text.replace(old_s22, new_s22)

# Check total words
words = text.split()
print("Total words after trim:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated manuscript successfully.")

