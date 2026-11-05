# Empirical Investigation into the AST Constraint Paradox

**Date:** 2026-11-05T11:57:00+05:30  
**Author:** Evidence-First Principal Research Scientist  
**Deliverable:** `research/ast_constraint_necessity.md`  
**Focus:** Resolving the relationship between AST Precedence Constraints, Syntactic Closure, and Retrieval Recall.

---

## 1. The Paradox Defined

In the Strategic Reset Factorial Ablation across 129 SWE benchmark tasks:
- **Condition B (`B_mr_only`)**: Multi-resolution representation alone, with **no explicit AST precedence constraints** ($x_{c,\text{any}} \ge x_{m,\text{any}}$ disabled), achieved **100.0% syntax validity** ($516/516$ valid ASTs) and **53.89%** Gold File Recall at $B=2,000$.
- **Condition C (`C_mr_containment`)**: Added explicit linear precedence constraints to the MILP optimizer, enforcing that a parent class container must be selected if any of its methods are selected. Condition C **decreased recall by $-5.43$ percentage points** (to 48.46%, $p = 0.0050$), while also achieving **100.0% syntax validity**.

This surfaces a critical scientific question:  
*If unconstrained multi-resolution selection already achieves 100% syntax validity, why did we impose precedence constraints, and why did they degrade recall?*

---

## 2. Experimental Investigation & Root Cause

We executed a controlled diagnostic harness (`scripts/investigate_ast_paradox.py`) analyzing the decisions of Condition B vs. Condition C:

### 2.1 The Free-Rider Exploitation by the Optimizer
In Condition B, the MILP objective maximizes utility $\sum u_i x_i$ subject strictly to $\sum c_i x_i \le B$.  
Because candidate methods carry positive lexical BM25 scores while their enclosing parent class nodes carry lower or redundant scores, the unconstrained optimizer exploits a mathematical loophole:
- It sets $x_{\text{method}} = 1$ for high-scoring methods.
- It sets $x_{\text{parent}} = 0$ (EXCLUDED) for their enclosing class containers.
- Across evaluated tasks, **$95.5\%$ of selected methods in Condition B were orphaned** (17.10 out of 17.90 methods had unselected parents).

The unconstrained optimizer treated parent context as a "free good" because the mathematical formulation did not penalize omitted ancestors.

### 2.2 Why Condition B Still Achieved 100% Syntax Validity
Syntactic validity was evaluated by passing the final compiled context string to `ast.parse()`. Condition B achieved 100% validity due to two independent mechanisms:

1. **Python Grammar Invariance**:  
   In Python grammar, a method definition `def method_name(self, arg1, arg2): pass` is grammatically indistinguishable from a top-level module function. Even if emitted completely unindented with zero class wrapper, Python's AST parser accepts it with **100.0% syntax validity**.
2. **Serializer Implicit Parent Reconstruction**:  
   In `src/mrtopos/context_serializer.py` (lines 186–201), the serializer groups symbols by file and inspects `method_nodes.keys()`. When it detects a selected method whose parent class was omitted by the optimizer, the serializer automatically reconstructs:
   ```python
   class ClassName:
       def selected_method(self):
           ...
   ```
   The serializer deterministically wraps the orphan method in its parent class header!

### 2.3 The True Cost of Explicit Precedence Constraints (Condition C)
When linear precedence constraints ($x_{c,\text{any}} \ge x_{m,\text{any}}$) were enabled in Condition C:
- The MILP solver was forbidden from selecting a method unless it simultaneously allocated budget to the parent class node.
- Even at the minimal STUB resolution, class signatures and docstrings consumed knapsack capacity ($15$ to $45$ tokens per class).
- Under tight budgets ($B=2,000$), this overhead forced the solver to drop $1$ to $3$ candidate methods across distinct files.
- **Measured Empirical Loss**: Recall dropped by **$-5.43\text{ pp}$** at $B=2,000$ (from $53.89\%$ to $48.46\%$, paired $t(128) = 2.86, p = 0.0050, d_z = -0.25$).
- At higher budgets ($B \ge 4,000$), budget slack absorbed the parent overhead, reducing the penalty to $-1.55\text{ pp}$ (4k) and $-1.47\text{ pp}$ (8k).

---

## 3. Information Preservation vs. Syntactic Correctness

While raw unnested method emission passes `ast.parse()`, it incurs severe semantic degradation:
- Emitting `def get(self, url): ...` at module level strips the method of its class namespace (`requests.sessions.Session`).
- Downstream LLMs (e.g. Gemma 4) cannot bind `self` to instance attributes without the class contract.

However, **explicit MILP constraints are NOT required to preserve this structure**:
- The serializer's structural layout engine deterministically reconstructs enclosing class headers at layout time.
- Adding explicit binary constraints inside the MILP adds combinatorial complexity and inflates surrogate costs, degrading knapsack efficiency.

---

## 4. Scientific Verdict & Recommendation

| Component | Syntactic Contribution | Recall Impact | Computational Cost | Recommendation |
|---|:---:|:---:|:---:|:---:|
| **MILP Precedence Constraints ($x_c \ge x_m$)** | **Redundant** (0% marginal validity) | **Negative** ($-5.43\text{ pp}$ at 2k) | Moderate ($O(N)$ linear inequalities) | **REMOVE from main optimizer** |
| **Serializer Deterministic Wrapping** | **Sufficient** (100% validity & structure) | **Neutral** (~9.4 tokens layout overhead) | Minimal ($O(N)$ grouping) | **RETAIN in serializer** |

**Conclusion**: Syntactic closure should be enforced by the **serializer's deterministic AST emission rules**, not by linear knapsack constraints. Removing explicit precedence constraints recovers $+5.43\text{ pp}$ recall under tight budgets without sacrificing grammar validity or structural namespace integrity.

