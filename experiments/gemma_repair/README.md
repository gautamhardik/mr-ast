# Gemma 4 Autonomous Software Repair Evaluation Protocol

**Target Model**: `google/gemma-4-31B-it-qat-w4a16-ct` (Google Gemma 4 31B Parameter Instruction-Tuned, INT4 Quantized)  
**Track**: Google Gemma 4 Developer Agent Paper Track (Kaggle Competition ID: `163111`)  
**Status**: Packaged Protocol & Execution Harness  

---

## 1. Experimental Overview

This package provides the complete, automated test harness and prompt execution pipeline for measuring downstream software repair pass rates (resolved SWE-bench tasks) across the five context compilation strategies:
1. `full_file`: Greedy whole-file retrieval.
2. `bm25_raw`: Flat BM25 snippet retrieval (no class scope).
3. `bm25_scoped`: Scoped snippet retrieval (methods wrapped in parent class stubs).
4. `mrtopos_con_greedy`: Multi-Resolution TopoS with Constraint-Aware Greedy compiler.
5. `mrtopos_milp`: Multi-Resolution TopoS with Exact PC-MCKP MILP compiler.

---

## 2. Infrastructure & Hardware Requirements

### 2.1 Model Specifications
- **Model Identifier**: `google/gemma-4-31B-it-qat-w4a16-ct`
- **Tokenizer**: 262,144-vocabulary SentencePiece BPE (`models/gemma4_tokenizer/`)
- **Reasoning Tokens**: `<|channel>`, `<channel|>`, `<tool_call|>`, `<tool_response|>`
- **Context Limit**: 128,000 tokens

### 2.2 Serving Infrastructure
To serve the 31B parameter model with low inference latency and full context window support, the serving host must meet the following minimum specifications:
- **Accelerators**: 4x NVIDIA L4 GPUs (24GB VRAM each, total 96GB VRAM) or 2x NVIDIA A100 (80GB VRAM each).
- **Inference Server**: vLLM 0.6+ configured with tensor parallelism:
  ```bash
  vllm serve google/gemma-4-31B-it-qat-w4a16-ct \
      --tensor-parallel-size 4 \
      --max-model-len 32768 \
      --dtype auto \
      --port 8000
  ```
- **Local Host Boundary Note**: On standard developer machines without 4x L4 GPUs (e.g. CPU-only Windows host), prompt generation, context compilation, and test harness execution run locally, while model inference is dispatched to the vLLM cluster endpoint via `run_experiment.py`.

---

## 3. Test Harness Execution & Verification Protocol

### 3.1 Patch Application Pipeline
For each benchmark task:
1. **Context Compilation**: The context is compiled under budget $B$ using the designated strategy and verified to be strictly $\le B$ subword tokens.
2. **Prompt Assembly**: The context and issue description are formatted into the official Gemma 4 Developer Agent prompt template.
3. **Inference**: The model generates a candidate solution containing a git patch diff.
4. **Harness Execution**:
   - The pre-patch repository snapshot is restored.
   - The task's `test_patch` is applied via `git apply` / `patch.exe`.
   - The model's proposed patch is applied.
   - Task-specific unit tests are executed via `pytest`.
   - If tests pass with exit code 0: **RESOLVED**.
   - If tests fail: **UNRESOLVED**.
   - If patch fails to apply: **PATCH_ERROR**.

---

## 4. Reproducing the Repair Experiment

To execute the evaluation script against an active vLLM endpoint:
```bash
python experiments/gemma_repair/run_experiment.py \
    --vllm_url http://localhost:8000/v1 \
    --tasks_file data/tasks.jsonl \
    --budgets 2000 4000 8000 \
    --methods mrtopos_milp bm25_scoped bm25_raw full_file \
    --output_dir results/gemma_repair
```

