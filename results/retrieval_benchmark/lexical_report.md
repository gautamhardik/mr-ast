# Lexical Baseline Retrieval Benchmark Report

**Date:** 2026-11-04  
**Benchmark Scope:** All 129 tasks across 4 repositories in `swegemma`  
**Method:** Offline BM25 over code graph AST nodes (symbol names + docstrings + signatures), mapped to candidate repository filepaths.

---

## 1. Aggregated Retrieval Metrics

| Evaluation Subset | Task Count | Recall@1 | Recall@5 | Recall@10 | Recall@20 | MRR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Overall** | **129** | **0.0%** | **20.9%** | **37.2%** | **51.9%** | **0.095** |
| **`fastapi/fastapi`** | 67 | 0.0% | 23.9% | 38.8% | 56.7% | 0.098 |
| **`Textualize/rich`** | 48 | 0.0% | 10.4% | 27.1% | 35.4% | 0.075 |
| **`psf/requests`** | 13 | 0.0% | 38.5% | 61.5% | 84.6% | 0.145 |
| **`encode/httpx`** | 1 | 0.0% | 100.0% | 100.0% | 100.0% | 0.250 |

---

## 2. Key Analysis & Observations

1. **Why Lexical Recall Alone Is Insufficient**:
   - At top-10 retrieval, pure BM25 recovers the ground-truth modified file in only **37.2%** of tasks.
   - At top-20, coverage increases to **51.9%**, but almost half of all tasks still have zero relevant files in the initial lexical candidate pool.
   - Rich has the lowest lexical recall (Recall@10: 27.1%), primarily because issues describe high-level terminal rendering glitches (e.g. table borders, console wrapping) rather than naming the internal renderer classes directly.
2. **The Exact Scientific Need for U-GRACE**:
   - When a bug report mentions an external API or symptom (e.g. `FastAPI` route failure or `Requests` HTTP adapter redirect), BM25 hits the entry-point facade (e.g., `requests.sessions` or `fastapi.applications`).
   - The actual bug fix often resides 1 or 2 hops deeper in the call graph (e.g., `requests.adapters.HTTPAdapter` or `fastapi.routing`).
   - **Graph propagation (Phase 3)**: Expanding from BM25 seed nodes along `calls` edges combined with dense 256-d AST similarity is necessary to bridge this lexical-structural gap.

---

## 3. Artifacts Generated
- [`results/retrieval_benchmark/lexical_baseline_metrics.json`](file:///c:/Users/hiten/Downloads/GEMMA/results/retrieval_benchmark/lexical_baseline_metrics.json): JSON metrics summary.
- [`results/retrieval_benchmark/lexical_per_task.csv`](file:///c:/Users/hiten/Downloads/GEMMA/results/retrieval_benchmark/lexical_per_task.csv): Detailed per-task rankings and hit indicators for all 129 tasks.

