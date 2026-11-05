with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('### 2.3 The PC-MCKP Formulation')
idx2 = text.find('## 3. Methodology & Architecture')

new_sec23 = """### 2.3 Precedence-Constrained Multi-Choice Knapsack Formulation (PC-MCKP)
Let $\\mathcal{N} \\subseteq \\mathcal{V}$ denote candidate symbols. Binary variable $x_{ir} \\in \\{0, 1\\}$ indicates whether entity $i$ is compiled at tier $r$. Base utility combines lexical relevance $s_i$ and topological weight $w_i$: $u_i = s_i + \\lambda_{\\text{topo}} w_i$. With tier multipliers $\\alpha_r \\in \\{0.0, 0.2, 0.6, 1.0\\}$, context compilation is formulated over an additive surrogate cost model:

$$\\max_{\\mathbf{x}, \\boldsymbol{\\xi}} \\sum_{i \\in \\mathcal{N}} \\sum_{r \\in \\mathcal{R}} \\alpha_r u_i x_{ir} - \\gamma \\sum_{(u, v) \\in \\mathcal{E}_{\\text{call}} \\cap (\\mathcal{N} \\times \\mathcal{N})} \\xi_{uv}$$

Subject to:
1. **Surrogate Token Capacity**: $\\sum_{i \\in \\mathcal{N}} \\sum_{r=1}^3 c_{ir} x_{ir} \\le B$, where $c_{ir}$ is the isolated subword token cost of node $i$ at tier $r$.
2. **Mutual Exclusivity**: $\\sum_{r \\in \\mathcal{R}} x_{ir} = 1 \\quad \\forall i \\in \\mathcal{N}$.
3. **AST Precedence**: If child $i$ is included ($r \\ge 1$), parent $p(i)$ must be included: $\\sum_{r=1}^3 x_{ir} \\le \\sum_{r=1}^3 x_{p(i), r} \\iff x_{p(i), 0} \\le x_{i0}$.
4. **Soft Causal Callee Contract**: If caller $u$ is FULL ($x_{u3}=1$), callee $v$ should be at least SKELETON ($x_{v2} + x_{v3} \\ge 1$), with slack $\\xi_{uv} \\ge 0$ penalizing omissions: $x_{u3} - (x_{v2} + x_{v3}) \\le \\xi_{uv}$.

*Surrogate Cost vs. Final Serialization*: Because concatenating formatted class definitions introduces layout overhead (headers, indentations, blank lines), the MILP optimizes an additive surrogate cost model. The deterministic Budget Guard (§3.2) guarantees true token feasibility against the Gemma 4 tokenizer without modifying solver optimality on the candidate graph.

---

"""

text = text[:idx1] + new_sec23 + text[idx2:]

words = text.split()
print("Total words after Section 2.3 update:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

import subprocess, sys
subprocess.run([sys.executable, 'scripts/generate_pdf.py'], capture_output=True)
import fitz
doc = fitz.open('paper/final_submission_candidate.pdf')
print('PDF pages:', len(doc))
doc.close()

