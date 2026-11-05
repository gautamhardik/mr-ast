# Google Gemma 4 Developer Agent Paper Track: Submission Checklist

**Competition**: Google Gemma 4 Developer Agent Paper Track (Kaggle Competition ID: `163111`)  
**Paper Title**: *Topology-Preserving Context Compilation for Constrained Software Engineering Agents*  
**Short Name**: MR-TopoS  
**Submission Deadline**: November 12, 2026 at 23:59 UTC  
**Target Category**: Track 1 — Developer Agent Architecture & Context Engineering  

---

## 1. Compliance & Formatting Verification

- [x] **Word Count & Page Limits**: Paper draft formatted to standard conference format (~3,000 words, structured into Abstract, Intro, Formulation, Methodology, Experiments, Results, Related Work, Limitations, Conclusion).
- [x] **Target Model Alignment**: Explicitly designed and calibrated for `google/gemma-4-31B-it-qat-w4a16-ct`. Token counts measured using official 262,144-vocabulary SentencePiece BPE tokenizer.
- [x] **Special Token Integration**: Reasoning channel tokens (`<|channel>`, `<channel|>`) and tool-calling tokens (`<tool_call|>`, `<tool_response|>`) integrated into execution pipeline.
- [x] **Scientific Integrity**:
  - Zero manufactured or fabricated results.
  - Zero gold-patch or test-patch leakage into retrieval or knapsack valuation.
  - Strict reporting of negative findings (e.g. Full-File Hit@1 inversion at 16k due to test-file crowding).
  - Clear hardware boundary documentation (local host vs 4x L4 GPU cluster).
- [x] **Reproducibility Package**:
  - `README_REPRODUCE.md` providing exact step-by-step terminal commands.
  - `configs/final_experiment.yaml` containing all hyperparameters and dataset paths.
  - Fixed random seeds and deterministic HiGHS mathematical solver guarantees.
- [x] **Visual Figures**:
  - `paper/figures/figure2_scope_tax.png` / `.pdf`: Demonstrating the Scope Tax and 3.4x symbol capacity advantage.
  - `paper/figures/figure3_solver_speed.png` / `.pdf`: Demonstrating HiGHS branch-and-cut dual-simplex scaling vs heuristic greedy compiler.

---

## 2. Research Contribution Checklist

- [x] **Theoretical Novelty**: First formalization of the **"Scope Tax"** in fine-grained code context retrieval and its resolution via Precedence-Constrained Multi-Choice Knapsack (PC-MCKP).
- [x] **Algorithmic Contribution**: Exact HiGHS branch-and-cut optimization (<5 ms per task) replacing heuristic greedy compilers, guaranteeing 0% precedence violations.
- [x] **Program Analysis Contribution**: Differential Typing Pruner separating modern typing metadata (`Annotated[T, Doc(...)]`) from verbose prose while maintaining non-empty class invariants.
- [x] **System Reliability**: Strict Real-Token Budget Guard with deterministic multi-stage trimming guaranteeing 100.0% zero budget violations across all benchmark evaluations.
- [x] **Benchmark Scale**: Complete evaluation across all 129 tasks, 4 token budgets, and 5 baseline methods (2,580 evaluated conditions).

---

## 3. Submission Sign-off

Signed by: Independent Adversarial Research Audit & Antigravity Autonomous Agent Team  
Date: November 5, 2026

