with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Streamline Section 3.2
old_s32 = """### 3.2 Differential Typing Pruner & Snapshot Grounding
1. **Differential Typing Pruner**: For modern libraries using `Annotated[T, Doc(...)]` (e.g., FastAPI), the pruner strips verbose documentation metadata while preserving runtime validation constraints (`Field(...)`). Docstrings in Tier 2 are pruned to their initial sentence; empty classes receive `pass`, preventing indentation errors.
2. **Direct Snapshot Grounding**: For modules containing assignments without function definitions (e.g., `rich/_cell_widths.py`), MR-TopoS synthesizes a `GLOBAL_DATA` symbol node, preserving constant tables at Tier 3 and eliding literals at Tiers 1–2.
3. **Causal Path Propagation**: Seed candidates expand along invocation ($\lambda_{\text{call}}=0.75$) and import ($\lambda_{\text{import}}=0.40$) paths up to depth $h=2$: $w_v = \max_{u \in \text{Pred}(v)} (w_u \cdot \lambda(u, v))$.
4. **Strict Real-Token Budget Guard**: Serialized contexts are validated against the Gemma 4 tokenizer. If joint whitespace fusion causes $T > B$, a deterministic 4-stage fallback trimming loop downgrades STUB $\to$ SKELETON $\to$ FULL $\to$ line truncation, guaranteeing $T \le B$ with $100.0\%$ mathematical certainty."""

new_s32 = """### 3.2 Differential Typing Pruner & Snapshot Grounding
1. **Differential Typing Pruner**: Strips verbose documentation metadata from `Annotated[T, Doc(...)]` while preserving validation rules (`Field(...)`). Docstrings in Tier 2 are pruned to their initial sentence; empty classes render `pass`.
2. **Snapshot Grounding**: Synthesizes `GLOBAL_DATA` nodes for assignment tables (e.g., `rich/_cell_widths.py`), preserving lookup tables at Tier 3 and eliding values at Tiers 1–2.
3. **Causal Path Propagation**: Seed candidates expand along call ($\lambda_{\text{call}}=0.75$) and import ($\lambda_{\text{import}}=0.40$) paths up to depth $h=2$: $w_v = \max_{u \in \text{Pred}(v)} (w_u \cdot \lambda(u, v))$.
4. **Strict Budget Guard**: Serialized contexts are measured against the Gemma 4 tokenizer. If formatting causes $T > B$, a deterministic fallback loop downgrades STUB $\to$ SKELETON $\to$ FULL $\to$ line truncation, guaranteeing $T \le B$ with zero violations."""

text = text.replace(old_s32, new_s32)

# 2. Streamline Section 7
old_s7 = """## 7. The Full-File Localization Paradox

In whole-file retrieval (`full_file`), increasing budget from $B=8,000$ to $B=16,000$ paradoxically degrades Top-1 gold localization due to **test file crowding**: monolithic test files contain dense keyword matches and massive token footprints (`tests/test_requests.py` has 15,941 tokens, vs 7,977 for target `requests/models.py`). At 16k tokens, the test file fits and is packed first, crowding out the gold source file. MR-TopoS eliminates this pathology by pruning test files at symbol resolution."""

new_s7 = """## 7. The Full-File Localization Paradox

In whole-file retrieval (`full_file`), increasing budget from $B=8,000$ to $B=16,000$ paradoxically degrades Top-1 gold localization due to **test file crowding**: monolithic test files contain dense keyword matches and massive token footprints (`tests/test_requests.py` has 15,941 tokens, vs 7,977 for target `requests/models.py`). At 16k, the test file fits and crowds out the gold source file. MR-TopoS eliminates this pathology by pruning test files at symbol resolution."""

text = text.replace(old_s7, new_s7)

# 3. Streamline Section 8
old_s8 = """## 8. Discussion & Limitations

1. **Candidate Pool Scalability**: MR-TopoS fixed the candidate pool at $K=60$. As shown in Section 5.3, this saturates under large budgets ($B \ge 8\text{k}$). Future work should dynamically scale $K$ with budget.
2. **Multi-Turn Integration**: The Gemma 4 repair pilot confirmed that zero-shot unified diffs suffer from line drift. Future agent integrations should embed MR-TopoS into interactive tool loops (e.g., search/replace blocks).
3. **Language Portability**: While evaluated on Python ASTs, the PC-MCKP formulation is language-agnostic and directly extensible to JavaScript, Go, and Rust via tree-sitter."""

new_s8 = """## 8. Discussion & Limitations

1. **Candidate Pool Depth**: Fixing candidate pool depth at $K=60$ limits large-budget performance ($B \ge 8\text{k}$). Dynamically scaling $K$ with budget remains future work.
2. **Multi-Turn Integration**: The Gemma 4 pilot confirmed that zero-shot diffs suffer from line drift. Agents require interactive edit tool loops rather than single-shot patch emission.
3. **Language Scope**: While evaluated on Python, PC-MCKP is language-agnostic and extensible to JavaScript, Go, and Rust via tree-sitter."""

text = text.replace(old_s8, new_s8)

words = text.split()
print("Total words after streamlining:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

import subprocess, sys
subprocess.run([sys.executable, 'scripts/generate_pdf.py'], capture_output=True)
import fitz
doc = fitz.open('paper/final_submission_candidate.pdf')
print('PDF pages:', len(doc))
doc.close()

