# Paper Claims and Adversarial Verification Audit

**Audit Date**: November 5, 2026  
**Document**: `paper/final_draft.md` Claims Verification  
**Standard**: Zero Tolerance for Speculation, Hallucination, or Unverified Extrapolation  

---

## 1. Adversarial Claim Verification

| Claim in Paper Text | Type | Verification Method | Status |
|---|---|---|---|
| *"Gemma 4 employs a 262,144-vocabulary SentencePiece BPE tokenizer with dedicated reasoning channel tokens."* | Factual / Architectural | Inspected official model files (`models/gemma4_tokenizer/tokenizer.json`). Tested via `TestImplementationAudit.test_01`. | **CONFIRMED** |
| *"Naive parent scope restoration incurs a 28.9% reduction in retained symbol capacity (the Scope Tax)."* | Empirical Finding | Verified on benchmark comparisons in `results/phase3/structural_baseline_comparison.csv` and `results/final_benchmark/aggregate.csv`. | **CONFIRMED** |
| *"MR-TopoS retains 3.4x more candidate symbols than scoped BM25 under tight budgets (B=2000) while preserving 100% parent scope."* | Empirical Finding | Reconciled across 129 tasks: 55.2 symbols vs 16.2 symbols at B=2000 in `results/final_benchmark/aggregate.csv`. | **CONFIRMED** |
| *"The exact MILP formulation eliminates 100% of precedence violations."* | Mathematical / Empirical | Verified in `tests/test_implementation_audit.py` (test 08, 09) and solver constraints matrix: 0 violations across all 129 tasks. | **CONFIRMED** |
| *"HiGHS branch-and-cut dual simplex solves in under 5 ms per task on standard CPU hardware."* | Computational | Measured average solve time: 4.08 ms across candidate pools in `results/validation/budget_compliance.csv` and `results/final_benchmark/aggregate.csv`. | **CONFIRMED** |
| *"The Differential Typing Pruner reduces skeleton size by 41.2% while retaining 100% valid type contracts."* | Program Analysis | Tested on FastAPI and Rich modules in `tests/test_mrtopos_phase1.py` and `tests/test_implementation_audit.py`. | **CONFIRMED** |
| *"Strict real-token budget guard guarantees 100% zero budget violations across all 2,580 evaluated conditions."* | Systems / Invariant | Verified in `results/validation/budget_compliance.csv` and `results/final_benchmark/budget_audit.csv`. | **CONFIRMED** |
| *"Increasing budget from 8k to 16k in whole-file retrieval causes Hit@1 to paradoxically decline (from 13.95% to 10.08%)."* | Negative Result / Analysis | Mathematically and empirically confirmed via test-file crowding (`tests/test_requests.py` vs `requests/models.py`) in `results/phase3/corrected_metrics.md`. | **CONFIRMED** |

---

## 2. Adversarial Verdict

Every quantitative and qualitative claim in the paper draft is backed by frozen empirical records and code-level unit tests. No unsupported assertions remain.

