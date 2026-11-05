# Empirical Connectivity Validation: Dual-View Program Topology

**Author:** Antigravity Research Team (Adversarial Audit Group)  
**Date:** November 5, 2026  
**Document:** `audit/mrtopos_connectivity_validation.md`  
**Target:** Google - The Gemma 4 Developer Agent Paper Track  
**Status:** Pre-Implementation Empirical Audit  

---

## 1. Executive Summary

This validation rigorously investigates the graph-theoretic properties of the proposed **Dual-View Program Topology** across all 129 benchmark tasks in the SWE-bench Gemma dataset.

We specifically test:
1. The exact construction of AST syntactic hierarchy edges ($E_{hier}$) and import dependency edges ($E_{import}$).
2. Empirical connectivity before and after Dual-View augmentation across all four benchmark cohorts (FastAPI, Rich, Requests, HTTPX).
3. Mapping coverage: Whether ground-truth modified files from all 129 tasks can be mapped to graph nodes.
4. The critical scientific risk: Whether Dual-View topology actually improves retrieval or causes catastrophic contextual dilution through global root hubs.

---

## 2. Empirical Connectivity Audit Across Repositories

We measured graph connectivity on both the original call graphs ($G_{call}$) and the augmented Dual-View graphs ($G_{dual} = G_{call} \cup G_{hier} \cup G_{import}$) using NetworkX.

### 2.1 Measured Graph Topology Statistics

| Repository | Cohort Tasks | $G_{call}$ Nodes | $G_{call}$ Edges | $G_{call}$ Isolates (%) | $G_{call}$ Largest WCC (%) | $G_{dual}$ Nodes | $G_{dual}$ Edges | $G_{dual}$ Isolates (%) | $G_{dual}$ Largest WCC (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **FastAPI** | 67 | 4,287 | 2,477 | 3,062 (**71.4%**) | 574 (**13.4%**) | 6,148 | 10,987 | 0 (**0.0%**) | 5,742 (**93.4%**) |
| **Rich** | 48 | 1,925 | 5,478 | 67 (**3.5%**) | 1,781 (**92.5%**) | 2,349 | 7,767 | 0 (**0.0%**) | 2,335 (**99.4%**) |
| **Requests** | 13 | 754 | 1,878 | 59 (**7.8%**) | 626 (**83.0%**) | 945 | 2,492 | 0 (**0.0%**) | 926 (**98.0%**) |
| **HTTPX** | 1 | 740 | 1,618 | 21 (**2.8%**) | 483 (**65.3%**) | 924 | 2,224 | 0 (**0.0%**) | 924 (**100.0%**) |
| **Total / Avg** | **129** | **7,706** | **11,451** | **3,209 (41.6%)** | **63.6%** | **10,366** | **23,470** | **0 (0.0%)** | **97.7%** |

*Definitions:*
- **Isolates:** Nodes with total degree $d_{in} + d_{out} = 0$.
- **WCC:** Weakly Connected Component.

### 2.2 Key Findings
1. **Elimination of Graph Isolates:** Augmenting the static call graph with AST hierarchy edges ($E_{hier}$) completely eliminates isolated nodes ($0.0\%$ isolates across all repositories).
2. **Component Expansion:** The largest connected component expands from 13.4% to **93.4%** in FastAPI, and exceeds **98.0%** across Rich, Requests, and HTTPX.
3. **The 6.6% Residual in FastAPI:** In FastAPI, 6.6% of nodes in $G_{dual}$ remain in secondary components. These correspond strictly to external third-party library imports (e.g., `starlette`, `pydantic`) referenced in tutorial scripts that do not resolve back into internal repository modules. Intra-repository reachability from `REPO_ROOT` to all internal Python modules is exactly **100.0%**.

---

## 3. Mapping Coverage Audit: Ground-Truth Files to Graph Nodes

We conducted a complete mapping audit of all ground-truth modified files across all 129 tasks against `data/graphs/*.json`.

### 3.1 Mapping Results

| Repository | Tasks | Ground-Truth File References | Successfully Mapped to Graph Nodes | Unmapped File References (%) | Primary Cause of Unmapped Files |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **FastAPI** | 67 | 165 | 132 | 33 (**20.0%**) | Tutorial scripts in `docs_src/` and utility release scripts not parsed in graph JSON. |
| **Rich** | 48 | 91 | 62 | 29 (**31.9%**) | Non-code data lookup tables (`_unicode_data/`, `_cell_widths.py`, `_export_format.py`). |
| **Requests** | 13 | 15 | 15 | 0 (**0.0%**) | All modified files contain standard functions/classes. |
| **HTTPX** | 1 | 7 | 7 | 0 (**0.0%**) | All modified files contain standard functions/classes. |
| **Total** | **129** | **278** | **216** | **62 (22.3%)** | **Static graph omission of data-only files & scripts.** |

### 3.2 The Critical Omission in `data/graphs/*.json`
Our audit revealed why 22.3% of ground-truth files are unmapped:
The pre-generated graphs in `data/graphs/*.json` only created nodes for `ast.FunctionDef` and `ast.ClassDef`. 
Files that contain only module-level assignments, constants, lookup tables, or tuples (such as `rich/_cell_widths.py`, which defines the `CELL_WIDTHS` unicode table) **contain zero functions or classes**. Consequently, the graph generator emitted **zero nodes** for these files.

**Mandatory Pre-Implementation Requirement:**
MR-TopoS cannot rely exclusively on `data/graphs/*.json`. The AST builder must parse repository snapshots directly and instantiate explicit `ast.Module` nodes for every `.py` file, guaranteeing **100% mapping coverage** of all 278 ground-truth files.

---

## 4. Does Dual-View Topology Actually Improve Retrieval?

### 4.1 The "Mega-Hub" Dilution Risk
If AST hierarchy edges ($E_{hier}$) and call edges ($E_{call}$) are treated identically in path retrieval:
- Two unrelated functions $f_1 \in \text{module}_A$ and $f_2 \in \text{module}_B$ would have an undirected path:
  $$f_1 \to \text{module}_A \to \text{pkg}_A \to \text{REPO\_ROOT} \to \text{pkg}_B \to \text{module}_B \to f_2$$
- Because `REPO_ROOT` connects to every top-level package, it has a degree equal to the number of top-level directories.
- Any unweighted shortest-path or Steiner-tree algorithm would traverse `REPO_ROOT`, pulling in generic directory headers and flooding the context window with irrelevant sibling modules.

### 4.2 The Scope-Constrained Dual-View Formulation
To prevent mega-hub dilution and guarantee that topology improves retrieval:
1. **$E_{hier}$ is Asymmetric & Intra-File Only:** AST hierarchy edges are directed strictly downward ($\text{Module} \to \text{Class} \to \text{Method}$). Upward traversal across modules is strictly forbidden.
2. **Inter-File Transitions Require Causal Edges:** Cross-file reachability can *only* occur via explicit $E_{call}$ (invocation) or $E_{import}$ (dependency) edges.
3. **Container Context Inclusion:** If a method $m$ is selected by an execution path, its enclosing class $C$ and module header $M$ are included at Tier 0 (Stub) or Tier 1 (Skeleton) solely to provide syntactic scope, not to trigger graph expansion into sibling methods.

### 4.3 Measured Validation Verdict
* **Is 100% repository-wide reachability true?** Yes, in the sense of syntactic containment from `REPO_ROOT` down to all internal AST nodes. No, in the sense of flat call-edge traversals (6.6% third-party leaves in FastAPI).
* **Does it improve retrieval?** Only when implemented under **Scope-Constrained Dual-View** rules where hierarchy provides lexical scope and call/import provides inter-module causality. Flat undirected traversal is actively harmful.

