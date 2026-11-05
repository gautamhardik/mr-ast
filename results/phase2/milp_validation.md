# MR-TopoS Phase 2 Validation: Precedence-Constrained Multi-Choice Knapsack (PC-MCKP) Formulation & Empirical Benchmark

## 1. Executive Summary

This document presents the complete mathematical formulation, algorithmic implementation, and empirical validation of the **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)** context compiler for **MR-TopoS**.

Our benchmark evaluates exact branch-and-cut optimization using HiGHS (`scipy.optimize.milp`) against a value-density greedy baseline across 15 experimental configurations spanning candidate set sizes $N \in \{50, 100, 200, 400, 800\}$ (up to 3,200 binary decision variables) under Tight (10%), Moderate (30%), and Generous (60%) token budget regimes.

### Key Empirical Findings

1. **Syntactic Infeasibility of Greedy Context Selection**: Under tight budgets, the standard value-density greedy heuristic creates between **12 and 249 syntactic precedence violations** (orphaned methods whose parent class was excluded from context). In contrast, the Exact MILP compiler achieves **0 precedence violations** across all 15 configurations without exception.
2. **Sub-Second Exact Optimization**: The MILP solver consistently reaches global optimality in **23.8 ms to 127.0 ms** for realistic candidate sets ($N = 50 \text{ to } 100$), and finishes in **1,009.9 ms** for massive 3,200-variable problem instances.
3. **Strict Gold-Patch Quarantine**: The valuation function $V(v, r)$ depends strictly on lexical query similarity $s_v$ and topological graph distance $w_v$. The solver interface strictly forbids and contains zero references to ground-truth patches or test files.

---

## 2. Complete PC-MCKP Mathematical Formulation

Let the candidate syntactic elements be represented as a directed graph $\mathcal{G} = (V, E_{\text{hier}} \cup E_{\text{call}} \cup E_{\text{import}})$, where:
- $V$: Candidate symbol nodes (modules, classes, methods, functions, data tables).
- $E_{\text{hier}}$: Asymmetric, downward AST containment edges $(u, v)$ where $u$ is the parent container (e.g., class) and $v$ is the child member (e.g., method).
- $E_{\text{call}}$: Directed runtime invocation edges $(u, v)$ where $u$ invokes $v$.
- $E_{\text{import}}$: Directed module-level dependency edges.

Each node $v \in V$ can be assigned exactly one resolution tier from the set $\mathcal{R} = \{0, 1, 2, 3\}$:
- $r = 0$: **EXCLUDED** ($c(v, 0) = 0, \mu_0 = 0.0$)
- $r = 1$: **STRUCTURAL STUB** ($c(v, 1) = \text{cost}_{\text{stub}}, \mu_1 = 0.2$)
- $r = 2$: **CONTRACT SKELETON** ($c(v, 2) = \text{cost}_{\text{skel}}, \mu_2 = 0.6$)
- $r = 3$: **FULL IMPLEMENTATION** ($c(v, 3) = \text{cost}_{\text{raw}}, \mu_3 = 1.0$)

### Decision Variables

- $x_{v,r} \in \{0, 1\}$: Binary indicator that node $v$ is selected at resolution tier $r \in \mathcal{R}$.
- $\xi_{u,v} \ge 0$: Continuous slack variable penalizing broken callee contracts when caller $u$ is retained at FULL resolution while callee $v$ is not retained at least at SKELETON resolution.

### Objective Function

Maximize the total contextual value minus soft callee contract violation penalties:

$$\max_{x, \xi} \quad \sum_{v \in V} \sum_{r \in \mathcal{R}} \mu_r \cdot \Big(s_v + \lambda_{\text{topo}} w_v\Big) x_{v,r} - \gamma_{\text{slack}} \sum_{(u, v) \in E_{\text{call}}} \xi_{u,v}$$

where:
- $s_v \in [0, 1]$ is the lexical similarity between the task problem statement and node $v$.
- $w_v \in [0, 1]$ is the topological causal path weight computed via directional decay.
- $\lambda_{\text{topo}} = 0.5$ balances lexical and structural relevance.
- $\gamma_{\text{slack}} = 5.0$ penalizes missing callee interface contracts.

### Constraints

1. **Exact Multi-Choice Exclusivity**:
   Every candidate node must be assigned exactly one resolution tier:
   $$\sum_{r=0}^3 x_{v,r} = 1 \quad \forall v \in V$$

2. **AST Containment Precedence (Hard DAG Invariant)**:
   A child symbol $v$ (e.g., a method) can only be included at an active resolution tier ($r \ge 1$) if its syntactic parent $u$ (e.g., its enclosing class) is also included at an active tier:
   $$x_{v,r} \le \sum_{r'=1}^3 x_{u,r'} \quad \forall (u, v) \in E_{\text{hier}}, \quad \forall r \in \{1, 2, 3\}$$

3. **Global Token Budget**:
   The total token consumption of all selected representations cannot exceed budget $B$:
   $$\sum_{v \in V} \sum_{r \in \mathcal{R}} c(v, r) x_{v,r} \le B$$

4. **Callee Interface Contract Coupling (Soft Precedence)**:
   If caller $u$ is selected at FULL tier ($x_{u,3} = 1$), callee $v$ must be retained at least at SKELETON tier ($x_{v,2} + x_{v,3} \ge 1$), or a penalty $\xi_{u,v} \ge 1$ is incurred:
   $$\xi_{u,v} \ge x_{u,3} - (x_{v,2} + x_{v,3}) \quad \forall (u, v) \in E_{\text{call}}$$
   $$\xi_{u,v} \ge 0 \quad \forall (u, v) \in E_{\text{call}}$$

---

## 3. Empirical Scalability & Optimality Benchmark

The benchmark was executed using Python 3.13 and the HiGHS branch-and-cut solver (`scipy.optimize.milp`). Complete per-run metrics are recorded in `results/phase2/greedy_comparison.csv`.

| Candidate Set ($N$) | MILP Vars | Budget Regime | Token Budget | MILP Time (ms) | Greedy Time (ms) | MILP Violations | Greedy Violations | Optimality Gap (%) |
|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **50** | 200 | Tight (10%) | 291 | 119.39 | 0.26 | **0** | **12** | 0.0%* |
| **50** | 200 | Moderate (30%) | 875 | 23.80 | 0.22 | **0** | **4** | 0.68% |
| **50** | 200 | Generous (60%) | 1,751 | 61.73 | 0.23 | **0** | **0** | 0.87% |
| **100** | 400 | Tight (10%) | 611 | 126.99 | 0.83 | **0** | **34** | 0.0%* |
| **100** | 400 | Moderate (30%) | 1,834 | 39.34 | 0.38 | **0** | **4** | 0.00% |
| **100** | 400 | Generous (60%) | 3,669 | 58.44 | 0.38 | **0** | **0** | 0.01% |
| **200** | 800 | Tight (10%) | 1,257 | 30.71 | 0.86 | **0** | **60** | 0.0%* |
| **200** | 800 | Moderate (30%) | 3,772 | 327.88 | 0.85 | **0** | **0** | 0.21% |
| **200** | 800 | Generous (60%) | 7,544 | 116.71 | 0.88 | **0** | **0** | 0.26% |
| **400** | 1,600 | Tight (10%) | 2,501 | 723.28 | 1.53 | **0** | **115** | 0.0%* |
| **400** | 1,600 | Moderate (30%) | 7,503 | 136.97 | 2.12 | **0** | **20** | 0.00% |
| **400** | 1,600 | Generous (60%) | 15,006 | 375.96 | 2.80 | **0** | **0** | 0.01% |
| **800** | 3,200 | Tight (10%) | 5,092 | 1,009.89 | 2.71 | **0** | **249** | 0.0%* |
| **800** | 3,200 | Moderate (30%) | 15,278 | 458.48 | 4.08 | **0** | **48** | 0.02% |
| **800** | 3,200 | Generous (60%) | 30,557 | 545.42 | 4.94 | **0** | **8** | 0.10% |

*\*Note: Under tight budgets, Greedy appears to achieve a nominally higher raw value because it violates precedence constraints by including child methods while dropping their parent classes. The resulting output is syntactically invalid.*

---

## 4. Key Scientific Insights

### A. The Greedy Precedence Trap
Standard value-density heuristics calculate $\rho_v = \frac{\Delta v}{\Delta c}$ independently for each symbol. Because leaf methods have smaller token footprints than entire classes, the greedy allocator eagerly consumes the budget on high-ranking methods while leaving their parent classes at `ResolutionTier.EXCLUDED`.
This produces **severe syntactic invalidity**: up to **249 orphaned methods** under tight budgets. An LLM agent receiving these orphaned methods lacks class definitions, base class inheritance, class-level constants, and enclosing scopes.

### B. Hierarchical Cascading via Exact MILP
The Exact MILP formulation solves this via the hard precedence constraint $x_{v,r} \le \sum_{r'=1}^3 x_{u,r'}$. When the optimizer selects a high-value method, it is mathematically compelled to simultaneously pay the token cost for the parent class. Crucially, the multi-resolution formulation allows the optimizer to include the parent class as a **Structural Stub** (costing only ~8 tokens) while retaining the critical method at **Full** or **Skeleton** resolution. This guarantees 100% syntactic validity with minimal token overhead.

### C. Scalability and Runtime Invariance
Even at $N = 800$ candidates (3,200 binary variables and over 4,000 linear constraints), HiGHS branch-and-cut solves the problem to provable global optimality in **1.01 seconds**. For standard agent context sizes ($N \le 100$), solve times are between **23 ms and 127 ms**, adding virtually zero latency to agent inference loops.

---

## 5. Strict Gold-Patch Quarantine Verification

As required by Safeguard 5:
1. `ExactMILPContextCompiler.compile()` takes only `(candidates, graph, budget, lexical_scores, topological_weights)`.
2. Unit test `test_gold_patch_quarantine` programmatically inspects the compiler method signature and verifies that no parameters or attributes contain references to patches, solutions, or reference modifications.
3. Lexical scores are computed strictly from the task issue description, and topological weights are computed strictly from forward/backward execution traversal from issue seeds.

