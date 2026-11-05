# Master Claim-Evidence Matrix: Confirmatory Research Audit

**Date:** 2026-11-05T12:28:00+05:30  
**Author:** Evidence-First Principal Research Scientist  
**Deliverable:** `research/final_claim_evidence_matrix.md`  
**Standard:** Zero-Leniency Independent Verification  
**Target:** Google Gemma 4 Developer Agent Paper Track

---

## 1. Master Claim Status Table

| # | Scientific Claim | Quantitative Finding | Source Evidence File | Statistical Verification | Confirmatory Verdict |
|---|---|---|---|---|:---:|
| **C1** | **Multi-Resolution Recall Advantage** | $+16.61\text{ pp}$ at $2\text{k}$; $+13.07\text{ pp}$ at $4\text{k}$ over lexical scoping | `results/strategic_reset/experiment_ledger.csv` | Paired $t$-test with Holm correction: $p_{\text{Holm}} = 0.0006$ at 2k; $p_{\text{Holm}} = 0.0004$ at 4k; $d_z = +0.36$ | **VERIFIED** |
| **C2** | **Syntactic Parse Validity** | 100.0% valid Python ASTs ($516/516$ conditions at $K=60$; $100.0\%$ on held-out tasks) | `results/strategic_reset/integrity_audit_summary.json` | Tested via `ast.parse()` on every compiled context; Scoped BM25 has $24.8\%$ failure rate | **VERIFIED** |
| **C3** | **Full Implementation Preservation** | Retains $1.55\times$ more full executable implementations ($19.47$ vs $12.55$) at $2\text{k}$ | `results/strategic_reset/statistical_analysis_summary.json` | Allocates $1,849$ tokens to full methods vs $1,192$ for BM25; non-target code compressed to skeletons | **VERIFIED** |
| **C4** | **Candidate Pool Saturation & Resolution** | Scaling $K=60 \to 400$ increases $16\text{k}$ recall from $57.05\%$ to $76.70\%$ | `results/heldout_confirmatory_validation.json` | Confirmed on 66 untouched held-out tasks grouped by commit: $+20.76\text{ pp}$ gain ($p_{\text{Holm}} = 0.00019, d_z = +0.54$) | **VERIFIED** |
| **C5** | **Zero-Tolerance Budget Compliance** | 100.0% zero budget violations across all 5,160 evaluations | `results/strategic_reset/integrity_audit_summary.json` | Maximum token violation: exactly 0; verified by Gemma 4 tokenizer | **VERIFIED** |
| **C6** | **MCKP Formulation & Precedence Removal** | Pure Multiple-Choice Knapsack Problem (MCKP); optimizer precedence constraints removed | `research/ast_constraint_necessity.md` | Precedence constraints reduced recall by $-5.43\text{ pp}$ at 2k; serializer reconstructs parents post-hoc | **REFINED & VERIFIED** |
| **C7** | **Topological Graph Dependency Claims** | Static call-graph weights ($\lambda_{\text{topo}}$) provide $0.00\text{ pp}$ marginal recall | `results/strategic_reset/statistical_analysis_report.md` | $p = 1.0000$ at 2k, 8k, 16k; all claims of graph topology improving recall retracted | **RETRACTED FROM RECALL** |
| **C8** | **Solver Latency & Optimality Benchmark** | Greedy compiles in $23.7\text{ ms}$; HiGHS solves in $2.8\text{ ms}$ pure simplex | `results/solver_comparison/empirical_scaling.csv` | MILP $+4.69\text{ pp}$ at 4k becomes $p_{\text{Holm}} = 0.0519$ (non-significant); Greedy adopted as production engine | **QUALIFIED & VERIFIED** |
| **C9** | **Gemma 4 Prompt Efficiency Pilot** | Reduces Gemma 4 31B generation latency by $28.3\%$ ($7.57\text{ s}$ vs $10.55\text{ s}$) | `results/gemma_repair/pilot_execution.csv` | Paired $t(5) = 2.76, p = 0.038$; zero-shot single-shot diffs fail `git apply` due to line drift; framed as latency pilot | **QUALIFIED & VERIFIED** |
| **C10**| **Aider Baseline Comparison** | Aider-inspired static repository map reproduction; MR-TopoS is $15\times$ to $50\times$ faster | `research/aider_baseline_fidelity.md` | Aider 0% AST validity and zero full implementations disclosed as by-design multi-turn agent properties | **QUALIFIED & VERIFIED** |

---

## 2. Summary Verdict

All 10 research claims have been forensically verified, refined, or retracted based on empirical evidence:
- **5 Claims Strictly Verified**: C1 (Multi-Resolution Gain), C2 (Syntactic Validity), C3 (Implementation Preservation), C4 (Held-Out Saturation Resolution), C5 (Budget Compliance).
- **1 Claim Refined**: C6 (Formulated as MCKP; knapsack precedence constraints removed).
- **1 Claim Retracted**: C7 (Graph topology recall claims retracted; $0.00\text{ pp}$ gain disclosed).
- **3 Claims Qualified**: C8 (Greedy production compiler vs MILP reference), C9 (Gemma 4 generation efficiency pilot), C10 (Aider-inspired static repository map reproduction).
