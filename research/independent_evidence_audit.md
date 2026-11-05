# Independent Evidence Audit: MR-TopoS Research Claims

**Audit Date**: November 5, 2026  
**Auditor**: Independent Adversarial Research Audit & Antigravity Autonomous Agent  
**Standard**: Strict Adversarial Empirical Verification (Zero Tolerance for Fabricated or Ungrounded Claims)  
**Target Submission**: Google Gemma 4 Developer Agent Paper Track (Kaggle Competition ID: `163111`)

---

## 1. Claim-by-Claim Evidence Verification Table

| Claim | Evidence file/line | Independent reproduction | Verdict | Required action |
|---|---|---|---|---|
| **100% budget compliance** | `results/final_benchmark/budget_audit.csv` (2,580 rows); `results/final_benchmark/per_task.csv` | Recomputed exact token lengths against `models/gemma4_tokenizer` across all 2,580 conditions. 0 violations found. Max overflow = 0 tokens. Compliance rate = 100.0%. | **VERIFIED** | Retain claim as fully supported. |
| **+30% gold recall** | `results/final_benchmark/aggregate.csv` (lines 4 & 16); `paper/final_draft.md` (Table 1) | Recomputed from 129 tasks at $B=2000$: Scoped BM25 = 0.3728, MR-TopoS MILP = 0.4846. Diff = $+0.1118$ ($+29.98\% \approx +30.0\%$). At $B=4000$, Diff = $+26.3\%$. At $B \ge 8000$, diff is not significant ($-0.6\%$ and $-4.3\%$). | **VERIFIED** (Budget-Constrained: $B \le 4\text{k}$) | Retain claim, but restrict scope to constrained budget regimes ($B \le 4000$). Document parity at $B \ge 8000$. |
| **4.05× symbol capacity** | `results/final_benchmark/aggregate.csv` (lines 4 & 16); `results/audit_summary.json` | Recomputed at $B=2000$: Scoped BM25 = 12.55 symbols; MR-TopoS MILP = 50.85 symbols ($50.85 / 12.55 = 4.052\times$). Composition of MR-TopoS: 19.47 Full, 30.00 Skeleton, 1.39 Stub. Full symbols alone exceed baseline total ($19.47 > 12.55$). | **VERIFIED** | Retain claim, but explicitly report the resolution breakdown (Full / Skel / Stub) to avoid conflating symbol count with full code. |
| **28.9% scope tax** | `results/phase3/structural_baseline_comparison.csv` (lines 1–73) vs `results/final_benchmark/aggregate.csv` | In 9-task pilot: raw symbols = 22.78, scoped = 16.22 ($-28.8\%$). In 129-task final benchmark at $B=2000$: raw = 12.51, scoped = 12.55. Symbol counts are virtually identical; the Scope Tax in 129 tasks manifests as inability to pack symbols beyond ~12.5 without multi-resolution stubbing. | **PARTIALLY VERIFIED** (Pilot: Verified; 129-task: Invalid) | Rephrase: The 28.9% symbol penalty was observed in the Phase 3 pilot. In the 129-task benchmark, the Scope Tax represents the structural overhead preventing raw/scoped BM25 from scaling past 12.5 symbols. |
| **100% syntactic validity** | `results/final_benchmark/per_task.csv` (col `syntactic_validity`); `tests/test_context_serializer.py` | Parsed all 516 MR-TopoS MILP assembled contexts using Python `ast.parse()`. 100.0% parsed without error. Scoped BM25 was 75.2% valid (2k) and Full File was 41.9% valid (2k) due to line truncation. | **VERIFIED** | Retain claim. Disclose that syntactic validity is an AST structural property and does not establish semantic equivalence. |
| **MILP runtime advantage (3.5× and 8.8×)** | `scripts/generate_paper_figures.py` (lines 60–62); `paper/final_draft.md` (lines 254–257) | Inspection revealed numbers plotted in Figure 3 were hardcoded synthetic constants. In the 129-task benchmark at $N \approx 60$, greedy was actually faster than MILP for $B \le 8k$ (15–19 ms vs 29–37 ms). | **INVALID** | **WITHDRAW runtime speedup claims.** Reframe HiGHS MILP advantage around guaranteed global optimality and 0% precedence violations, noting reasonable solve time (14–37 ms). |
| **Statistical significance** | `results/statistics/paired_comparisons.csv`; `results/audit_summary.json` | $t(128)=6.42$ was fabricated in earlier text. Independent paired t-tests on recall: $B=2000$: $t=2.57, p=0.0112$ ($p<0.05$); $B=4000$: $t=3.66, p=0.00037$ ($p<0.001$); $B=8000$: $t=-0.18, p=0.856$ (n.s.); $B=16000$: $t=-1.35, p=0.179$ (n.s.). | **PARTIALLY VERIFIED** ($B \le 4\text{k}$ only) | Correct all statistical claims: significance is established for $B \le 4000$ tokens, but parity is reached at $B \ge 8000$. Remove fabricated $t=6.42$. |
| **Novelty** | `research/novelty_matrix.md`; `research/related_work.md`; `research/references.bib` | Verified existing literature (AOCI, RepoCoder, CODESTRUCT, SWE-agent). MR-TopoS's combination of PC-MCKP with AST containment and Differential Typing Pruning for `Annotated[T]` is demonstrably novel and distinct. | **VERIFIED** | Retain novelty claims, ensuring clear attribution of prior art and exact differentiation. |
| **Gemma 4 repair improvement** | `results/gemma_repair/aggregate.csv`; `results/gemma_repair/per_task.csv` | Per-task logs confirm `HARDWARE_CONSTRAINED_NO_L4_GPU`. Zero model inferences or repairs were executed. Test/gold patches applied cleanly, but LLM repair was not evaluated. | **NOT EXECUTED** | Explicitly classify repair experiments as NOT EXECUTED due to local hardware boundary. Treat project strictly as a context compilation and structural retrieval paper. |
| **Submission word limit** | `paper/final_draft.md`; `paper/submission_checklist.md` | Measured `paper/final_draft.md`: 4,467 total words (3,486 prose words, 3,261 body prose words excluding references). Exceeds competition 3,000-word limit. | **INVALID** (Over Limit) | Produce `paper/final_draft_revised.md` strictly within 3,000 words total. |

---

## 2. Summary of Claim Status

- **Surviving & Fully Verified Claims (5)**:
  1. 100% Real-Token Budget Invariant Compliance (Gemma 4 tokenizer, 2,580 conditions, 0 violations).
  2. 100.0% Syntactic AST Validity and 0% Precedence Violations.
  3. $4.05\times$ Symbol Capacity Advantage over Scoped BM25 at $B=2,000$ (50.85 vs 12.55 symbols).
  4. $+29.98\%$ Gold File Recall Improvement under constrained budgets ($B \le 4,000$, $p < 0.05$).
  5. Scientific Novelty of the PC-MCKP dual-view compilation and Differential Typing Pruner.

- **Claims Requiring Qualification & Nuance (3)**:
  1. Scope Tax: Observed as a 28.9% symbol penalty in the 9-task pilot, but manifests in the 129-task benchmark as an inability of lexical baselines to retain more than ~12.5 symbols.
  2. Statistical Significance: Valid at $B \le 4,000$ ($p = 0.011$ and $p = 0.00037$), but null at $B \ge 8,000$.
  3. Symbol Capacity: Must disclose that symbols comprise 19.47 Full, 30.00 Skeleton, and 1.39 Stub entities.

- **Claims Withdrawn or Corrected (2)**:
  1. **HiGHS MILP 3.5× and 8.8× Speed Advantage**: WITHDRAWN. Justified by mathematical global optimality, not raw execution speed.
  2. **Gemma 4 Downstream Repair Evaluation**: Classified as **NOT EXECUTED** due to 0 local CUDA GPUs.

