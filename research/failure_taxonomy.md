# Systematic Failure Taxonomy & Boundary Analysis

**Audit Date**: November 5, 2026  
**Corpus**: 129 SWE Benchmark Tasks across 4 Repositories  
**Focus**: Identifying and Classifying Structural Failure Modes in Repository Context Retrieval  

---

## 1. Taxonomy of Context Retrieval Failure Modes

Through our adversarial audit of all 129 benchmark tasks, we classify retrieval and context failures into four distinct structural categories:

```
                          REPOSITORY CONTEXT FAILURE MODES
                                         |
     +-------------------+---------------+------------------+-------------------+
     |                   |                                  |                   |
     v                   v                                  v                   v
[ Category 1 ]      [ Category 2 ]                     [ Category 3 ]      [ Category 4 ]
Polysemous &        Newly Created                      Data-Only Table     Monolithic Test
Generic Identifiers Reference Files                    Omission            File Crowding
("render", "parse") (Zero Pre-Patch Files)             (Lookup Arrays)     (15k-token modules)
```

---

## 2. Detailed Category Analysis

### Category 1: Polysemous and Generic Symbol Collisions
- **Symptom**: When an issue description mentions generic actions such as `"validate input"` or `"render terminal"`, BM25 returns dozens of identically named methods (`validate`, `render`, `process`) across unrelated packages.
- **Impact**: Flat lexical retrieval fills the candidate pool with disconnected helper functions.
- **MR-TopoS Resolution**: The asymmetric dual-view topology dampens isolated symbols. The Causal Path Extractor propagates weights strictly along directed invocation ($E_{\text{call}}$) and import ($E_{\text{import}}$) edges. Coincidental name matches that lack graph connectivity receive $w_i = 0$, allowing connected domain logic to prevail.

---

### Category 2: Newly Created Reference Files (The Upper Bound Limit)
- **Symptom**: In certain benchmark tasks, the reference pull request creates an entirely new source or test file (e.g. adding `scripts/prepare_release.py` in `fastapi_15661`).
- **Inference Reality**: At inference time, an agent only possesses the pre-patch repository snapshot. A file that does not yet exist physically cannot be retrieved by *any* static code retriever.
- **Empirical Quantification**: Across the 129 tasks, there are 278 total gold file references. Our audit reveals that **49 of these references ($17.6\%$) are newly created files**.
- **Corrected Upper Bound**:
  - Raw micro coverage on all files: $61.87\%$ ($172 / 278$).
  - **True micro coverage on pre-existing candidate files**: **$75.11\%$ ($172 / 229$)**.
  - **Eligible task success rate**: **$87.29\%$ ($103 / 118$ eligible tasks)**.
- **Reporting Rule**: Research papers must not penalize retrieval models for failing to retrieve non-existent files. We explicitly report both raw and pre-existing coverage metrics.

---

### Category 3: Data-Only Configuration and Constant Modules
- **Symptom**: Files like `rich/_cell_widths.py` or `rich/_unicode_data/*.py` consist entirely of module-level constant arrays or lookup tuples without `def` or `class` keywords.
- **Prior Art Failure**: Tools like CODESTRUCT or ctags parse only classes and functions, silently dropping data-only files and causing a **$22.3\%$ coverage gap**.
- **MR-TopoS Resolution**: Direct snapshot AST parsing registers `GLOBAL_DATA` nodes with constant elision (`_WIDTHS = [...]`), preserving the variable names and docstrings under Tier 1 and Tier 2 while retaining the raw arrays under Tier 3.

---

### Category 4: Monolithic Test File Crowding (The Localization Paradox)
- **Symptom**: When the budget expands from 8k to 16k in whole-file retrieval, Hit@1 drops from $13.95\%$ to $10.08\%$.
- **Mechanism**: Large integration test files (`tests/test_requests.py` at $15,941$ tokens) exceed the 8k budget but fit into the 16k budget. At 16k, the test file is greedily packed first, exhausting the entire budget and crowding out the compact gold source file `requests/models.py` ($7,977$ tokens).
- **MR-TopoS Resolution**: Fine-grained multi-resolution optimization decomposes test files into individual test functions. The optimizer includes only relevant test cases at FULL resolution while pruning unrelated test fixtures, completely preventing context monopolization.

---

## 3. Failure Distribution Across Benchmark Repositories

| Repository | Primary Failure Mode Observed | Pre-Patch File Coverage | Overall Success Rate |
|---|---|---|---|
| `fastapi/fastapi` (67 tasks) | Category 2 (New test files added in PR) | 73.8% | 85.1% |
| `Textualize/rich` (48 tasks) | Category 3 (Data lookup tables) & Category 1 | 78.4% | 89.6% |
| `psf/requests` (13 tasks) | Category 4 (Test file crowding) | 71.4% | 84.6% |
| `encode/httpx` (1 task) | Category 1 (Transport interface polymorphism) | 100.0% | 100.0% |
| **All Repositories (129 tasks)** | **Mixed Distribution** | **75.11%** | **87.29%** |

