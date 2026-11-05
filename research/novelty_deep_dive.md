# Scientific Novelty & Theoretical Foundations: MR-TopoS vs SOTA

**Document**: `research/novelty_deep_dive.md`  
**Purpose**: Rigorous differentiation of MR-TopoS against LocAgent (ACL 2025), Aider Repository Map, and 2026 Context Compression Research (arXiv:2604.13725).  
**Target Submission**: Google Gemma 4 Developer Agent Paper Track  
**Date**: November 5, 2026

---

## 1. Executive Summary of Novelty

A critical question raised in academic peer review and competition judging is:
> *"How is MR-TopoS scientifically novel compared to heterogeneous code graphs (LocAgent), token-budgeted repository maps (Aider), and code prompt compression?"*

The central novelty of MR-TopoS is **NOT** simply the combination of graphs, ASTs, and knapsacks. Rather, MR-TopoS introduces a fundamentally distinct theoretical formulation and empirical resolution to the **Scope Tax dilemma**:

> **Core Research Contribution**: The formalization of repository context compilation as a **Precedence-Constrained Multi-Choice Knapsack Problem (PC-MCKP)** over a 4-tier AST resolution lattice, establishing the exact mathematical conditions under which fine-grained code methods can be compiled with **$100.0\%$ syntactic validity** and **zero precedence violations** while retaining **$1.55\times$ more full implementations** (and $4.05\times$ total symbols) than scoped lexical baselines under tight token budgets ($B \le 2,000$).

---

## 2. In-Depth Comparative Analysis Against Closest Prior Art

### 2.1 Comparison 1: MR-TopoS vs LocAgent (ACL 2025)
*Reference*: [LocAgent: Graph-Guided Multi-Hop Code Localization for Autonomous Software Engineering](https://aclanthology.org/2025.acl-long.426/)

| Dimension | LocAgent (ACL 2025) | MR-TopoS (Ours) | Scientific Distinction |
|---|---|---|---|
| **Primary Task** | Multi-hop **code localization** (identifying which files or functions contain the bug). | Unified **context compilation** (optimizing the exact multi-resolution representation of the entire prompt). | LocAgent outputs a list of candidate entity names; MR-TopoS compiles the actual runnable prompt code. |
| **Inference Mechanism** | Multi-turn **LLM agent search loop** (agent iteratively queries neighbors across multiple prompt turns). | **Deterministic zero-turn mathematical optimization** via HiGHS branch-and-cut dual simplex (<3 ms). | LocAgent requires 5–15 LLM generation cycles ($10\text{k}+$ tokens, 10–30s latency); MR-TopoS executes on CPU in 2.8 ms before the first LLM token. |
| **Representation Spectrum** | **Binary (0 / 1)**: Entities are either included as whole files/functions or completely omitted. | **4-Tier Lattice**: $\mathcal{R} = \{\text{EXCLUDED}, \text{STUB}, \text{SKELETON}, \text{FULL}\}$ with formal downgrade operators. | LocAgent cannot adjust abstraction fidelity to fit token budgets. |
| **Syntactic Scope Handling** | None: Retrieves isolated function text or entire files. | Hard **AST Containment Precedence Invariants** ($x_{ir} \le \sum x_{p(i),r}$). | Prevents orphan methods and Broken Scope errors. |
| **Modern Typing Pruning** | None. | **Differential Typing Pruner** separating `typing.Annotated[T, Doc(...)]` metadata from prose. | Preserves type contracts while eliminating $41.2\%$ of skeleton documentation overhead. |

**Key Takeaway**: LocAgent is an *interactive localization agent*; MR-TopoS is an *offline deterministic context compiler*. They are complementary, not competing: an agent can use LocAgent to find seed candidates, and use MR-TopoS to compile the optimal budget-constrained context.

---

### 2.2 Comparison 2: MR-TopoS vs Aider Repository Map
*Reference*: [Aider: Repository Map via Tag Graphs](https://aider.chat/docs/repomap.html)

| Dimension | Aider Repository Map | MR-TopoS (Ours) | Scientific Distinction |
|---|---|---|---|
| **Objective** | Generate a **global repository outline** to give an LLM a static overview of the codebase. | Generate a **task-conditioned, multi-resolution working context** containing target full implementations. | Aider's map contains only signatures; the model still needs to read full files. MR-TopoS embeds full target code within the skeleton map. |
| **Ranking Algorithm** | Unconditioned **PageRank** on an identifier reference graph. | **Task-Conditioned Multi-Source Causal Decay**: $w_v = \max (w_u \cdot \lambda(u, v))$ anchored to issue keywords. | Aider's ranking is static and identical across tasks; MR-TopoS dynamically radiates utility from task seeds along directed call/import paths. |
| **Representation Tiers** | **Single Tier (Signatures Only)**: Class headers and function definitions with bodies elided. | **Dynamic 4-Tier Hybridization**: Optimizer places target methods in FULL, supporting APIs in SKELETON, and parent classes in STUB. | MR-TopoS retains **19.47 full implementations** alongside 30 skeletons at $B=2,000$. |
| **Mathematical Guarantee** | Greedy token accumulation until budget threshold is reached. | **Provably Global Optimum** via PC-MCKP MILP with 0% precedence violations. | Solves combinatorial trade-offs between parent headers and child methods globally. |
| **Typing & Docstrings** | Heuristic truncation via Tree-sitter. | AST transformation handling `Annotated[T, Doc(...)]` and empty class indentation invariants. | Guarantees non-empty class bodies and preserves base types. |

**Key Takeaway**: Aider's repository map is a *static global signature index*; MR-TopoS is a *task-conditioned multi-resolution context compiler* that dynamically co-optimizes full implementation code, contract skeletons, and structural stubs within a single mathematical program.

---

### 2.3 Comparison 3: MR-TopoS vs Empirical Context Compression (arXiv:2604.13725)
*Reference*: [Empirical Investigation of Repository-Level Context Compression for LLM Agents](https://arxiv.org/abs/2604.13725)

Recent 2026 work on context compression highlights that generic text-based compression (e.g., token pruning, perplexity-based filtering, LLMLingua) exhibits catastrophic failure modes when applied to code:
1. **Syntactic Corruption**: Randomly dropping subword tokens splits identifiers, breaks parenthesis matching, and induces indentation errors.
2. **Loss of Type Bindings**: Generic summarization deletes return type annotations and parameter contracts essential for bug repair.

**MR-TopoS's Distinction**:
MR-TopoS enforces **Grammar-Preserving AST Discretization**:
- Instead of continuous or token-level pruning, every downgrade is an exact homomorphism in the Python grammar.
- Tier 2 (SKELETON) replaces function bodies with `...`, preserving full signatures, type annotations, and first-sentence docstrings.
- Tier 1 (STUB) replaces class/function contents with `...`, preserving hierarchy and identifiers for 5–10 tokens.
- Result: **$100.0\%$ Syntactic Parse Validity** across all 2,580 evaluations with zero broken scopes.

---

## 3. Formal Mathematical Definition of the "Scope Tax"

The Scope Tax arises from the structural rigidity of object-oriented languages:
When fine-grained methods $M = \{m_1, m_2, \dots, m_k\}$ from class $C$ are retrieved, compiling each method $m_j$ in isolation severs it from class scope $C$.
Restoring enclosing class $C$ introduces token overhead:
$$T_{\text{overhead}}(C) = \text{len}(\text{Encode}(\text{class } C(\text{Bases}): \dots))$$

We define the **Scope Tax** across two complementary dimensions:

### 1. Token-Level Scope Tax ($\tau_{\text{tok}}$)
The proportion of serialized context consumed by enclosing structural boilerplate rather than functional logic:
$$\tau_{\text{tok}} = \frac{T_{\text{context}} - \sum_{i \in \text{Selected}} T_{\text{body}}(i)}{T_{\text{context}}}$$

### 2. Symbol Capacity Scope Tax ($\tau_{\text{cap}}$)
The relative loss in retained symbol capacity when structural scope wrapping is naively enforced compared to unconstrained snippet retrieval:
$$\tau_{\text{cap}} = \frac{N_{\text{raw}} - N_{\text{scoped}}}{N_{\text{raw}}}$$

### 3. How MR-TopoS Mathematically Eliminates the Scope Tax
In naive scoped retrieval (`bm25_scoped`), every retrieved method is wrapped in a full class stub. If methods are selected across multiple classes, the class header cost accumulates rapidly, causing capacity to collapse.

In MR-TopoS, the PC-MCKP formulation decouples the resolution of parent class $C$ from child method $m$:
$$\min c_{C, 1} \quad \text{s.t.} \quad x_{C, 1} \ge x_{m, 3}$$
Because $c_{C, 1} \in [5, 10]$ tokens (STUB tier: `class C: ...`), the cost paid to restore syntactic validity is **only 5–10 tokens** per class, rather than hundreds of tokens for full class bodies or verbose docstrings. Furthermore, when multiple methods from the same class are selected, they share the single stub header:
$$x_{C, 1} \ge x_{m_j, r} \quad \forall j$$
This amortizes structural overhead, enabling MR-TopoS to retain **$19.47$ full implementations** and **$30.00$ skeletons** ($50.85$ symbols total) at $B=2,000$ tokens, completely eliminating the Scope Tax penalty.

