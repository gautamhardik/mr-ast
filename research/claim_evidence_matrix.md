# Claim-to-Evidence Traceability Matrix

**Project**: MR-TopoS Research Paper  
**Target Track**: Google Gemma 4 Developer Agent Paper Track  
**Date**: November 5, 2026  
**Auditor**: Independent Adversarial Audit  

---

## 1. Overview

To guarantee absolute scientific rigor and eliminate unsubstantiated claims or confirmation bias, every technical claim made in the MR-TopoS research paper is formally mapped to an empirical artifact, test case, or mathematical derivation in this matrix.

---

## 2. Claim-to-Evidence Mapping

| Claim # | Paper Claim | Exact Evidence Artifact | Test / Log Reference | Validation Metric / Finding |
|---|---|---|---|---|
| **CLM-01** | **Official Gemma 4 Tokenizer Integration**: Target model utilizes a 262,144 SentencePiece BPE tokenizer with dedicated multi-channel reasoning tokens (`<\|channel>`, `<channel\|>`). | `research/tokenizer_verification.md`, `models/gemma4_tokenizer/` | `TestImplementationAudit.test_01_tokenizer_verification` | Vocabulary size is exactly $262,144$ ($2^{18}$); special tokens verified. |
| **CLM-02** | **Discovery of the "Scope Tax"**: Wrapping fine-grained methods in parent class stubs restores syntactic validity ($100\%$) but incurs a $28.9\%$ reduction in retained symbol capacity and causes gold files to be crowded out under tight budgets ($B=2000$). | `results/phase3/structural_baseline_comparison.csv` | `results/phase3/corrected_metrics.md` | Gold coverage drops from $88.9\%$ (raw BM25) to $55.6\%$ (scoped BM25) at $B=2000$ due to class header tax. |
| **CLM-03** | **Multi-Resolution Capacity Advantage**: By dynamically stubbing non-target container symbols, MR-TopoS retains **$3.4\times$ to $6.8\times$ more candidate symbols** than scoped BM25 with $100\%$ parent scope validity and zero crowding. | `results/final_benchmark/aggregate.csv` | `scripts/run_final_benchmark.py` | Retains $55.2$ symbols vs $16.2$ symbols at $B=2000$ with $88.9\%$ gold file recall. |
| **CLM-04** | **PC-MCKP Mathematical Invariants**: Multi-choice exclusivity ($\sum_r x_{ir} = 1$) and parent-child precedence ($x_{p(i),0} \le x_{i0}$) are strictly satisfied with zero violations. | `src/mrtopos/knapsack_solver.py` | `TestImplementationAudit.test_07_milp_multiple_choice_exclusivity`, `test_08_milp_parent_child_precedence` | $0$ precedence violations across both HiGHS MILP and Constraint-Aware Greedy compilers. |
| **CLM-05** | **Exact MILP Computational Dominance**: Exact branch-and-cut dual simplex via HiGHS solves the PC-MCKP knapsack in $<5.0\text{ ms}$ per task, executing faster than constraint-aware greedy at candidate scale. | `results/final_benchmark/aggregate.csv`, `tests/test_mrtopos_phase2.py` | `TestMRTopoSPhase2.test_milp_solver_exact_optimality` | HiGHS solve time: $4.08\text{ ms}$ ($N=60$) vs Greedy $14.19\text{ ms}$; at $N=800$, MILP is $8.8\times$ faster. |
| **CLM-06** | **Differential Typing Pruning Efficiency**: Stripping verbose docstrings to 1-line summaries and removing `Doc(...)` while preserving base type $T$ and validation rules preserves $100\%$ type contracts. | `src/mrtopos/differential_pruner.py` | `TestImplementationAudit.test_02_structural_stub_pruning`, `test_03_contract_skeleton_pruning` | Non-empty class body invariant verified; docstring summaries extracted cleanly. |
| **CLM-07** | **Zero Dummy Token Invariant**: All token costs ($c_{\text{raw}}, c_{\text{skel}}, c_{\text{stub}}$) are computed using real Gemma 4 subword encodings, satisfying $0 < c_{\text{stub}} \le c_{\text{skel}} \le c_{\text{raw}}$. | `research/implementation_audit.md` | `TestImplementationAudit.test_10_no_dummy_token_costs_guard` | Real subword token ordering strictly monotonic across all code entities. |
| **CLM-08** | **Strict Real-Token Budget Guard**: Serialized contexts never exceed nominal token budgets $B \in \{2000, 4000, 8000, 16000\}$. Multi-stage trimming absorbs formatting overhead deterministically. | `results/validation/budget_compliance.csv`, `results/final_benchmark/budget_audit.csv` | `TestContextSerializer.test_strict_budget_guard_trimming` | **$100.0\%$ compliance** across all 129 tasks and all budgets. Zero budget violations ($>B$). |
| **CLM-09** | **Full-File Localization Crowding Paradox**: Increasing token budget from 8k to 16k in whole-file retrieval causes Hit@1 to paradoxically decline (from $13.95\%$ to $10.08\%$) because large non-gold test files fit into 16k, crowding out compact gold source files. | `results/phase3/corrected_metrics.md` | `results/final_benchmark/aggregate.csv` | Proved via case study of `tests/test_requests.py` ($15,941$ tokens) vs `requests/models.py` ($7,977$ tokens). |
| **CLM-10** | **Rigorous Downstream Packaging Boundary**: Gemma 4 31B W4A16 inference requires 4x NVIDIA L4 GPUs running vLLM and cannot be run on CPU-only local hosts; evaluation protocol and test harness are packaged for official Kaggle cluster. | `results/phase4/repair_experiment_protocol.md` | `experiments/gemma_repair/README.md` | Automated pytest harness validated on patch application; reproduction scripts packaged for submission. |

---

## 3. Adversarial Quality Gate Sign-Off

All 10 claims above are supported by immutable empirical evidence files and passing unit test suites. No claims of unmeasured downstream repair performance are made; all architectural, computational, and retrieval metrics are derived strictly from real code and verified token counts.

