# MR-AST: Complete Step-by-Step Reproduction Guide

**Track**: Google Gemma 4 Developer Agent Paper Track (Kaggle Competition ID: `163111`)  
**Paper**: *MR-AST: Multi-Resolution AST Context Selection for Budget-Constrained Software Engineering Agents*  
**Date**: November 5, 2026  

---

## 1. Repository Layout & Package Mapping

The conceptual method **MR-AST** is implemented within the following repository directories:
- `src/mrtopos/`: Core context compilation and optimization engine:
  - `src/mrtopos/ast_builder.py`: AST parsing, hierarchy construction, and resolution tier extraction.
  - `src/mrtopos/knapsack_solver.py`: Multiple-Choice Knapsack Problem (MCKP) solvers (HiGHS dual revised simplex and $O(N \log N)$ greedy selector).
  - `src/mrtopos/context_serializer.py`: Context serialization, shared-parent reconstruction, and atomic symbol budget guard.
  - `src/mrtopos/multilang_serializers.py`: Cross-language multi-resolution AST projection serializers (Go, Java, TypeScript, Rust).
  - `src/mrtopos/models.py`: Domain models (`SymbolNode`, `ResolutionTier`, `DualViewGraph`).
- `src/retrieval/`: Baseline retrieval implementations:
  - `src/retrieval/lexical_index.py`: BM25 index for `full_file` and `bm25_scoped` conditions.
  - `src/retrieval/aider_repomap.py`: Aider-inspired PageRank repository map outline generator.
  - `src/retrieval/dense_hybrid_retriever.py`: Dense-lexical hybrid retriever fusing precomputed embeddings with BM25.
- `experiments/`: Multi-turn agent sandboxing and LLM evaluation:
  - `experiments/multi_turn_agent/agent_loop.py`: Hermetic multi-turn developer agent sandbox with AST block editing.
  - `experiments/gemma_repair/`: Gemma 4 31B pilot execution and prompt latency logging.
- `models/gemma4_tokenizer/`: Local Gemma 4 evaluation tokenizer artifact:
  - `models/gemma4_tokenizer/tokenizer.json` (SHA-256: `cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f`, 262,144 BPE vocabulary).
- `data/`: SWE-bench Lite benchmark corpus (129 tasks, 127 unique base-commit clusters).
- `results/`: Authoritative experimental ledgers and evaluation outputs.
- `paper/`: Final manuscript markdown and compiled publication PDF.

---

## 2. Environment Setup

### 2.1 Prerequisites
- Python 3.10 to 3.13
- Git 2.40+
- GNU `patch` or Git bundled patch utility

### 2.2 Installation
Clone the repository and install dependencies in an isolated virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Core dependencies:
```
transformers>=4.45.0
scipy>=1.14.0
rank_bm25>=0.2.2
matplotlib>=3.9.0
numpy>=1.26.0
pytest>=8.0.0
```

---

## 3. Tokenizer Verification & Unit Tests

### 3.1 Tokenizer Asset Verification
MR-AST enforces subword token counts using the local Gemma 4 tokenizer artifact:
```bash
# Verify local Gemma 4 evaluation tokenizer artifact (vocab 262,144, SHA-256 cc8d3a0c...)
python -m pytest tests/test_implementation_audit.py -k test_01_tokenizer_verification -v
```

### 3.2 Running Implementation Audits
Verify core mathematical invariants, serialization validity, and unit tests:
```bash
python -m pytest tests/ -v
```
All 29 unit tests across 7 test suites must pass with exit code 0 (including multi-language serializers and multi-turn agent sandbox tests).

---

## 4. Running Benchmarks & Replicating Paper Tables

### 4.1 Master 129-Task Benchmark (Table 1)
Execute the benchmark evaluating all 129 SWE tasks across 4 token budgets ($B \in \{2\text{k}, 4\text{k}, 8\text{k}, 16\text{k}\}$) and comparison baselines:
```bash
python -u scripts/run_final_benchmark.py
```
Outputs generated in `results/final_benchmark/`:
- `per_task.csv`: 2,580 evaluated condition rows.
- `aggregate.csv`: Summary metrics per method and budget.
- `budget_audit.csv`: Verification of 100.0% zero budget violations.

### 4.2 Retrospective Commit-Disjoint Baseline Evaluation (Table 2)
Execute the retrospective commit-disjoint evaluation across 66 evaluation tasks (65 base-commit clusters):
```bash
python scripts/compute_matched_heldout_baselines.py
```
*Note on Chronology & Protocol*: Candidate-depth saturation bounds were informed by the master 5,160-run full-corpus sweep across all 129 tasks prior to formalizing the 63-task development set and 66-task retrospective commit-disjoint partition.
Outputs generated in `results/`:
- `results/heldout_authoritative_matched_baselines.csv`: Per-task recall across 66 evaluation tasks and 4 budgets.
- `results/heldout_reconciliation_comparison.json`: Commit-clustered 95% confidence intervals and post-hoc Holm-12 adjusted p-values.

### 4.3 Generating Publication Figures (Figures 2 & 3)
Generate high-resolution charts for the research paper:
```bash
python scripts/generate_paper_figures.py
```
Generated artifacts in `paper/figures/`:
- `figure2_scope_tax.png` / `.pdf`: Scope Tax trade-off and symbol capacity advantage.
- `figure3_solver_speed.png` / `.pdf`: HiGHS dual revised simplex scaling vs greedy selector.

---

## 5. Recompiling Publication Manuscript & PDF

To recompile the final manuscript and PDF:
```bash
python scripts/generate_pdf.py
```
Output:
- `paper/final_submission_candidate.html`
- `paper/final_submission_candidate.pdf` (8 pages, compliant layout, zero overflow)

---

## 6. Reproducibility Guarantee

All experiments use deterministic seed 42. Knapsack optimization via HiGHS produces identical mathematical global optima across operating systems (Windows, Linux, macOS).
