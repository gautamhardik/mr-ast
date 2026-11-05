# Final Research Gate: MR-TopoS Pre-Implementation Recommendation

**Author:** Antigravity Research Team (Adversarial Audit Group)  
**Date:** November 5, 2026  
**Document:** `audit/mrtopos_go_no_go.md`  
**Target:** Google - The Gemma 4 Developer Agent Paper Track  
**Verdict:** **B. CONDITIONAL GO — Approved for Implementation IF AND ONLY IF Four Mandatory Research Changes Are Incorporated.**  

---

## 1. Executive Gate Decision

Following our empirical measurements, mathematical formulation of the Precedence-Constrained Knapsack problem, and rigorous reconciliation of all previous claims:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FINAL VERDICT: CONDITIONAL GO                   │
│                                                                        │
│  MR-TopoS is approved to proceed to implementation, subject to four   │
│  mandatory research and architectural conditions. Proceeding without   │
│  these conditions will result in experimental failure and reviewer     │
│  rejection.                                                            │
└────────────────────────────────────────────────────────────────────────┘
```

We explicitly reject an unconditioned "GO" because empirical validation revealed four structural risks in the original naive proposal:
1. Flat hierarchy traversal creates catastrophic dilution through the `REPO_ROOT` mega-hub.
2. 22.3% of benchmark ground-truth files are completely absent from `data/graphs/*.json`.
3. Complete docstring stripping discards critical behavioral edge-case documentation.
4. Conflation of file counts with task instances distorted previous task exposure figures.

---

## 2. Quantitative Reconciliation of Previous Claims

In accordance with strict scientific accountability, the table below reconciles all initial claims against actual measured ground truth:

| Topic | Initial Claim / Audit Figure | Actual Measured Ground Truth | Status & Correction |
| :--- | :--- | :--- | :--- |
| **Task Docs Exposure** | "51.5% of tasks modify files in `docs_src/`" | **15 out of 129 tasks (11.6%)** touch `docs_src/`. In FastAPI alone, **15 out of 67 tasks (22.4%)** touch `docs_src/`. | **CORRECTED.** The previous turn conflated unique modified file paths in FastAPI (34/68 = 50.0%) with task instances. Only 3 tasks in the entire dataset (2.3%) modify *only* docs. |
| **Token Compression** | "88.8% compression" | **86.4%–88.6%** on FastAPI modern typed code; **71.7%–74.3%** cross-repository average across Rich, Requests, and HTTPX. | **QUALIFIED.** 88.8% is the upper bound on heavy `Annotated[Doc]` typing classes. It is not uniform across traditional codebases. |
| **Topology Reachability** | "100% repository-wide reachability" | **97.7% average WCC coverage** (FastAPI: 93.4%, Rich: 99.4%, Requests: 98.0%, HTTPX: 100.0%). 0.0% graph isolates. | **QUALIFIED.** Syntactic reachability from `REPO_ROOT` to internal modules is 100%. Residual non-connected nodes are external third-party imports. |
| **GPU Inference Latency** | "21.5-minute run vs. 4.3 GPU hours" | One 129-task inference pass = **21.5 minutes**. Full experimental matrix (6 baselines $\times$ 2 core budgets = 12 runs) = **4.3 hours**. | **RECONCILED.** 21.5 min is per-run latency; 4.3 hours is total study compute. |
| **Kaggle Quota** | "30 GPU hours per week" | **Verified platform quota** for phone-verified Kaggle accounts (resets weekly). | **VERIFIED.** Consumes only 14.3% of available free quota. |

---

## 3. Four Mandatory Conditions of Approval

Implementation of MR-TopoS may commence **only** under the following strict conditions:

### Condition 1: Asymmetric, Scope-Constrained Dual-View Topology
* **The Vulnerability:** Flat undirected traversal across AST hierarchy edges causes `REPO_ROOT` to act as an artificial mega-hub, bridging completely unrelated files and flooding the prompt.
* **Mandatory Rule:** $E_{hier}$ edges must be directed strictly downward ($\text{Module} \to \text{Class} \to \text{Method}$). Traversing through `REPO_ROOT` to connect different modules is strictly forbidden. Inter-module paths may *only* follow explicit $E_{call}$ (invocation) or $E_{import}$ (dependency) edges.

### Condition 2: Snapshot-Grounded Direct AST Parsing (Resolving the 22.3% Gap)
* **The Vulnerability:** 22.3% of ground-truth modified files (like `rich/_cell_widths.py`) define constants or lookup tables and contain zero functions/classes, causing them to be completely omitted from `data/graphs/*.json`.
* **Mandatory Rule:** The pipeline cannot rely exclusively on `data/graphs/*.json`. The graph builder must parse repository snapshots directly via `tarfile` and instantiate top-level `ast.Module` nodes for every `.py` file, guaranteeing 100% representation.

### Condition 3: Tier 2 Contract Skeletons Must Retain 1-Line Docstring Summaries
* **The Vulnerability:** In traditional libraries without `Annotated[Doc]`, stripping docstrings completely provides only a marginal 5% token savings while discarding behavioral parameter explanations needed to fix bugs.
* **Mandatory Rule:** Tier 2 contract skeletons must retain the first sentence (1-line summary) of class and function docstrings. Only markdown guides, examples, and `Doc(...)` type annotations are stripped.

### Condition 4: Exact MILP Formulation with Strict Data Isolation
* **The Vulnerability:** Greedy heuristic knapsack solvers produce orphaned methods and broken syntax.
* **Mandatory Rule:** Context optimization must be solved using the exact Precedence-Constrained Multiple-Choice Knapsack (PC-MCKP) program via `scipy.optimize.milp` (verified at 34ms solve time).
* **Quarantine Invariant:** The optimizer and retriever must have zero access to `t['patch']` or `t['test_patch']`.

---

## 4. Work Roadmap Post-Conditional Approval

If the user approves this CONDITIONAL GO verdict, execution proceeds in five disciplined phases:

```
Phase 1: Direct Snapshot AST Builder & Scope-Constrained Topology (Milestone 8)
   │
Phase 2: Differential Typing Pruner with Empty-Body Syntax Guards
   │
Phase 3: PC-MCKP MILP Context Compiler (scipy.optimize.milp)
   │
Phase 4: 6-Way Matched Budget Experiment & Significance Testing (2k, 4k, 8k, 16k)
   │
Phase 5: Kaggle GPU Inference & Camera-Ready Publication Paper
```

**Final Gate Assessment:** MR-TopoS possesses genuine, publishable scientific merit as a novel, mathematically grounded context compilation framework for developer agents, provided the four mandatory conditions are strictly enforced.

