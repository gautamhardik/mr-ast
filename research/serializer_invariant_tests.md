# Adversarial Serializer Invariant and Fallback Stage Verification Report

**Author:** Evidence-First Principal Research Scientist  
**Date:** 2026-11-05  
**Artifacts Generated:** `results/serializer_invariants_results.json`, `scripts/test_serializer_invariants.py`  
**Scope:** Formal AST Invariant Proofs, Adversarial Stress Testing, and Empirical Audit of 2,580 Benchmark Runs  

---

## 1. Executive Summary

A core claim of MR-TopoS is that its context serializer maintains **Abstract Syntax Tree (AST) syntactic closure** under strict token budgets. When combinatorial knapsack optimization selects fine-grained methods, their parent scopes must be reconstructed to prevent syntax errors. Furthermore, when rendering formatting overhead pushes serialized tokens past the budget, the fallback trimming loop must not break structural containment.

This report establishes:
1. **Adversarial Invariant Proofs**: Across four challenging adversarial structural cases (low-utility parent STUB containing high-utility FULL child, multi-method shared containers, nested classes, and explicit parent downgrade to `EXCLUDED`), the serializer maintains 100% AST parse validity and structural containment.
2. **Emergency Fallback Boundary**: In synthetic stress tests where token budgets are artificially squeezed below the minimum tokens needed for a single compound statement ($B=35$ tokens), Stage 4 (raw line truncation) breaks AST syntax.
3. **Empirical Benchmark Audit (2,580 Conditions)**: In the actual SWE benchmark ($B \ge 2,000$ tokens), formatting overhead averages only **9.45 tokens** (max 60 tokens). This overhead is absorbed **100.0% by Stage 1 and Stage 2 AST resolution downgrades**. Stage 4 line truncation was triggered **0 times** across all 1,032 MR-TopoS evaluations, explaining why MR-TopoS achieves **100.0% syntactic validity** while unconstrained baselines suffer up to **39.1% syntax failures**.

---

## 2. Adversarial Invariant Test Suite Results

The adversarial test suite was implemented in `scripts/test_serializer_invariants.py` and executed against the official Google Gemma 4 tokenizer (`vocab_size = 262,144`).

### Table 1: Invariant Verification Matrix

| Test Case | Scenario Description | Serialization Behavior | AST Parse Result | Structural Invariant Verdict |
|:---:|---|---|:---:|:---:|
| **Case 1** | Low-utility STUB parent ($u=0.05$) + High-utility FULL child ($u=0.95$) | Serializer renders `class Worker:` and indents `def run(self):` | **PASS (100% Valid)** | **MAINTAINED**: Parent class header preserved despite utility disparity |
| **Case 2** | Multi-method shared parent (`start` at FULL, `stop` at SKELETON) | Emits single `class Manager:` header; both methods correctly indented | **PASS (100% Valid)** | **MAINTAINED**: No duplicate class headers; suites non-empty |
| **Case 3** | Nested class hierarchy (`Outer.Inner.execute`) | Emits `class Inner:` wrapping `execute` | **PASS (100% Valid)** | **MAINTAINED**: Sub-class suites strictly well-formed |
| **Case 4** | Parent downgraded to `EXCLUDED` during trimming while child remains `FULL` | Serializer detects active child, dynamically reconstructs `class Worker:` | **PASS (100% Valid)** | **MAINTAINED**: Child method never emitted as an unindented orphan |
| **Case 5** | Over-budget stress test ($B=35$ tokens, 5 symbols totaling 150 tokens) | Stages 1–3 exhaust AST options; Stage 4 truncates lines mid-statement | **FAIL (SyntaxError)** | **BOUNDARY IDENTIFIED**: Raw line truncation cannot guarantee AST syntax |

---

## 3. Fallback Tracing & Step-by-Step Mechanics

The deterministic Budget Guard in `src/mrtopos/context_serializer.py` enforces budgets through a prioritized 4-stage downgrade loop:

```mermaid
flowchart TD
    Start["Serialized Tokens > Budget B?"] -->|No| Compliant["Emit Context (AST Valid)"]
    Start -->|Yes| Stage1["Stage 1: Prune Lowest-Utility STUBs (STUB -> EXCLUDED)"]
    Stage1 --> Check1{"Tokens <= B?"}
    Check1 -->|Yes| Compliant
    Check1 -->|No| Stage2["Stage 2: Downgrade Lowest-Utility SKELETONs (SKELETON -> STUB)"]
    Stage2 --> Check2{"Tokens <= B?"}
    Check2 -->|Yes| Compliant
    Check2 -->|No| Stage3["Stage 3: Downgrade Lowest-Utility FULLs (FULL -> SKELETON)"]
    Stage3 --> Check3{"Tokens <= B?"}
    Check3 -->|Yes| Compliant
    Check3 -->|No| Stage4["Stage 4: Emergency Line Truncation (Binary Search)"]
    Stage4 --> NonASTCompliant["Emit Truncated Context (Syntax at Risk)"]
```

### Detailed Downgrade Mechanics
1. **Sorting Key**: Candidates are ordered by `(tier_order, utility_ascending)`:
   - $\text{tier\_order}(\text{STUB}) = 1$
   - $\text{tier\_order}(\text{SKELETON}) = 2$
   - $\text{tier\_order}(\text{FULL}) = 3$
   This guarantees that high-resolution full implementations are protected while low-utility metadata stubs are pruned first.
2. **Dynamic Scope Recovery (Case 4)**:
   In `_serialize_file`:
   ```python
   all_class_ids = set(class_nodes.keys()).union(method_nodes.keys())
   ```
   Even if a class node's tier was set to `EXCLUDED` during Stage 1 trimming, its ID remains in `method_nodes.keys()` because its child method is still active. The serializer retrieves the class name from `graph.nodes` and emits `class {cname}:` around the child method. This architectural design ensures that child methods are **never emitted as bare top-level indented functions**.

---

## 4. Empirical Benchmark Audit: Fallback Activations Across 2,580 Conditions

We analyzed `results/final_benchmark/budget_audit.csv` across all 129 tasks, 4 token budgets ($2\text{k}, 4\text{k}, 8\text{k}, 16\text{k}$), and 5 methods (2,580 total evaluations).

### Table 2: Method-Level Budget Guard & Fallback Activation Audit

| Method | Total Conditions | Zero-Overhead Runs | Positive Overhead Runs | Positive Overhead Rate (%) | Mean Overhead Absorbed (Tokens) | Max Overhead (Tokens) | Compliance Rate (%) | Syntactic AST Validity (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`bm25_raw`** | 516 | 516 | 0 | 0.0% | 0.0 | 0 | 100.0% | 80.6% |
| **`bm25_scoped`** | 516 | 516 | 0 | 0.0% | 0.0 | 0 | 100.0% | 76.7% |
| **`full_file`** | 516 | 516 | 0 | 0.0% | 0.0 | 0 | 100.0% | 60.9% |
| **`mrtopos_con_greedy`** | 516 | 308 | 208 | 40.3% | 9.19 | 60 | 100.0% | **100.0%** |
| **`mrtopos_milp` (Ours)** | 516 | 311 | 205 | 39.7% | 9.45 | 60 | 100.0% | **100.0%** |
| **Total Benchmark** | **2,580** | **2,167** | **413** | **16.0%** | **3.73** | **60** | **100.0%** | — |

### Key Empirical Findings
1. **Additive Cost Model vs. Serialization Reality**:
   - The MILP solver optimizes a **surrogate additive cost function**: $\sum_{i,j} c_{ij} x_{ij} \le B$, where $c_{ij}$ is the subword token count of the isolated symbol.
   - When the serializer assembles the final Python source files, formatting overhead (file headers, class declarations, 4-space indentations, inter-symbol blank lines) adds an average of **9.45 tokens** (std: 11.2 tokens; max: 60 tokens).
   - In 39.7% of MILP runs, this formatting overhead pushes the raw token count slightly above $B$ (e.g., 2,015 tokens on a 2,000 budget).
2. **Zero Invocations of Stage 4 Line Truncation**:
   - In all 413 positive-overhead conditions, the excess tokens (1–60 tokens) were absorbed **entirely by Stage 1 and Stage 2 AST downgrades**.
   - **Stage 4 line truncation was invoked 0 times out of 1,032 MR-TopoS runs.**
   - Consequently, the AST-breaking failure mode observed in synthetic Case 5 **never occurs** under real operational conditions ($B \ge 2,000$).
3. **Root Cause of Baseline Syntax Failures**:
   - The lexical baselines (`full_file`, `bm25_raw`, `bm25_scoped`) pack code monolithically with a while-loop. When the next symbol exceeds budget, they invoke line truncation.
   - In `full_file`, line truncation severed incomplete source files in **39.1% of tasks**.
   - In `bm25_scoped`, line truncation cut off class wrappers or method suites in **23.3% of tasks**.
   - MR-TopoS's multi-resolution AST resolution downgrading completely eliminates this vulnerability.

---

## 5. Mathematical Framing & Formulation Corrections

Based on this evidence, the following theoretical corrections are established for the manuscript:

1. **Surrogate-Cost Optimization**:
   The PC-MCKP MILP is mathematically an optimization over an **additive surrogate cost model**, not an exact representation of non-linear BPE token concatenation.
   $$\min_{\mathbf{x}} c^T \mathbf{x} \quad \text{s.t.} \quad \sum_{i \in \mathcal{V}} \sum_{r \in \mathcal{R}} c_{ir} x_{ir} \le B$$
2. **Deterministic Feasibility Projection**:
   The serializer and Budget Guard act as a deterministic projection operator $\Pi_B(\mathbf{x}^*)$ mapping the solver's surrogate assignment $\mathbf{x}^*$ into the feasible token polytope of the true tokenizer:
   $$\mathbf{x}_{\text{final}} = \Pi_B(\mathbf{x}^*) \quad \text{such that} \quad \text{Tokens}(\mathcal{C}(\mathbf{x}_{\text{final}})) \le B$$
3. **Scope of Theorem 1 (Syntactic Closure)**:
   Theorem 1 holds for all contexts emitted by Stages 1–3. Stage 4 line truncation is explicitly bounded as an emergency fallback for extreme sub-contract budgets ($B < 50$ tokens) where compound statements cannot fit.

---

*Report Verified by Evidence-First Principal Research Scientist.*

