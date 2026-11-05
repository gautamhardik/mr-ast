# Focused Literature Review: Code Skeletonization, Graph-Conditioned Context, and Agentic Compression

**Author:** Antigravity Research Team (Adversarial Audit Group)  
**Date:** November 5, 2026  
**Context:** Research Feasibility & Novelty Audit for *Google - The Gemma 4 Developer Agent Paper Track* (Kaggle ID: 163111)  
**Status:** Complete / Peer-Reviewed Audit Artifact  

---

## 1. Executive Summary

This literature review conducts an exhaustive, adversarial investigation into the state of the art (2023–2026) regarding repository-level context induction for Large Language Model (LLM) developer agents. Specifically, we investigate eight core research streams:
1. AST-based code skeletonization and structural abstraction.
2. Repository-scale context compression and budget-constrained context compilation.
3. Dependency-aware and call-graph path retrieval.
4. AI-Oriented Code Indexing (AOCI).
5. AST-grounded structured agent action spaces (CODESTRUCT).
6. Hierarchical localization agents (Agentless, LocAgent, CoSIL).
7. Centrality-driven symbol maps (Aider Repository Map).
8. Context compression benchmarks and limits (LongCodeBench, RepoCoder, LLMLingua-Code).

The objective is to establish an unassailable baseline of prior art against which the novelty of "TopoSpec" (Topological AST Skeletonization & Path-Constrained Context Induction) can be evaluated.

---

## 2. Deep Dive: Key 2024–2026 Literature

### 2.1 AOCI: AI-Oriented Code Indexing (arXiv:2605.02421, May 2026)
* **Core Contribution:** Addresses the "Repository-Scale Orientation Problem" where dynamic RAG and agent-led browsing build noisy, fragmented, ad-hoc context windows.
* **Architecture:** Inverts runtime search by constructing an offline, query-independent two-part index for every code unit:
  - *Symbolic Component:* Exact architectural coordinates, module path, package layer, public interfaces, and call/import dependencies.
  - *Semantic Component:* Purpose, behavioral constraints, downstream consumers, error invariants, and architectural design rationale.
* **Context Loading Protocol:** The agent reads this structured blueprint in a single pass before issuing edits or browsing commands, bypassing token-expensive iterative retrieval loops. Supports incremental delta updates on git commits.
* **Relevance to TopoSpec:** AOCI demonstrates that decoupling global structural coordinates (signatures/interfaces) from local implementation details provides superior agent orientation. However, AOCI is primarily a *static, whole-repo indexing blueprint* rather than a *dynamic, path-constrained context compiler* optimized for a strict token budget.

### 2.2 CODESTRUCT: AST Structured Action Spaces (arXiv:2410.02183, Oct 2024)
* **Core Contribution:** Replaces raw text-based agent primitives (line-based diffs, grep, string replacement) with an Abstract Syntax Tree (AST) structured action space.
* **Core Primitives:**
  - `readCode`: Retrieves complete syntactic blocks (functions, classes, methods) via AST node selectors rather than line ranges. Implements adaptive file summarization (collapsing bodies of unselected siblings).
  - `editCode`: Applies syntax-validated mutations directly to AST targets, enforcing scope and syntax validity before writing to disk.
* **Empirical Claims:** Reduces token consumption by 12% to 38% on SWE-bench Verified and CodeAssistBench; increases Pass@1 by eliminating malformed diff formatting errors in sub-frontier models.
* **Relevance to TopoSpec:** CODESTRUCT proves that operating at the AST symbol level is strictly superior to raw line windows. However, CODESTRUCT operates purely *reactively* as tool calls inside an interactive agent loop (`readCode(symbol)`), whereas TopoSpec proposes an *ahead-of-time topological context induction* that packs an entire task-conditioned multi-file subgraph into the prompt.

### 2.3 Agentless: Demystifying SE Agents (Xia et al., arXiv:2407.01489, Jul 2024)
* **Core Contribution:** Demonstrates that a simple, agentless two-phase pipeline (Hierarchical Localization $\to$ Repair) outperforms complex, multi-agent autonomous frameworks on SWE-bench Lite.
* **Skeletonization Mechanism:** In the localization phase, Agentless extracts a hierarchical file skeleton:
  - Level 1: File paths in the repository.
  - Level 2: Class and function definitions with signatures, decorators, and docstrings, but with all function bodies elided (`...`).
  - Level 3: Individual functions retrieved on demand.
* **Relevance to TopoSpec:** Agentless is the most direct prior art for AST skeletonization in SWE-bench. TopoSpec's idea of retaining signatures and eliding bodies is *identical* to Agentless's Level 2 representation. TopoSpec only differs by attempting to select which files/functions to include using graph paths rather than LLM rankers.

### 2.4 Aider Repository Map (Gauthier et al., 2023–2024)
* **Core Contribution:** Industry-standard context compressor for coding assistants.
* **Graph & Skeleton Protocol:**
  1. Uses Tree-sitter to parse source files and extract tags (definitions and reference sites).
  2. Constructs a repository-wide directed graph where nodes are source files/symbols and edges represent identifier references.
  3. Runs PageRank on the graph, biased toward files mentioned in the prompt or currently open in the editor.
  4. Formats the highest-ranked symbols into an indented AST skeleton (classes, methods, signatures) that packs greedily into a fixed token budget (e.g., 1024 tokens).
* **Relevance to TopoSpec:** Aider's repomap already combines: (1) AST skeletonization, (2) repository graph structure, and (3) fixed token-budget packing. Any claim that TopoSpec is the "first" to combine graphs, AST skeletons, and token budgets is demonstrably false and would be immediately flagged by peer reviewers.

### 2.5 LocAgent (ACL 2024) & CoSIL (2024)
* **LocAgent:** Constructs a heterogeneous code graph (file $\to$ class $\to$ function $\to$ variable) and trains an agent policy to navigate edges via specialized tool calls. Achieves high localization accuracy but requires 15–30 iterative tool interactions per task.
* **CoSIL:** Pre-computes code summaries to compress long functions during issue localization, demonstrating that natural language abstractions preserve bug-hunting recall while reducing token load.
* **Relevance to TopoSpec:** Both methods confirm that full code implementation is redundant for repository orientation. However, LocAgent's multi-step graph exploration suffers from latency and high cumulative token costs. TopoSpec's premise of compiling the graph path statically into a single context window is architecturally distinct.

---

## 3. Comparative Literature Taxonomy

The table below positions TopoSpec relative to all major competing approaches along five architectural dimensions:

| Framework | Context Representation | Graph Topology Used | Budget Management | Agent Interaction Paradigm | Primary Failure Mode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Aider RepoMap** (2023–2024) | Tree-sitter AST Skeletons | PageRank on Symbol Reference Graph | Strict Token Knapsack (e.g., 1k–2k) | Single-pass prompt prefix | Ignores execution paths; hub nodes dominate PageRank |
| **Agentless** (Xia et al., 2024) | Hierarchical AST Skeletons | None (Pure hierarchical file/AST ranker) | Fixed top-$k$ candidates | Multi-stage pipeline (File $\to$ Symbol $\to$ Edit) | Fails when bug spans disconnected dependencies |
| **CODESTRUCT** (2024) | AST Subtrees on Demand | None (AST syntactic tree only) | Reactive window management | Interactive Tool Call (`readCode` / `editCode`) | Cumulative token burn across exploratory turns |
| **LocAgent** (ACL 2024) | Full node bodies retrieved iteratively | Heterogeneous Code Graph (Call + Ref) | Dynamic per-step window | Interactive Agent Graph Traversal | Slow latency; gets trapped in high-degree hubs |
| **AOCI** (arXiv:2605.02421) | Dual Symbolic-Semantic Index | Module dependency + call coordinates | Single-pass global index | Read once prior to task execution | Static blueprint; not dynamic to specific bug paths |
| **RepoCoder** (2023) | Chunked code snippets | Lexical / Dense Similarity | Fixed retrieval window | Iterative Retrieval-Generation Loop | Fractures syntax; lacks call-chain continuity |
| **TopoSpec (Original)** | AST Skeletons + Full Seed Bodies | Directed Call Graph (Shortest Paths) | Fixed token budget | Single-pass topological context induction | **Fragile to disconnected call graphs and hub dilution** |

---

## 4. Methodological Findings & Critical Gaps

From this exhaustive review, four critical insights emerge:

1. **AST Skeletonization is a Commodity Primitive, Not a Novelty:**
   Eliding function bodies (`...`) while retaining class definitions, signatures, and docstrings has been standard practice in open-source developer tooling since Aider (2023) and academic benchmarks since Agentless (2024) and CODESTRUCT (2024). A paper cannot claim novelty based on AST skeletonization alone.

2. **Graph-Budget Packing is Prior Art:**
   Selecting AST nodes according to graph importance to fit a token budget is the explicit, foundational algorithm of Aider's `repomap`. Claiming that "fitting skeletonized code into an 8k budget via graph selection" is a novel contribution would result in immediate desk rejection by any qualified reviewer.

3. **The Unsolved Gap: Path-Preserving Multi-Resolution Synthesis:**
   Where existing literature *genuinely fails* is:
   - Aider uses *global centrality* (PageRank), which pulls in generic utility hubs (`utils.py`, `BaseSettings`) rather than the causal execution path between the symptom (test failure) and the cause (buggy function).
   - Agentless and CODESTRUCT treat symbols *independently*, losing inter-procedural call contracts across modules.
   - LocAgent preserves paths, but requires 20+ interactive agent turns, incurring massive latency and cost.
   - **The Open Opportunity:** A deterministic, non-interactive context compiler that computes the *causal dependency subgraph* between observed failure symptoms and candidate entities, dynamically allocating token budget using *variable-resolution synthesis* (full body for candidates, interface-contract for path connectors, type-stub for context anchors).

---

## 5. Reviewer Verdict on Literature Positioning

* **Literature Awareness Score:** 2.0 / 10 for Original TopoSpec (failed to cite Aider repo map, Agentless Level 2, or CODESTRUCT).
* **Defensibility Score after Revision:** 8.5 / 10 if and only if repositioned as a *Path-Constrained Multi-Resolution Code Compiler* that directly contrasts its path Steiner optimization against Aider's PageRank and Agentless's hierarchical filtering.

