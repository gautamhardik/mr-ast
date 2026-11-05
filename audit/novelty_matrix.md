# Novelty Audit & Prior Art Comparison Matrix

**Audit Date:** 2026-11-05  
**Target:** Rigorous comparison of U-GRACE against peer literature and competitive systems

---

## 1. Prior Art Comparison Matrix

| System / Method | Venue / Origin | Retrieval Strategy | Graph Representation | Embedding Usage | Uncertainty / Stopping | Primary Strength | Critical Vulnerability vs. Prior Art |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LocAgent** | ACL 2024 / Gerstein Lab | Multi-hop agentic graph search with LLM reasoning | Directed heterogeneous graph (classes, funcs, files, invocations, imports, inheritance) | Dense neural code embeddings for multi-hop ranking | LLM self-reflection & termination token | 92.7% file localization on SWE-bench Lite; highly sophisticated heterogeneous graph schema | U-GRACE is drastically simpler, lacks multi-hop agentic navigation, and uses static call-only edges. |
| **CoSIL** | arXiv 2024 | LLM-driven on-the-fly graph expansion | Dynamic on-demand function call graphs constructed by LLM | Zero pre-indexing (Index-free) | Context pruning based on target hit probability | No offline index required; scales to arbitrary unindexed codebases | U-GRACE requires static pre-computed graphs and embeddings. |
| **SpIDER** | ICML 2024 | Spatially informed dense retrieval | Syntax tree & symbol dependency graph | Dense neural embeddings fused with structural graph distance | Score thresholding & margin gating | Cross-language support (Python, Java, TS); rigorous geometric embedding fusion | SpIDER formulates structural graph convolution mathematically; U-GRACE is simple 1-hop scalar multiplication. |
| **Gemma 4 Benchmark (aghasalim / HF)** | Gemma Competition Community 2026 | Lexical BM25 file-level retrieval | Provided competition call graphs | Pre-computed 256-d competition embeddings | Fixed top-$k$ truncation | Evaluated across same 129 tasks; showed that BM25 beats graph expansion | Demonstrates that the community *already knew* that BM25 outperforms the competition's graph/embedding assets. |
| **U-GRACE (Current Proposal)** | Gemma 4 Paper Track (Proposed) | BM25 seed grounding $\to$ 1-hop call propagation | NetworkX MultiDiGraph (`calls` edges only) | Static dot-product with 256-d competition embeddings | Shannon entropy over top-20 candidate softmax | Fully offline, CPU-executable in sandbox | **Novelty Flaw**: Merges standard BM25 with naive neighbor expansion. Does not present a fundamentally new theory or competitive architecture. |

---

## 2. In-Depth Novelty Analysis

### A. Novelty vs. LocAgent
LocAgent constructs a heterogeneous graph containing 6 node types and 8 edge types (including inheritance, imports, member access, call sites). In contrast, U-GRACE only uses the provided 1-relation `calls` edge. Claiming state-of-the-art novelty for 1-hop expansion over single-type call edges in late 2026 is completely untenable before academic reviewers.

### B. Baseline Discrepancy with aghasalim's Benchmark
- **Why aghasalim reported high BM25 Hit@5 (~55%–69%) while our baseline showed 20.9%**:
  - **Granularity Difference**: aghasalim ran BM25 directly on **file-level source text** from repository checkouts. In contrast, our implementation ran BM25 over **AST symbol nodes** and projected nodes to files.
  - **Namespace Filtering**: When file-level BM25 runs on repository sources, documentation and test directories are excluded by convention (e.g., searching only `src/` or `fastapi/`).
  - In our implementation, AST nodes from `tests/` and `docs_src/` (which make up 85% of all nodes in FastAPI) were indexed alongside core code, severely depressing the baseline. Once a namespace prior is added, BM25 alone jumps to 58.1%.
- **Verdict**: The low BM25 baseline in U-GRACE was an artifact of indexing test and documentation nodes without standard repository search heuristics.

### C. Actual Novelty Verdict
- **Core Claimed Novelty**: "Uncertainty-Guided Graph Retrieval combining AST embeddings and call graphs."
- **Audit Reality**:
  - The embeddings are non-discriminative (median similarity = 0.93).
  - The graph expansion hurts performance compared to BM25.
  - The uncertainty metric has near-zero correlation with actual bug localization.
- **Novelty Classification**: **CONFIRMED FLAW**. The paper does not possess sufficient novelty to win "Overall Best Paper" at a Google DeepMind competition.

