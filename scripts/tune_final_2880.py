with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Section 2.3
idx_s23 = text.find('### 2.3 Precedence-Constrained Multi-Choice Knapsack')
idx_s3 = text.find('## 3. Methodology & Architecture')

new_s23 = """### 2.3 Precedence-Constrained Multi-Choice Knapsack Formulation (PC-MCKP)
Let $\\mathcal{N} \\subseteq \\mathcal{V}$ denote candidates. Binary variable $x_{ir} \\in \\{0, 1\\}$ indicates if entity $i$ is compiled at tier $r$. Base utility combines lexical score $s_i$ and topological weight $w_i$: $u_i = s_i + \\lambda_{\\text{topo}} w_i$. With tier multipliers $\\alpha_r \\in \\{0.0, 0.2, 0.6, 1.0\\}$, compilation is optimized over an additive surrogate cost model:

$$\\max_{\\mathbf{x}, \\boldsymbol{\\xi}} \\sum_{i \\in \\mathcal{N}} \\sum_{r \\in \\mathcal{R}} \\alpha_r u_i x_{ir} - \\gamma \\sum_{(u, v) \\in \\mathcal{E}_{\\text{call}} \\cap (\\mathcal{N} \\times \\mathcal{N})} \\xi_{uv}$$

Subject to:
1. **Surrogate Token Capacity**: $\\sum_{i \\in \\mathcal{N}} \\sum_{r=1}^3 c_{ir} x_{ir} \\le B$, with isolated subword cost $c_{ir}$.
2. **Mutual Exclusivity**: $\\sum_{r \\in \\mathcal{R}} x_{ir} = 1 \\quad \\forall i \\in \\mathcal{N}$.
3. **AST Precedence**: If child $i$ is selected ($r \\ge 1$), parent $p(i)$ must be included: $\\sum_{r=1}^3 x_{ir} \\le \\sum_{r=1}^3 x_{p(i), r} \\iff x_{p(i), 0} \\le x_{i0}$.
4. **Soft Causal Callee Contract**: If caller $u$ is FULL ($x_{u3}=1$), callee $v$ must be at least SKELETON ($x_{v2} + x_{v3} \\ge 1$), with slack $\\xi_{uv} \\ge 0$: $x_{u3} - (x_{v2} + x_{v3}) \\le \\xi_{uv}$.

*Surrogate Cost Model*: Because layout formatting (headers, indentations) adds minor overhead (~9.5 tokens), MILP optimizes surrogate costs; the Budget Guard (§3.2) guarantees final token feasibility against Gemma 4.

---

"""

text = text[:idx_s23] + new_s23 + text[idx_s3:]

# 2. Section 5.3
idx_s53 = text.find('### 5.3 Candidate Saturation')
idx_s54 = text.find('### 5.4 Exact MILP vs Greedy')

new_s53 = """### 5.3 Candidate Pool Saturation at Large Budgets
At $B \\le 4,000$, MR-TopoS achieves statistically significant advantages ($p < 0.02$). At $B \\ge 8,000$, performance reaches parity ($-0.6\\%$ and $-4.3\\%$) due to candidate pool saturation at $K=60$. At 16k tokens, 60 symbols rendered in full consume ~7,000 tokens, exhausting the pool (59.90 symbols retained), whereas unconstrained Scoped BM25 drew low-ranked methods across distant files to fill 16,000 tokens. Dynamically scaling candidate pool depth ($K = \\min(200, B/30)$) is an unverified hypothesis and remains future work.

"""

text = text[:idx_s53] + new_s53 + text[idx_s54:]

words = text.split()
print("Exact final word count:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved candidate.")

