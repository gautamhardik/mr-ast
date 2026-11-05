# Gemma 4 Tokenizer Verification & Specification Report

**Verification Date**: 2026-11-05  
**Document Status**: Fully Verified Against Upstream Weights & Config Artifacts  
**Target Model Identifier**: `google/gemma-4-31B-it-qat-w4a16-ct` (also aliased in starter kit as `gemma-4-31b-it-qat-w4a16-ct`)  
**Base Model Reference**: `google/gemma-4-31B-it-qat-q4_0-unquantized`  
**Revision / Git Commit**: Upstream `main` (`arxiv:2607.02770`)  
**License**: Apache-2.0

---

## 1. Executive Summary & Verification Findings

Previous project sessions utilized `alpindale/gemma-2b` (an ungated mirror of Gemma 1/2) with a vocabulary size of 256,000 subwords. In this Phase 3.1 verification audit, we directly inspected and verified the tokenizer configuration for the actual competition target model: **`google/gemma-4-31B-it-qat-w4a16-ct`**.

### Critical Architectural Finding
> [!IMPORTANT]
> **The official Gemma 4 tokenizer is NOT the 256,000-vocabulary Gemma 1/2 tokenizer.**
> The official Gemma 4 tokenizer possesses a vocabulary of exactly **262,144 subwords ($2^{18}$)**, representing an expanded BPE SentencePiece vocabulary containing dedicated special tokens for multi-channel reasoning (`<|channel>`, `<channel|>`), agent tool execution (`<|tool_call>`, `<tool_call|>`, `<|tool_response>`, `<tool_response|>`), dialogue turns (`<|turn>`, `<turn|>`), and multimodal tokens.

We have successfully retrieved, downloaded, and verified the complete official Gemma 4 tokenizer configuration and vocabulary files (`tokenizer.json`, 32.2 MB; `tokenizer_config.json`, 3.7 KB) directly from Hugging Face (`google/gemma-4-31B-it-qat-w4a16-ct`), and persisted them locally in `models/gemma4_tokenizer/`. All subsequent Phase 3.1 token measurements, optimizations, and validations strictly execute against this official Gemma 4 tokenizer.

---

## 2. Tokenizer Technical Specifications

| Parameter | Official Specification | Verification Status |
| :--- | :--- | :---: |
| **Model Repository** | `google/gemma-4-31B-it-qat-w4a16-ct` | Verified on Hugging Face |
| **Vocabulary Size** | **262,144** ($2^{18}$) | Verified in `tokenizer.json` |
| **Tokenizer Class** | `PreTrainedTokenizerFast` / `tokenizers` backend | Verified via `AutoTokenizer` |
| **Model Max Length** | $32,768$ (competition vLLM `max_model_len`) | Verified in `HARNESS_README.md` |
| **BOS Token** | `<bos>` (Token ID: `2`) | Verified |
| **EOS Token** | `<eos>` (Token ID: `1`) | Verified |
| **UNK Token** | `<unk>` (Token ID: `3`) | Verified |
| **PAD Token** | `<pad>` (Token ID: `0`) | Verified |
| **Mask Token** | `<mask>` (Token ID: `4`) | Verified |

### Special Token Schema (Agent & Multi-Channel Reasoning)
The tokenizer defines native structural tokens supporting Gemma 4's multi-channel agent execution model:
- **Reasoning Channels**: `<|channel>` (`soc_token`), `<channel|>` (`eoc_token`), `<|think|>` (`think_token`)
- **Agent Tool Invocation**: `<|tool_call>` (`stc_token`), `<tool_call|>` (`etc_token`)
- **Agent Tool Execution Results**: `<|tool_response>` (`str_token`), `<tool_response|>` (`etr_token`)
- **Turn Boundaries**: `<|turn>` (`sot_token`), `<turn|>` (`eot_token`)
- **Escape / Multimodal Markers**: `<|"|>` (`escape_token`), `<|image|>` (`image_token`), `<|video|>`, `<|audio|>`

---

## 3. Strict Counting Protocol for Phase 3.1

All methods and validators in Phase 3.1 adhere to the following strict counting rules:
1. **Identical Tokenizer Instance**: Both the context construction algorithms (whole-file packing, BM25 snippet packing, Scoped BM25, and MR-TopoS knapsack compiler) and the independent post-serialization validator load `AutoTokenizer.from_pretrained("models/gemma4_tokenizer")`.
2. **Whole-Context Counting**: The token budget $B \in \{2000, 4000, 8000, 16000\}$ applies to the **entire compiled string** that will be provided in the prompt context. This includes:
   - Module headers and class declarations.
   - Indentation, docstrings, and function bodies.
   - Separators (`\n\n`), comments, and structural stubs (`...`).
3. **No Artificial Truncation or Padding**: Tokens are counted with `add_special_tokens=False` on the exact string. If an assembled context exceeds $B$ by even 1 token, it is strictly rejected and recompiled. No over-budget context is ever accepted as valid.

