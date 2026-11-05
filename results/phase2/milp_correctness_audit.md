# MR-TopoS Phase 2 Verification: Mathematical & Implementation Correctness Audit

## 1. Mathematical Formulation vs. Implementation Audit

This document provides a line-by-line verification auditing the mathematical formulation of the **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)** context compiler against its actual implementation in [`src/mrtopos/knapsack_solver.py`](file:///c:/Users/hiten/Downloads/GEMMA/src/mrtopos/knapsack_solver.py).

### Core Constraint Verification

| Mathematical Constraint | Mathematical Definition | Implementation in `knapsack_solver.py` | Verification Status |
|:---|:---|:---|:---:|
| **Representation Exclusivity** | $\sum_{r=0}^3 x_{v,r} = 1 \quad \forall v \in V$ | Lines 119–126: For each node $i$, row entries for $j \in \{0, 1, 2, 3\}$ are set to $1.0$, with bounds $[1.0, 1.0]$. | **VERIFIED** |
| **Zero Cost for Excluded** | $c(v, 0) = 0$ | Lines 106–111: `costs = {ResolutionTier.EXCLUDED: 0, ...}`. No tokens deducted when $r=0$. | **VERIFIED** |
| **AST Containment Precedence** | $\sum_{r=1}^3 x_{v,r} \le \sum_{r'=1}^3 x_{u,r'} \quad \forall (u, v) \in E_{\text{hier}}$ | Lines 136–143: For parent $p$ and child $i$, sets $x_{i,j} = +1$ and $x_{p,j} = -1$ for $j \in \{1, 2, 3\}$ with upper bound $0.0$. | **VERIFIED** |
| **Global Token Budget** | $\sum_{v} \sum_{r} c(v, r) x_{v,r} \le B$ | Lines 103–118: Sets row coefficients to subword token counts, bounded in $[0, B]$. | **VERIFIED** |
| **Soft Callee Coupling** | $\xi_{uv} \ge x_{u, 3} - (x_{v, 2} + x_{v, 3}) \quad \forall (u, v) \in E_{\text{call}}$ | Lines 145–156: Sets $x_{u, 3} = +1$, $x_{v, 2} = -1$, $x_{v, 3} = -1$, and $\xi_{uv} = -1$, bounded by $\le 0$. | **VERIFIED** |
| **Integrality & Slack Types** | $x_{v,r} \in \{0, 1\}, \quad \xi_{uv} \in [0, 1]$ | Lines 160–166: `integrality[:num_x] = 1` (binary), `integrality[num_x:] = 0` (continuous). | **VERIFIED** |

---

## 2. Representation Fidelity Invariant: Child vs. Parent Resolution

### Question
*Is child representation fidelity allowed to exceed parent representation fidelity, and what is the scientific justification?*

### Formal Policy
**YES. Child representation fidelity is strictly permitted to exceed parent representation fidelity ($r_{\text{child}} > r_{\text{parent}}$), provided that the parent container is active ($r_{\text{parent}} \ge \text{STUB}$).**

### Mathematical Form
The precedence constraint is formulated as:
$$\sum_{j=1}^3 x_{\text{child}, j} \le \sum_{k=1}^3 x_{\text{parent}, k}$$

Under this formulation:
1. If the child is selected at **FULL** resolution ($x_{\text{child}, 3} = 1$), the LHS equals $1$.
2. The constraint requires the RHS to be $\ge 1$.
3. The parent can satisfy this by being selected at:
   - $x_{\text{parent}, 1} = 1$ (**STUB**)
   - $x_{\text{parent}, 2} = 1$ (**SKELETON**)
   - $x_{\text{parent}, 3} = 1$ (**FULL**)

### Architectural & Scientific Justification
1. **Context Window Preservation**:
   In production software repositories (e.g., FastAPI's `applications.py` or HTTPX's `_client.py`), core classes often span 2,000 to 5,000 lines of code ($8,000+$ subword tokens).
   If child fidelity were bounded by parent fidelity ($r_{\text{child}} \le r_{\text{parent}}$), selecting a single 25-line bug-fix method at `FULL` resolution would mathematically compel the optimizer to expand the entire 5,000-line enclosing class at `FULL` resolution. This would immediately exhaust a 4,000 or 8,000-token context budget on unrelated methods.
2. **Lexical Scope Sufficiency**:
   For an LLM reasoning engine to locate and repair a defect inside a method, the enclosing class only needs to provide its syntactic lexical scope:
   ```python
   class Client(BaseClient):
       ...
       def request(self, method, url, ...):
           # FULL 45 lines of target implementation here
           ...
   ```
   A Tier 1 **Structural Stub** (~10 tokens) provides the class name, inheritance hierarchy, and method encapsulation without incurring the 5,000-token penalty of the entire class body.
3. **Nested Containment & Transitivity**:
   For nested structures (Module $\to$ OuterClass $\to$ InnerClass $\to$ Method), containment constraints cascade transitively:
   $$\sum_{r=1}^3 x_{\text{method}, r} \le \sum_{r=1}^3 x_{\text{class}, r} \le \sum_{r=1}^3 x_{\text{module}, r}$$
   Activating a method guarantees that its enclosing class and module are active at least as Stubs.

---

## 3. Direction and Magnitude of Objective Penalties

The objective is to maximize contextual value while penalizing omitted callee contracts:
$$\max_{x, \xi} \quad \sum_{v \in V} \sum_{r \in \mathcal{R}} V(v, r) x_{v,r} - \gamma_{\text{slack}} \sum_{(u, v) \in E_{\text{call}}} \xi_{u,v}$$

In the HiGHS implementation, the standard linear program format is minimization: $\min_y c^T y$.
The vector $c$ is constructed as:
- For decision variables $x_{v,r}$: $c_{v,r} = -V(v, r)$ (negated to convert maximization into minimization).
- For slack variables $\xi_{u,v}$: $c_{\xi} = +\gamma_{\text{slack}}$ (positive cost added to the objective).

### Verification of Penalty Direction
When caller $u$ is selected at `FULL` ($x_{u,3} = 1$) but callee $v$ is omitted ($x_{v,2} = x_{v,3} = 0$), constraint 4 enforces:
$$1 - 0 - \xi_{uv} \le 0 \implies \xi_{uv} \ge 1$$
In minimization, the solver is forced to set $\xi_{uv} = 1$, adding $+5.0$ to the minimization cost function:
$$\min \Big( -\text{Value} + 5.0 \Big) \iff \max \Big( \text{Value} - 5.0 \Big)$$
The magnitude $\gamma_{\text{slack}} = 5.0$ exceeds the maximum value gain of an individual method upgrade ($\sim 1.0$), creating a strong optimization pressure for the solver to retain the interface skeleton of called dependencies.

---

## 4. Inference-Time Input Tracing & Strict Gold Quarantine

As mandated by experimental control rules:

### A. Lexical Relevance Scores ($s_v$)
- Input: `problem_statement` text from the task issue.
- Method: BM25 score against tokenized code text (qualified symbol name + docstring + signature).
- Formula: $s_v = \frac{\text{BM25Score}(Q, v)}{\max_{u} \text{BM25Score}(Q, u)} \in [0, 1]$.
- Available at inference time: **YES**.

### B. Topological Proximity Weights ($w_v$)
- Input: Symptom seeds identified exclusively from stack traces, file paths, or symbol identifiers explicitly mentioned in the `problem_statement`.
- Method: Directional BFS over $G = (V, E_{\text{call}} \cup E_{\text{import}})$ with call decay $\beta_{\text{call}} = 0.75$ and import decay $\beta_{\text{import}} = 0.40$.
- Available at inference time: **YES**.

### C. Strict Gold Quarantine Confirmation
- **No Ground-Truth Leakage**: The context compiler has zero access to:
  - Task ground-truth patch (`patch`)
  - Evaluation test patch (`test_patch`)
  - Ground-truth modified file paths
  - Commit author or post-commit test results
- The compiler signature strictly enforces:
  `compile(candidates, graph, budget, lexical_scores, topological_weights)`
- All inputs are derived exclusively from pre-patch snapshots and issue descriptions.

