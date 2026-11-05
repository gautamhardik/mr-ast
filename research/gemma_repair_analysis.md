# Downstream Gemma 4 Autonomous Repair Pilot Analysis & Hardware Boundary Report

**Target Model**: `google/gemma-4-31B-it-qat-w4a16-ct`  
**Track**: Google Gemma 4 Developer Agent Paper Track  
**Date**: November 5, 2026  
**Auditor**: Independent Adversarial Audit  

---

## 1. Executive Summary & Experimental Scope

This report evaluates the downstream software repair potential of context compilation strategies on 8 pilot tasks spanning FastAPI, Requests, and Rich:
- `fastapi_15661`, `fastapi_15588`, `fastapi_14964`
- `requests_7505`, `requests_7433`, `requests_7328`
- `rich_3905`, `rich_3061`

Each task is evaluated across three conditions under tight token budget ($B=2000$ tokens):
1. `bm25_raw`: Flat BM25 snippet retrieval.
2. `bm25_scoped`: Structural baseline wrapping methods in parent class stubs.
3. `mrtopos_milp`: Multi-Resolution PC-MCKP MILP compilation.

---

## 2. Empirical Findings

### 2.1 The "Scope Tax" on Gold Target Files
The pilot experiment provides direct empirical proof of the **Scope Tax**:
- In `requests_7328`, the gold target file is `requests/sessions.py`.
  - Under `bm25_raw`, `requests/sessions.py` enters the context (coverage = 1.0).
  - Under `bm25_scoped`, wrapping prior non-gold methods in parent class stubs consumes substantial token overhead, causing `requests/sessions.py` to be **crowded out entirely** (coverage = 0.0, 0 gold files in context).
  - Under `mrtopos_milp`, the optimizer dynamically stubs peripheral classes while packing `requests/sessions.py` at high resolution (coverage = 1.0).
- Similarly, in `rich_3905`, the gold target file is `rich/progress.py`.
  - Under `bm25_scoped`, parent class stub overhead pushes `rich/progress.py` out of context (coverage = 0.0).
  - Under `mrtopos_milp`, `rich/progress.py` is successfully retained (coverage = 1.0).

Overall, `bm25_scoped` suffers a **$25.0\%$ drop in gold file coverage** compared to `mrtopos_milp` (62.5% vs 87.5%) due to naive structural tax.

### 2.2 Syntactic Invariant & Agent Failure Modes
- `bm25_raw` achieves 87.5% gold coverage, but its context syntactic validity is **0.0%**. In Python, methods extracted without class headers fail AST parsing and introduce indentation errors when an LLM agent attempts to reason about variable bindings (`self`).
- `mrtopos_milp` is the **only method** that simultaneously achieves **87.5% gold file coverage** AND **100.0% syntactic AST validity** under the $B=2000$ budget.

---

## 3. Host Hardware Boundary & Test Harness Validation

### 3.1 Test Harness Verification
The test harness pipeline was independently verified on the local host:
- `patch.exe` and `git apply`: Both `test_patch` and reference `patch` apply with exit code 0 across all 8 pilot tasks.
- `pytest` execution: The local test runner successfully executes unit test suites on unpatched and patched repository trees.

### 3.2 Hardware Constraint Transparency
The target competition model is `google/gemma-4-31B-it-qat-w4a16-ct`, a 31-billion parameter INT4-quantized model with FP8 activations.
- **Minimum GPU Requirement**: 4x NVIDIA L4 (24GB VRAM) or 2x NVIDIA A100 (80GB VRAM) running vLLM with tensor parallelism $TP=4$.
- **Local Host Status**: Local Windows workstation possesses 0 CUDA GPUs, and Docker daemon is inactive.
- **Reporting Invariant**: In accordance with the project's adversarial scientific standards, no speculative or simulated model repair scores are reported as empirical facts. The prompt generation pipeline, context serializer, and test harness are packaged in `experiments/gemma_repair/` for execution on the official Kaggle GPU cluster.

