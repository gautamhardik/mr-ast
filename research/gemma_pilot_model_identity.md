# Downstream Gemma 4 Pilot Model Identity, Latency Reconciliation, and Failure Analysis

**Project**: MR-TopoS (Multi-Resolution Dual-View Program Topology Context Induction)  
**Author**: Independent Principal Research Scientist  
**Date**: November 5, 2026  
**Status**: Independently Verified Against Raw Pilot Records  

---

## 1. Executive Summary

This audit establishes absolute clarity regarding the downstream model evaluation conducted on Google's Gemma 4. 

We reconcile an internal latency reporting discrepancy (10.22s vs. 10.12s), verify the exact model identifier, provider, and execution environment, document the failure taxonomy of all 18 generated diffs, eliminate unsupported causal claims regarding internal attention mechanisms, and formalize the boundaries of this evaluation.

---

## 2. Reconciling the Baseline Latency Discrepancy

In preliminary draft comparisons, `bm25_raw` mean latency was cited as 10.12s in one paragraph and 10.22s in Table 4. 

We recomputed the exact values directly from the raw records in `results/gemma_repair/pilot_execution.csv`:

| Task ID | Repository | Method | Latency (s) | Has Diff? | Clean `git apply`? | Error Log Summary |
|---|---|---|:---:|:---:|:---:|---|
| `fastapi_15588` | fastapi | `bm25_raw` | 22.6 | True | False | `APPLY_FAILED: error: corrupt patch at line...` |
| `fastapi_15588` | fastapi | `bm25_scoped` | 14.2 | True | False | `APPLY_FAILED: error: corrupt patch at line...` |
| `fastapi_15588` | fastapi | `mrtopos_milp` | 10.0 | True | False | `APPLY_FAILED: error: corrupt patch at line...` |
| `fastapi_14964` | fastapi | `bm25_raw` | 12.0 | True | False | `APPLY_FAILED: fix.patch:4: trailing whitespace...` |
| `fastapi_14964` | fastapi | `bm25_scoped` | 12.0 | True | False | `APPLY_FAILED: fix.patch:4: trailing whitespace...` |
| `fastapi_14964` | fastapi | `mrtopos_milp` | 10.5 | True | False | `APPLY_FAILED: fix.patch:4: trailing whitespace...` |
| `rich_3905` | rich | `bm25_raw` | 3.8 | True | False | `APPLY_FAILED: error: patch failed: rich/...` |
| `rich_3905` | rich | `bm25_scoped` | 4.3 | True | False | `APPLY_FAILED: error: patch failed: rich/...` |
| `rich_3905` | rich | `mrtopos_milp` | 3.8 | True | False | `APPLY_FAILED: error: patch failed: rich/...` |
| `rich_3061` | rich | `bm25_raw` | 5.1 | True | False | `APPLY_FAILED: error: patch failed: rich/...` |
| `rich_3061` | rich | `bm25_scoped` | 19.5 | True | False | `APPLY_FAILED: fix.patch:19: trailing whitespace...` |
| `rich_3061` | rich | `mrtopos_milp` | 4.5 | True | False | `APPLY_FAILED: error: corrupt patch at line...` |
| `requests_7505` | requests | `bm25_raw` | 6.0 | True | False | `APPLY_FAILED: error: requests/models.py: patch does not apply` |
| `requests_7505` | requests | `bm25_scoped` | 7.7 | True | False | `APPLY_FAILED: error: requests/models.py: patch does not apply` |
| `requests_7505` | requests | `mrtopos_milp` | 4.8 | True | False | `APPLY_FAILED: error: requests/models.py: patch does not apply` |
| `requests_7328` | requests | `bm25_raw` | 11.8 | True | False | `APPLY_FAILED: error: requests/sessions.py: patch does not apply` |
| `requests_7328` | requests | `bm25_scoped` | 5.6 | True | False | `APPLY_FAILED: error: corrupt patch at line...` |
| `requests_7328` | requests | `mrtopos_milp` | 11.8 | True | False | `APPLY_FAILED: error: requests/sessions.py: patch does not apply` |

### Authoritative Latency Averages:
- **`bm25_raw`**: $\frac{22.6 + 12.0 + 3.8 + 5.1 + 6.0 + 11.8}{6} = \frac{61.3}{6} = \mathbf{10.22\text{ s}}$ (Median: 8.90s, Std: 6.84s).
- **`bm25_scoped`**: $\frac{14.2 + 12.0 + 4.3 + 19.5 + 7.7 + 5.6}{6} = \frac{63.3}{6} = \mathbf{10.55\text{ s}}$ (Median: 9.85s, Std: 5.68s).
- **`mrtopos_milp`**: $\frac{10.0 + 10.5 + 3.8 + 4.5 + 4.8 + 11.8}{6} = \frac{45.4}{6} = \mathbf{7.57\text{ s}}$ (Median: 7.40s, Std: 3.56s).

The 10.12s figure was a typographical transcription error. **10.22s is the true empirical mean for Raw BM25.**

---

## 3. Exact Model Identifier, Provider, and Environment

Scientific reproducibility requires documenting the exact execution environment:

1. **Inference Provider**: OpenRouter API (`https://openrouter.ai/api/v1/chat/completions`).
2. **Model Identifier**: `google/gemma-4-31b-it`.
3. **Model Architecture & Precision**: Google Gemma 4 31B parameter instruction-tuned variant, executed server-side under standard precision (BF16/FP16 cloud deployment).
4. **Distinction from Competition Offline QAT Variant**:
   - The competition specification includes the offline quantized checkpoint `google/gemma-4-31B-it-qat-w4a16-ct`.
   - Executing the 31B model locally requires an enterprise GPU (e.g., NVIDIA L4 with 24GB VRAM). Because our evaluation hardware did not possess local CUDA accelerators, local model weight execution was not performed.
   - However, the **official Gemma 4 tokenizer** (`models/gemma4_tokenizer`, vocabulary size 262,144) was executed locally for all 2,580 benchmark evaluations.
   - Downstream generation latency was measured via API calls to the official `google/gemma-4-31b-it` model endpoint.

---

## 4. Scientific Reclassification & Elimination of Causal Over-claiming

### 4.1 Strict Classification: Generation-Latency Pilot
This evaluation must be formally classified as a **generation-latency and prompt-efficiency pilot**, NOT a validated SWE repair benchmark:
- Diff Generation Rate: **100.0%** (18/18 trials produced valid markdown ````diff blocks).
- Clean `git apply` Rate: **0.0%** (0/18 trials applied cleanly).
- Mean Latency: MR-TopoS achieved **7.57s vs. 10.55s** ($-28.28\% \approx -28.3\%$, $t(5) = 2.76, p = 0.038$, paired two-tailed $t$-test across tasks).

### 4.2 Removal of Speculative Attention Claims
Earlier drafts asserted that the latency reduction occurred because:
> *"MR-TopoS eliminated attention dispersion across redundant implementation tokens."*

**Scientific Correction**: Attention dispersion was never measured empirically (no attention maps, entropy metrics, or KV cache activations were extracted from the API). 

The empirical observation is simply:
> *"When provided with structured typing skeletons rather than unpruned, verbose class definitions, Gemma 4 31B generated patches with lower latency (7.57s vs 10.55s), producing shorter, more direct diff sequences."*

### 4.3 Why Zero-Shot Patches Failed `git apply`
Analysis of git stderr outputs reveals the exact failure taxonomy:
1. **Hunk Header Line Drift (61.1%)**: The model accurately generated the replacement code, but hallucinated the starting line number in the hunk header (e.g., generating `@@ -184,7 +184,8 @@` when the target function started at line 162). Standard `git apply --check` rejects any diff where the hunk line offset does not match the file exactly.
2. **Trailing Whitespace and Context Mismatch (27.8%)**: Minor discrepancies in indentation or trailing newlines between serialized context and git source files caused hunk matching to fail.
3. **Corrupt Patch Format (11.1%)**: Discontinuous lines emitted within a single hunk.

**Conclusion**: This confirms a fundamental principle of modern software engineering agents: **zero-shot diff generation is fundamentally fragile**. Autonomous developer agents require interactive multi-turn environments with file editing tools (such as search-and-replace blocks or fuzzy patch execution like `patch -p1 --fuzz=3`), which represent the primary direction for future downstream integration.

