# Gemma 4 Controlled Software Repair Experiment Protocol

**Protocol Version**: 1.0  
**Target Benchmark**: SWE-Gemma Track (129 realistic software repair tasks across FastAPI, Rich, Requests, HTTPX)  
**Competition Model**: `google/gemma-4-31b-it-qat-w4a16-ct`  
**Evaluation Standard**: Strict Hermetic Control (Zero Reference/Test Patch Leakage)

---

## 1. Experimental Objectives

This protocol establishes a scientifically controlled experiment to evaluate whether context induction via **MR-TopoS** improves automated program repair performance compared to unconstrained **Raw BM25 snippets** and **BM25 with Scope Restoration**.

The core research question is:
> *Does topology-preserving, multi-resolution context compilation translate into higher valid patch generation rates and test resolution rates when provided to Gemma 4, compared to structurally fragmented lexical retrieval?*

---

## 2. Experimental Controls & Conditions

To guarantee that any observed difference in repair performance is strictly attributable to context compilation strategy, all experimental variables except context construction are held constant:

| Variable | Control Setting |
| :--- | :--- |
| **Model Architecture** | `google/gemma-4-31b-it-qat-w4a16-ct` (Official competition quantized INT4 checkpoint) |
| **Serving Infrastructure** | vLLM engine with `tensor_parallel_size = 4`, `gpu_memory_utilization = 0.90`, `max_model_len = 32768` on 4x NVIDIA L4 GPUs (96 GB VRAM) |
| **Sampling Parameters** | `temperature = 0.2`, `top_p = 0.95`, `seed = 42`, `thinking_config.thinking_budget = 4096` |
| **System Prompt** | Official competition prompt (`prompts/system.md`), specifying tool schemas and patch format |
| **Problem Statement** | Verbatim issue text from `tasks.jsonl` |
| **Token Budget Ceiling** | Strict 2,000 and 4,000 token context budgets for retrieved codebase context |
| **Tokenizer** | Official Gemma 256k SentencePiece BPE tokenizer |
| **Execution Sandboxes** | Two-container isolated harness (`Container A` for agent interactions, `Container B` for hermetic test execution) |
| **Gold Quarantine** | Zero access to `patch` or `test_patch` during retrieval, prompting, and patch generation |

---

## 3. Compared Context Induction Strategies

1. **`bm25_raw` (Unconstrained Snippet Baseline)**:
   - Top-scoring BM25 candidate symbols are packed in rank order until budget $B$.
   - Methods are emitted as standalone snippets without enclosing `class` or `module` scopes.
   - *Characteristic*: High lexical density, but structurally fragmented (0% parent scope preservation).

2. **`bm25_scoped` (Fair Structural Baseline)**:
   - Uses the identical BM25 candidate ranking.
   - Whenever a method is selected, its enclosing parent `class` declaration is restored as an AST stub.
   - *Characteristic*: 100% parent scope preservation, but class stubs introduce token overhead, crowding out downstream candidate symbols under tight budgets.

3. **`mrtopos_milp` (Multi-Resolution Dual-View Topology)**:
   - Precedence-Constrained Multi-Choice Knapsack (PC-MCKP) optimized via exact branch-and-cut (HiGHS).
   - Dynamically selects resolution tiers: `FULL` for high-relevance symptom symbols, `SKELETON` for direct API contracts, and `STUB` for parent containers and distant causal dependencies.
   - *Characteristic*: 100% parent scope preservation while packing 2.4x to 3.4x more relevant candidate symbols under the exact same token ceiling.

---

## 4. Test Verification & Scoring Protocol

Patch extraction and verification follow the 4-pass resilient protocol defined in `DATA/HARNESS_README.md`:

1. **Patch Extraction**:
   - Agent outputs a unified git diff, or the harness extracts modifications via `git add -N . && git diff --binary HEAD`.
2. **Patch Application**:
   - **Pass 1**: `git apply --unsafe-paths --ignore-space-change --ignore-whitespace --recount`.
   - **Pass 2**: `patch -p1 --batch`.
3. **Verification**:
   - Fresh pre-patch repository snapshot extracted into isolated sandbox (`Container B`).
   - Agent patch applied to sandbox.
   - Task `test_patch` applied to sandbox.
   - Target test suite executed via `pytest -q`.
   - **Scoring**: Task is marked **RESOLVED (1.0)** if and only if `pytest` returns exit code 0 and all fail-to-pass test cases pass. Any syntax error, patch failure, or test failure yields **0.0**.

---

## 5. Execution Environment & Compute Boundary Report

In accordance with independent audit guidelines, we document the precise computational boundary of the local evaluation environment:

- **Local Host Hardware**: Windows 11 host with Intel CPU, **0 NVIDIA CUDA GPUs** available.
- **Docker Daemon**: Docker Desktop engine is not running locally (`failed to connect to docker API`).
- **Target Model Constraints**: The official competition model `google/gemma-4-31b-it-qat-w4a16-ct` requires 4x NVIDIA L4 GPUs running vLLM with INT4 tensor parallel acceleration. Running full 31B parameter generation on a local CPU host is physically constrained by memory bandwidth and absence of GPU acceleration.
- **Harness Validation Status**: The context compilation pipeline, AST graph builders, patch applicators, and pytest test harnesses were fully validated locally across the pilot tasks using Python 3.13 and Git patch binaries. Full LLM repair execution requires submission to the official Kaggle 4x L4 GPU evaluation cluster.

