with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('### Positioning Relative to Prior Art')
idx2 = text.find('## 2. Theoretical Foundations')

new_pos_contrib = """### Positioning Relative to Prior Art
1. **LocAgent (ACL 2025)** navigates code graphs interactively through multi-turn LLM agent queries for binary file localization (Chen et al., 2025). In contrast, MR-TopoS is an offline, zero-turn compiler executing exact combinatorial optimization on CPU in milliseconds before generation begins.
2. **Aider Repository Map** applies Personalized PageRank over tag reference graphs to emit signature outlines, retrieving complete files separately in subsequent turns (Gauthier, 2024). In contrast, MR-TopoS solves a unified PC-MCKP nesting full implementations inside skeletonized class containers in a single prompt.
3. **Context Compression (EMNLP 2023; arXiv:2604.13725)** prunes tokens via statistical language model perplexity or entropy (Li et al., 2023; Feng et al., 2026). In formal code syntax, token-dropping severs structural delimiters and indentation; MR-TopoS enforces grammar-preserving AST transformations, guaranteeing 100% syntactic parse validity.

### Contributions
1. **Asymmetric Dual-View Topology**: Decouples containment ($E_{\\text{hier}}$) from invocations ($E_{\\text{call}}$) and dependencies ($E_{\\text{import}}$), preventing synthetic root hubs.
2. **Exact PC-MCKP Formulation**: Models context compilation as an exact MILP with linear precedence and exclusivity, proving syntactic closure when nesting full methods in stubbed containers.
3. **Differential Typing Pruner & Strict Budget Guard**: Purges prose documentation while preserving type contracts, backed by a deterministic budget guard for the Gemma 4 tokenizer.
4. **Empirical Validation**: Benchmarked across 129 SWE tasks, demonstrating $+29.98\\%$ gold recall and $1.55\\times$ more full implementations at $B=2,000$, confirmed by downstream Gemma 4 31B evaluations showing $28.3\\%$ faster generation.

---

"""

text = text[:idx1] + new_pos_contrib + text[idx2:]

words = text.split()
print("Final total word count:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved refined candidate.")

