# Systematic Ablation Analysis of MR-TopoS Components

**Audit Date**: November 5, 2026  
**Track**: Google Gemma 4 Developer Agent Paper Track  
**Evaluated Budget**: $B = 4,000$ subword tokens across 129 SWE benchmark tasks  

---

## 1. Objective

This investigation isolates and quantifies the marginal contribution of each architectural component within MR-TopoS:
1. Multi-Resolution Lattice (4 Tiers vs Binary 0/1 Inclusion)
2. AST Syntactic Scope Preservation (Hierarchical Containment vs Flat Snippets)
3. Causal Path Topology ($\lambda_{\text{topo}}=0.5$ vs Lexical-Only BM25)
4. Differential Typing Pruner (Modern Typing Metadata & Non-Empty Class Invariant)
5. Candidate Pool Scaling ($K \in \{20, 60, 100\}$)

---

## 2. Quantitative Findings

### 2.1 Multi-Resolution Representation Lattice
- **Full Model**: Retains $59.8$ symbols with gold recall of $0.7132$.
- **Binary Inclusion (`ablation_binary_tiers`)**: Retains only $31.0$ symbols (a **$48.2\%$ reduction in symbol capacity**), dropping gold recall to $0.5581$ (a **$21.7\%$ relative drop**).
- **Scientific Takeaway**: Forcing an all-or-nothing binary choice between raw code and total exclusion severely penalizes context diversity under tight token budgets. The 4-tier lattice allows container classes and non-focal callees to exist at STUB or SKELETON tiers, freeing capacity for high-utility target methods.

### 2.2 AST Scope Preservation & The Scope Tax
- **Flat Snippets (`ablation_no_scope_preservation`)**: Achieves higher symbol capacity ($41.5$ symbols) and recall ($0.6202$) than binary scoped retrieval ($31.0$ symbols), but suffers from **$0.0\%$ syntactic validity** due to orphan methods lacking class bindings.
- **MR-TopoS Solution**: Full MR-TopoS completely eliminates the Scope Tax: it achieves **$100.0\%$ syntactic validity** while retaining **$59.8$ symbols** ($+44.1\%$ over flat snippets and $+92.9\%$ over binary scoped retrieval).

### 2.3 Causal Path Subgraph Propagation
- Setting $\lambda_{\text{topo}} = 0$ (`ablation_no_causal_topology`) removes topological invocation and import weights.
- Gold file recall drops from $0.7132$ to $0.6512$ (a **$8.7\%$ degradation**), and Hit@1 drops from $0.2636$ to $0.2171$ (a **$17.6\%$ degradation**).
- **Scientific Takeaway**: Many bug fixes modify helper functions, interfaces, or type definitions that do not appear verbatim in the issue description. Causal path expansion surfaces these structural dependencies via directed call and import edges.

### 2.4 Differential Typing Pruner
- Disabling the pruner (`ablation_no_differential_pruner`) retains verbose docstrings and unpruned `Annotated[T, Doc(...)]` metadata.
- Skeleton token cost increases by **$41.2\%$**, reducing retained symbol capacity from $59.8$ to $47.2$.
- Furthermore, docstring-only classes become empty upon method stripping, causing AST parse failures (`IndentationError`) and reducing syntactic validity to **$96.1\%$**.
- **Scientific Takeaway**: The Differential Typing Pruner is essential for modern typed codebases like FastAPI and Pydantic v2.

### 2.5 Candidate Pool Scaling ($K$)
- At $K=20$, the candidate pool is too restricted: gold recall drops to $0.5426$ because supporting files never enter the optimizer's candidate set.
- At $K=60$ (standard MR-TopoS), gold recall reaches $0.7132$ with solve time of $4.32\text{ ms}$.
- At $K=100$, gold recall increases modestly to $0.7209$ ($+1.1\%$), but solve time increases to $7.18\text{ ms}$.
- **Scientific Takeaway**: $K=60$ represents the optimal Pareto frontier between recall and millisecond-level solver efficiency.

