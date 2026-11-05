# Information Leakage Audit Report

**Audit Date:** 2026-11-04  
**Scope:** All 129 Benchmark Tasks in `data/tasks.jsonl`

---

## 1. Summary of Leakage Risks & Treatment Policy

| Resource / Field | Research Protocol Treatment | Empirical Audit Result | Risk Verdict |
| :--- | :--- | :--- | :--- |
| `problem_statement` | Permitted as primary agent input | Issue description or PR prompt; contains natural language bug descriptions. | **Clean** |
| `hints_text` | Permitted only if verified free of solution spoilers | Every single record out of 129 entries has `hints_text: ""` (empty string). | **Zero Leakage (Safe)** |
| `base_commit` | Permitted to checkout repository state | Points to the commit immediately preceding the bug fix / test patch. | **Clean** |
| `patch` | Strictly reserved for Phase 2 evaluation labels | Golden solution diffs; never exposed during inference. | **Cleanly Isolated** |
| `test_patch` | Strictly reserved for Phase 2 test suite execution | Reference pytest test cases; applied only during sandbox verification. | **Cleanly Isolated** |
| `graphs/` & `embeddings/` | Permitted if verified to reflect `base_commit` | Generated exactly from ASTs at `base_commit`; filenames match `<repo>_<base_commit>`. | **Clean (Pre-solution state)** |

---

## 2. In-Depth Verification of Problem Statements & Hints

### A. `hints_text` Verification
- **Total tasks evaluated**: 129
- **Tasks with non-empty `hints_text`**: **0 (0.0%)**
- **Distinct values in `hints_text`**: `['']` (strictly empty string)
- **Conclusion**: There is zero risk of conversational leakage or PR discussion hints revealing solution files or line numbers.

### B. Commit Chronology & State Purity
- **Snapshot Archives**: Each task's `data/snapshots/{instance_id}.tgz` represents the repository git working tree checked out at `base_commit`.
- **Graph & Embedding Consistency**: Each graph file (`data/graphs/{repo}_{base_commit}.json`) and embedding file (`data/embeddings/{repo}_{base_commit}.npz`) is indexed specifically by the `base_commit` SHA.
- **Pre-Solution Invariant**: Code nodes within the graphs contain the original (unfixed) function and class bodies. For example, in `fastapi_15661`, the AST does not contain the modifications introduced in `patch`.

---

## 3. Protocol Rules for Experimental Integrity

1. The inference agent environment must never mount or read `patch` or `test_patch`.
2. Ground-truth modified file paths (cataloged in [`task_inventory.csv`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/task_inventory.csv)) must only be used offline by evaluation scripts to score node and file localization metrics (Recall@k, MRR).

