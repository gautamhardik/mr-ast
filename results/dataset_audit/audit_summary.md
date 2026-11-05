# Dataset Audit Executive Summary

**Audit Date:** 2026-11-04  
**Dataset:** `swegemma` Benchmark (`data/`)  
**Status:** Audit Complete & Validated (6/6 Deliverables Produced)

---

## 1. Key Audit Findings

### 100% Asset Coverage Across 129 Tasks
The apparent discrepancy between 129 tasks and 127 graph/embedding files is completely resolved:
- **Snapshots**: 129 `.tgz` archives named by `instance_id` (100% match).
- **Graphs & Embeddings**: 127 `.json` and `.npz` files named by `<repo>_<base_commit>`.
- Two pairs of tasks share identical base commits:
  1. `rich_3882` & `rich_3894` $\to$ `Textualize/rich` @ `4d6d631a3d2deddf8405522d4b8c976a6d35726c`
  2. `requests_6629` & `requests_6589` $\to$ `psf/requests` @ `7a13c041dbef42f9f3feb14110f02626f6892e9a`
- Every single one of the 129 tasks has full snapshot, code graph, and embedding coverage.

### Repository Distribution & Stratification Requirements

| Repository | Task Count | Percentage | Recommended Evaluation Role |
| :--- | :---: | :---: | :--- |
| **FastAPI** (`fastapi/fastapi`) | 67 | 51.9% | Primary Evaluation Benchmark |
| **Rich** (`Textualize/rich`) | 48 | 37.2% | Primary Evaluation Benchmark |
| **Requests** (`psf/requests`) | 13 | 10.1% | Secondary Supplementary Evaluation |
| **HTTPX** (`encode/httpx`) | 1 | 0.8% | Qualitative Case Study |

Pooled averages across all 129 tasks would be heavily biased towards FastAPI and Rich (89.1% combined). Reporting must be stratified by repository.

---

## 2. Technical Asset Characteristics

### Code Property Graphs (`data/graphs/*.json`)
- **Structure**: NetworkX Multi-Directed Graph format.
- **Node Attributes**: `id` (dotted symbol path, e.g. `module.Class.method`), `name`, `text` (raw source code block/signature).
- **Edge Attributes**: `source`, `target`, `type` (`calls`), `key` (multigraph index).

### Dense Code Embeddings (`data/embeddings/*.npz`)
- **Structure**: NumPy dictionary mapping symbol dotted ID directly to an embedding vector.
- **Node Alignment**: Exact 1-to-1 bijection with graph nodes (0 missing keys, 0 orphan keys).
- **Dimensions & Dtype**: 256 dimensions, `float32`.
- **Runtime Usability**: These are code AST representations without an online neural text encoder in the offline sandbox. Natural language issue descriptions cannot be directly embedded into this latent space at runtime without the source model checkpoint.
- **Methodological Impact**: Initial query entry points must be retrieved via **lexical / BM25 matching** on symbol names and docstrings, before structural expansion via `calls` edges and cosine similarity ranking.

---

## 3. Audit Deliverables Inventory

All audit deliverables are materialized in [`results/dataset_audit/`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/):

1. [`task_inventory.csv`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/task_inventory.csv): Detailed catalog of 129 tasks, commits, modified files, lines changed, and test files.
2. [`asset_coverage.csv`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/asset_coverage.csv): 129-row audit mapping task IDs to snapshot archives, graph files, and embedding files.
3. [`graph_schema.json`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/graph_schema.json): Formal JSON schema for NetworkX code graphs.
4. [`embedding_schema.json`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/embedding_schema.json): Formal specification for NumPy `.npz` vector archives.
5. [`leakage_report.md`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/leakage_report.md): Verification of `hints_text` purity and pre-commit AST states.
6. [`audit_summary.md`](file:///c:/Users/hiten/Downloads/GEMMA/results/dataset_audit/audit_summary.md): This executive summary.

