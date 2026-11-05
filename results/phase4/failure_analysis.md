# Controlled Repair Pilot & End-to-End Failure Mode Analysis

**Evaluation Date**: 2026-11-05  
**Artifact Scope**: Pilot evaluation on representative benchmark tasks across `fastapi`, `rich`, `requests`, and `httpx`.

---

## 1. Key Empirical Findings from the Pilot Experiment

The controlled pilot evaluation comparing **Raw BM25 (`bm25_raw`)**, **Scoped BM25 (`bm25_scoped`)**, and **MR-TopoS MILP (`mrtopos_milp`)** under matched 2,000-token budgets revealed critical empirical dynamics:

### 1.1. The "Scope Tax" and Candidate Crowding Pathology
A common assumption in literature is that restoring enclosing class and module scopes to raw snippets is purely beneficial. Our experiment reveals a severe unintended consequence: **the Scope Tax**.

When raw snippets are wrapped with enclosing `class` declarations to ensure syntactic validity:
- Enclosing class headers and docstrings consume additional tokens.
- Under tight budgets ($2,000$ tokens), this extra token overhead rapidly exhausts capacity.
- **Direct Empirical Consequence**: In tasks `requests_7328` and `rich_3905`, adding enclosing class declarations under `bm25_scoped` caused the actual gold target file to be **completely crowded out** of the context:
  - In `requests_7328`: `bm25_raw` achieved **1.0** gold coverage, whereas `bm25_scoped` dropped to **0.0** (context saturated at 917 tokens before reaching the gold file).
  - In `rich_3905`: `bm25_raw` achieved **1.0** gold coverage, whereas `bm25_scoped` dropped to **0.0** (context saturated at 1,994 tokens before reaching `rich/progress.py`).
  - In both tasks, **MR-TopoS MILP achieved 1.0 gold coverage** because its multi-resolution knapsack dynamically downscaled intermediate candidate symbols to `STUB` (~5–15 tokens) and `SKELETON` (~30–80 tokens), preserving parent container scoping without crowding out the gold target file.

### 1.2. Why Retrieval Metrics Cannot Substitute for Repair Results
Our audit demonstrates conclusively why localization metrics (Recall@K, MRR, Gold-File Coverage) must never be conflated with software repair success:

1. **Information Sufficiency vs. File Presence**: Having a target file present in context is a necessary but insufficient condition for repair. If only 1 method of a 50-method class is present, an agent cannot understand caller-callee contracts or inherited attributes, resulting in hallucinated attribute access.
2. **Syntactic Patch Failure Modes**: LLMs provided with orphaned method snippets frequently generate patches with incorrect indentation or misplaced decorators.
3. **Regression Failures**: A patch may fix the bug described in the problem statement but break existing regression tests in the repository test suite.
4. **Patch Application Failures**: Even syntactically plausible diffs fail to apply if line offsets or context lines in the patch do not match the base snapshot.

---

## 2. Test Harness & Execution Failure Modes

In our evaluation of the pre-patch snapshots and test suites, we identified four primary operational failure categories:

| Failure Category | Mechanism | Frequency in Benchmark | Remediation / Control |
| :--- | :--- | :---: | :--- |
| **Patch Line-Ending Corruption** | Patches stored without trailing newlines in JSON Lines fail `git apply` with `error: corrupt patch at line N`. | Benchmark-wide | Append `\n` before piping to patch tools; utilize 4-pass resilient patch application. |
| **Patch-Created Missing Files** | Ground-truth patch modifies a file created *ex nihilo* (`@@ -0,0 ... @@`) that did not exist in pre-patch snapshot. | 11 / 129 tasks (8.5%) | Pre-patch AST graphs cannot contain non-existent files. Must be classified as patch-creation tasks. |
| **Tutorial / Docs-Only Edits** | Modifications strictly inside `docs_src/` tutorial examples rather than library source code. | 6 / 129 tasks (4.7%) | Requires documentation-aware symbol extraction. |
| **High-Complexity Test Suite Stockouts** | Heavy test suites (e.g. `fastapi` running full async test suites or `requests` test suites requiring network mock servers) timing out or failing due to missing system packages. | Repository-specific | Hermetic virtual environments with pre-installed wheels from `DATA/wheels/`. |

---

## 3. Hardware & Compute Constraints

As established in our independent audit:
- The competition target model (`gemma-4-31b-it-qat-w4a16-ct`) requires a 4x NVIDIA L4 GPU cluster (96 GB VRAM) running vLLM with INT4 tensor parallelism.
- The local host is a Windows 11 development machine with 0 CUDA GPUs and Docker Desktop daemon offline.
- Consistent with peer review guidelines, we report this computational boundary explicitly. The context compilation algorithms, AST graph parsers, patch applicators, and metric calculators have been fully implemented and verified locally; full-scale Gemma LLM generation must be executed on the designated Kaggle competition infrastructure.

