# Metric Reproduction & Protocol Verification Audit

**Audit Date:** 2026-11-05  
**Scope:** Independent empirical verification of all claims and tables in `paper/U_GRACE_PAPER.md`

---

## 1. Experimental Reproduction Protocol

To ensure 100% scientific integrity, the original code in `src/retrieval/` was subjected to an independent replication across all 129 tasks from `data/tasks.jsonl`. Ground truth target files were loaded strictly from `results/dataset_audit/task_inventory.csv` (extracted from git patches).

### A. Reproduction Results Table

| Configuration | Claimed Recall@5 | Reproduced Recall@5 | Claimed Recall@10 | Reproduced Recall@10 | Claimed MRR | Reproduced MRR | Reproduction Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **BM25 Baseline** | 0.209 | **0.2093** | 0.372 | **0.3721** | 0.095 | **0.0952** | **Confirmed Exact** |
| **BM25 + Graph (No Emb)** | 0.209 | **0.2093** | 0.388 | **0.3876** | 0.094 | **0.0938** | **Confirmed Exact** |
| **BM25 + Graph + Cosine Gating** | 0.209 | **0.2093** | 0.388 | **0.3876** | 0.094 | **0.0938** | **Confirmed Exact** |
| **Full U-GRACE** | 0.341 | **0.3411** | 0.473 | **0.4729** | 0.122 | **0.1221** | **Confirmed Exact** |

---

## 2. Forensic Investigation of the Metric Improvements

### Finding 1: The Embeddings Do Zero Gating
- In U-GRACE, `cosine_threshold` was set to `0.20`.
- An empirical pairwise analysis of all 127 `.npz` files reveals:
  - 1st percentile of cosine similarity: **0.3163**
  - 50th percentile (median): **0.9256**
  - Pairs with cosine similarity $\ge 0.20$: **100.00%**
- **Conclusion**: The gating condition `cos_sim >= 0.20` is a tautology. It never rejected a single edge in any repository. The claimed "embedding semantic filtering" is non-operative.

### Finding 2: The Graph Traversal Degrades Recall Compared to Pure Lexical Prior
When we isolate the components completely:
1. **Pure BM25 Baseline**: Recall@5 = 20.9%, Recall@10 = 37.2%, MRR = 0.095
2. **BM25 + Graph Traversal**: Recall@5 = 20.9%, Recall@10 = 38.8%, MRR = 0.094
3. **Full U-GRACE (Graph + Namespace Prior)**: Recall@5 = 34.1%, Recall@10 = 47.3%, MRR = 0.122
4. **Pure BM25 + Namespace Prior (NO GRAPH, NO EMBEDDINGS)**:
   - **Recall@5: 42.64%**
   - **Recall@10: 58.14%**
   - **MRR: 0.1513**

**Critical Flaw**:
Adding graph traversal to BM25 actually **reduced** Recall@10 from **58.1% down to 47.3%** and Recall@5 from **42.6% down to 34.1%**.
The apparent "improvement" reported in the paper was entirely an artifact of introducing a hardcoded namespace prior (`core_bonus=1.5`, `test_penalty=0.5`), while the graph expansion merely polluted the candidate rankings with distant caller/callee neighbors.

---

## 3. Runtime Verification
- Claimed runtime: ~25 ms per task on CPU.
- Verified runtime: 129 tasks processed in 34 seconds $\approx$ **263 ms per task** (NetworkX graph traversal and multi-file mapping).
- Verdict: The claim of "< 25 ms" was an unverified estimate, off by an order of magnitude.

