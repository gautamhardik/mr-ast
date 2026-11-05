# MR-AST Write-up Visual Image Gallery & Assets Guide
**Competition:** Google — The Gemma 4 Developer Agent Paper Track (Kaggle ID: `163111`)

This document organizes all visual assets, preview cards, diagrams, and benchmark charts created for the **MR-AST** Kaggle Writeup submission.

---

## 1. Quick Copy-Paste Fields for Kaggle Submission Form

### Field 1: Title (Limit: 80 characters)
```text
MR-AST: Multi-Resolution AST Context Selection for Gemma 4 Agents
```
*(Length: 66 / 80 characters)*

### Field 2: Subtitle (Limit: 140 characters)
```text
Budget-constrained AST context compiler for Gemma 4 developer agents with 4-tier MCKP optimization and guaranteed syntactic validity.
```
*(Length: 137 / 140 characters)*

### Field 3: Submission Archive (Upload Files: max 100 MB)
- **Primary Package**: [`mr_ast_submission_package.zip`](file:///c:/Users/hiten/Downloads/GEMMA/mr_ast_submission_package.zip) **(17.95 MB)**
- **Alternate Name**: [`submission.zip`](file:///c:/Users/hiten/Downloads/GEMMA/submission.zip) **(17.95 MB)**

---

## 2. How Kaggle Writeups Display Images and PDF Pages

> [!IMPORTANT]
> **Why Local Markdown Links (`![banner](banner.png)`) Cannot Be Resolved Directly on Kaggle:**
> When you edit your write-up on Kaggle's website, Kaggle's servers cannot access your local laptop drive (`C:\Users\...`).
> 
> **How to Insert Images into Your Kaggle Write-up:**
> 1. In the Kaggle **Project Description** rich-text editor (see Screenshot 2), look at the top formatting toolbar.
> 2. Click the **Image icon** (the square icon showing a mountain and sun, next to the Table icon).
> 3. Select and upload the desired image from `paper/figures/` (e.g., `gallery_1_architecture.png`, `gallery_2_recall_benchmark.png`, or `pdf_pages/page_1.png`).
> 4. Kaggle uploads the image to its public CDN and automatically inserts a live tag like `![image.png](https://www.kaggle.com/media/...)` directly into your text!
> 
> **How the 8-Page PDF Manuscript is Displayed:**
> - Markdown and web browsers **cannot natively embed multi-page `.pdf` documents** inside a markdown text block.
> - Therefore, we rendered each page into a high-resolution PNG image (`page_1.png` through `page_8.png` in `paper/figures/pdf_pages/`).
> - In your Writeup description, you can upload **`page_1.png`** (or a 2-column table of pages) as an eye-catching visual preview.
> - Under **Attachments -> Files** (Screenshot 3), you upload the actual vector document **[`paper/final_submission_candidate.pdf`](file:///c:/Users/hiten/Downloads/GEMMA/paper/final_submission_candidate.pdf)** so judges and reviewers can download and inspect the complete publication paper.

---

### Gallery Figure 1: System Architecture Overview (1200 x 675)
- **File**: [`paper/figures/gallery_1_architecture.png`](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/gallery_1_architecture.png)
- **Caption**: *Figure 1: End-to-end MR-AST architecture from repository AST forest parsing and the 4-tier projection lattice to $O(N \log N)$ greedy knapsack optimization and grammar-preserving serialization with Invariant 1.*
- **Kaggle Description Embed Markdown**:
```markdown
![Figure 1: MR-AST System Architecture](gallery_1_architecture.png)
*Figure 1: End-to-end MR-AST architecture from repository AST forest parsing and the 4-tier projection lattice to $O(N \log N)$ greedy knapsack optimization and grammar-preserving serialization with Invariant 1.*
```

---

### Gallery Figure 2: Gold Recall & 2-Fold Cross-Validation (1200 x 675)
- **File**: [`paper/figures/gallery_2_recall_benchmark.png`](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/gallery_2_recall_benchmark.png)
- **Caption**: *Figure 2: Left: Gold symbol recall across budgets on the retrospective 66-task partition showing MR-AST outperforming Scoped BM25 (+16.44 pp, p=0.0043) and Aider RepoMap. Right: Zero-leakage 2-fold cross-validation confirming out-of-fold recall parity (76.92% vs 76.47% at 16k).*
- **Kaggle Description Embed Markdown**:
```markdown
![Figure 2: Recall Curves and Cross-Validation Parity](gallery_2_recall_benchmark.png)
*Figure 2: Left: Gold symbol recall across budgets on the retrospective 66-task partition showing MR-AST outperforming Scoped BM25 (+16.44 pp, p=0.0043) and Aider RepoMap. Right: Zero-leakage 2-fold cross-validation confirming out-of-fold recall parity (76.92% vs 76.47% at 16k).*
```

---

### Gallery Figure 3: Downstream Gemma 4 Latency & Patch Taxonomy (1200 x 675)
- **File**: [`paper/figures/gallery_3_gemma4_latency.png`](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/gallery_3_gemma4_latency.png)
- **Caption**: *Figure 3: Left: Gemma 4 31B downstream prompt latency showing a -28.3% reduction under MR-AST (p=0.038). Right: Unified-diff patch failure taxonomy (line drift 61.1%, indentation mismatch 22.2%, missing hunk headers 16.7%), illustrating the limitation of zero-shot single-turn patching.*
- **Kaggle Description Embed Markdown**:
```markdown
![Figure 3: Gemma 4 Latency Reduction and Failure Taxonomy](gallery_3_gemma4_latency.png)
*Figure 3: Left: Gemma 4 31B downstream prompt latency showing a -28.3% reduction under MR-AST (p=0.038). Right: Unified-diff patch failure taxonomy (line drift 61.1%, indentation mismatch 22.2%, missing hunk headers 16.7%), illustrating the limitation of zero-shot single-turn patching.*
```

---

### Gallery Figure 4: Scope Taxation Breakdown & Parent Deduplication (1200 x 675)
- **File**: [`paper/figures/gallery_4_scope_deduplication.png`](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/gallery_4_scope_deduplication.png)
- **Caption**: *Figure 4: Scope taxation analysis demonstrating 56.05% pooled token deduplication via post-hoc parent reconstruction (median 5.0 tokens per class).*
- **Kaggle Description Embed Markdown**:
```markdown
![Figure 4: Scope Taxation Deduplication](gallery_4_scope_deduplication.png)
*Figure 4: Scope taxation analysis demonstrating 56.05% pooled token deduplication via post-hoc parent reconstruction (median 5.0 tokens per class).*
```

---

### Gallery Figure 5: Solver Scaling & Complexity Benchmark (1200 x 675)
- **File**: [`paper/figures/gallery_5_solver_scaling.png`](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/gallery_5_solver_scaling.png)
- **Caption**: *Figure 5: Pure solver benchmark comparing HiGHS MILP against Python greedy implementation across candidate pool sizes $N \in [20, 800]$, highlighting sub-linear scaling, 20.8x speedup, and 0.0% optimality gap.*
- **Kaggle Description Embed Markdown**:
```markdown
![Figure 5: Solver Latency & Scaling](gallery_5_solver_scaling.png)
*Figure 5: Solver latency scaling and HiGHS speedup factor across candidate pool sizes N in [20, 800].*
```

---

## 3. Publication Paper Visual Preview (Pages 1–8)

All 8 publication pages of [`paper/final_submission_candidate.pdf`](file:///c:/Users/hiten/Downloads/GEMMA/paper/final_submission_candidate.pdf) rendered at 150 DPI:

| Page 1 (Title, Abstract, §1, §2) | Page 2 (§2 Formulation & Complexity) |
|:---:|:---:|
| [![Page 1](pdf_pages/page_1.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_1.png) | [![Page 2](pdf_pages/page_2.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_2.png) |
| **Page 3 (§3 Invariant 1 & Serializer)** | **Page 4 (§4 Corpus & Baselines)** |
| [![Page 3](pdf_pages/page_3.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_3.png) | [![Page 4](pdf_pages/page_4.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_4.png) |
| **Page 5 (§5 Table 1 Factorial Results)** | **Page 6 (§5 Table 2 Retrospective Split)** |
| [![Page 5](pdf_pages/page_5.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_5.png) | [![Page 6](pdf_pages/page_6.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_6.png) |
| **Page 7 (§6 Gemma 4 Pilot & §7 Paradox)** | **Page 8 (§8 Retrospective Protocol & References)** |
| [![Page 7](pdf_pages/page_7.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_7.png) | [![Page 8](pdf_pages/page_8.png)](file:///c:/Users/hiten/Downloads/GEMMA/paper/figures/pdf_pages/page_8.png) |

---

## 4. Suggested Ready-to-Paste Write-up Markdown Template

Below is a complete, polished draft that you can paste directly into the **Project Description** box on Kaggle:

````markdown
# MR-AST: Multi-Resolution AST Context Selection for Budget-Constrained Software Engineering Agents

## Overview & The Problem

Autonomous software engineering agents powered by modern LLMs (such as Google Gemma 4) operate under strict prompt token budgets (B between 2,000 and 16,000 tokens). Standard retrieval approaches face an intractable dilemma:
1. **Whole-File Retrieval (`full_file`)**: Rapidly saturates context windows with irrelevant boilerplates and tests, frequently displacing actual implementation targets (the *Full-File Localization Paradox*).
2. **Snippet Extraction**: Naively extracting localized slices induces syntax errors in **24.8%** of evaluated cases due to truncated enclosing scopes.
3. **Monolithic Scoping (`bm25_scoped`)**: Redundantly emits full class headers for every retrieved symbol, capping capacity at only ~12.5 symbols at B = 2,000 tokens.

To solve this, we introduce **MR-AST**, an offline context compilation framework that formulates context selection as a **Multiple-Choice Knapsack Problem (MCKP)** over a discrete multi-resolution AST projection lattice.

---

## Key Empirical Findings

Across 129 SWE-bench Lite tasks (5,160 factorial benchmark runs across 4 repositories), MR-AST achieves:
- **+16.61 pp Recall at 2k Tokens**: Lifts gold symbol recall from 37.28% to 53.89% (p = 0.0006).
- **1.55x More Full Implementations**: Allocates 1,849 tokens directly to full code bodies (vs. 1,192 for Scoped BM25), compressing peripheral context into signatures and stubs.
- **76.92% Retrospective 16k Recall**: Yields a +16.44 pp advantage over Scoped BM25 (p = 0.0043) and +20.76 pp over static candidate pools (p = 0.00056).
- **Zero-Leakage 2-Fold Cross-Validation Parity**: 2-fold cross-validation on candidate depth K(B) independently selects expanding schedules (K between 60 and 400) with out-of-fold recall parity (76.92% vs 76.47% at 16k).
- **Guaranteed Syntactic Validity (Invariant 1)**: Achieves **100.0%** syntax validity (`ast.parse != SyntaxError`) via atomic monotonic symbol pruning.
- **-28.3% Downstream Gemma 4 Latency Reduction**: In 18 Vertex AI inference trials with `google/gemma-4-31b-it`, prompt execution dropped from 10.55s to 7.57s (p = 0.038), saving approximately 1 minute across a hypothetical 20-turn agent session.

---

## Architecture & Formulation

![Figure 1: MR-AST System Architecture](gallery_1_architecture.png)

### 1. Multi-Resolution Projection Lattice
MR-AST projects AST nodes onto a 4-tier resolution lattice:
- **Tier 3 (FULL)**: Complete function and class bodies (100% token cost).
- **Tier 2 (SKELETON)**: Signatures, type hints, docstrings, and `...` body suites (~35% cost).
- **Tier 1 (STUB)**: Minimal identifier headers (median cost only 5.0 tokens, ~12% cost).
- **Tier 0 (EXCLUDED)**: Pruned (0 tokens).

### 2. Pure MCKP Optimization & Dynamic Schedule K(B)
Context compilation is formulated as a Multiple-Choice Knapsack Problem:
- **Objective**: Maximize total information utility across all AST nodes subject to the prompt budget constraint: `Total_Cost <= B`.
- **Constraint**: Exactly one resolution tier is selected per symbol (`Sum(x_ir) = 1`).
- **Dynamic Retrieval Depth**: Candidate pool depth scales dynamically with budget: `K in {60, 100, 200, 400}`. Delegating structural containment to the serializer recovers **+5.43 pp** recall (p = 0.0050) while maintaining fast O(N log N) greedy solve times.

### 3. Grammar-Preserving Serializer C(x)
Reconstructs enclosing classes post-hoc, achieving a **56.05% pooled deduplication rate** (eliminating 12,224 redundant definitions across 493 reconstructed method runs).

![Figure 4: Scope Taxation Deduplication](gallery_4_scope_deduplication.png)

---

## Benchmark Results

![Figure 2: Recall Curves and Cross-Validation Parity](gallery_2_recall_benchmark.png)

### Matched Results on Retrospective Partition (66 Tasks, 65 Clusters)
| Token Budget | Dynamic Candidate Depth | MR-AST (Dynamic) | Scoped BM25 | Aider RepoMap | Static K=60 | Diff vs BM25 | Holm-12 p-value |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2,000** | K = 60 | **49.88%** | 41.30% | 39.15% | 49.88% | +8.58 pp | 0.4395 (n.s.) |
| **4,000** | K = 100 | **64.76%** | 44.78% | 51.77% | 55.94% | **+19.97 pp** | **0.0072** (p < 0.01) |
| **8,000** | K = 200 | **71.72%** | 58.22% | 53.06% | 55.94% | **+13.50 pp** | **0.0423** (p < 0.05) |
| **16,000** | K = 400 | **76.92%** | 60.48% | 62.74% | 56.16% | **+16.44 pp** | **0.0043** (p < 0.01) |

---

## Downstream Gemma 4 31B Evaluation & Solver Micro-Benchmark

![Figure 3: Gemma 4 Latency Reduction and Failure Taxonomy](gallery_3_gemma4_latency.png)

In 18 Vertex AI inferences on `google/gemma-4-31b-it`, MR-AST delivered a **-28.3%** latency speedup (7.57s vs 10.55s, p = 0.038). An error analysis of single-turn unified diffs revealed 0.0% patch application rates across all paradigms due to line drift (61.1%), indentation mismatch (22.2%), and missing hunk headers (16.7%), demonstrating that autonomous developer agents strictly require interactive multi-turn repair environments (such as SWE-agent) rather than single-turn diff generation.

![Figure 5: Solver Latency & Scaling](gallery_5_solver_scaling.png)

Pure solver micro-benchmarks show the HiGHS branch-and-cut solver scales sub-linearly with **3.5x to 20.8x** speedups over Python loops with 0% optimality gap, compiling working memory in 23.7 ms.

---

## Full Publication PDF Preview

![Page 1](pdf_pages/page_1.png)

The complete 8-page publication manuscript (`paper/final_submission_candidate.pdf`) is attached to this submission.

---

## Quickstart & Replication

1. **Replication Notebook**: Open `notebooks/mrast_quickstart_and_replication.ipynb` to inspect and reproduce Table 2 metrics in under 30 seconds.
2. **CLI Quickstart**:
```bash
git clone https://github.com/gautamhardik/mr-ast.git
cd mr-ast
pip install -r requirements-lock.txt
pytest
```
````

