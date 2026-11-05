# Context Serialization Specification & Strict Real-Token Budget Enforcement

**Status**: Verified & Frozen  
**Date**: November 5, 2026  
**Auditor**: Independent Adversarial Research Audit  
**Implementation**: `src/mrtopos/context_serializer.py`  
**Empirical Validation**: `results/validation/budget_compliance.csv` (100.0% PASS across 20 test conditions in 4 repositories)

---

## 1. Context Architecture & Serialization Layout

Autonomous software engineering agents operating under constrained token budgets require context that is both semantically rich and syntactically valid. Raw concatenation of retrieved code snippets frequently breaks Python indentation, severs methods from their parent class scopes, or omits prerequisite type definitions.

The MR-TopoS `ContextSerializer` solves this by transforming the multi-resolution assignment vector $\mathbf{x}^*$ output by the PC-MCKP knapsack solver into a structured, unified Python context.

### 1.1 Structural Layout
The serialized context consists of ordered file sections:
```python
# File: {canonical_relative_path}
{file_content}

# File: {next_canonical_path}
{next_file_content}
```

Within each file section, symbols are rendered according to their assigned resolution tier and AST hierarchy:
1. **Module Level Data & Tables**:
   - Preserves lookup tables, constant dictionaries, and unicode mappings (`is_data_only=True`).
   - SKELETON / STUB tiers elide array contents (`_WIDTHS = [...]`) to prevent context exhaustion while retaining the identifier.
2. **Class Definitions with In-Scope Methods**:
   - If a class is selected at `FULL` with no individually targeted methods: emits complete class definition.
   - If a class is selected at `SKELETON` or `STUB` with child methods:
     ```python
     class ClassName:
         """1-line docstring summary if Tier 2."""
         def selected_full_method(self, ...):
             # Complete implementation body
             ...
         def selected_skeleton_method(self, ...):
             ...
         def selected_stub_method(self, ...):
             ...
     ```
   - **Indentation Invariant**: Child methods are strictly indented by 4 spaces (`textwrap.indent(code, "    ")`), ensuring the resulting file string passes `ast.parse()` without syntax errors.
3. **Top-Level Functions**:
   - Rendered at their selected resolution (FULL, SKELETON, or STUB).

---

## 2. Strict Real-Token Budget Guard

### 2.1 The Formatting Overhead Problem
While the knapsack optimizer enforces $\sum_i c_{ir} x_{ir} \le B$, the serialized text string introduces slight formatting overhead:
- File boundary comments: `# File: path/to/file.py\n` (~6–10 tokens per file).
- Inter-symbol blank lines and class declaration indentation.
In tight budgets ($B=2000$), formatting overhead can push an unconstrained compilation 10 to 40 tokens over budget (e.g. 2,034 tokens).

### 2.2 Deterministic Multi-Stage Trimming Algorithm
To guarantee that `len(tokenizer.encode(context)) <= budget` with 100.0% mathematical certainty, `ContextSerializer` implements a deterministic 4-stage fallback trimming loop:

1. **Measurement**: Exact tokenization of the assembled context text:
   $$T = \text{len}(\text{Encode}(\text{context\_str}))$$
   If $T \le B$, compilation succeeds immediately with 0 trimmed nodes.

2. **Stage 1 (STUB Pruning)**:
   If $T > B$, identify all active symbols assigned to `ResolutionTier.STUB`.
   Sort by utility ascending: $u_i = s_i + \lambda_{\text{topo}} w_i$.
   Progressively downgrade STUB symbols to `ResolutionTier.EXCLUDED`, re-evaluating $T$ after each downgrade until $T \le B$.

3. **Stage 2 (SKELETON Pruning)**:
   If all STUBs are exhausted and $T > B$, sort SKELETON symbols by utility ascending and downgrade to `ResolutionTier.STUB`.

4. **Stage 3 (FULL Pruning)**:
   If $T > B$, sort FULL symbols by utility ascending and downgrade to `ResolutionTier.SKELETON`.

5. **Stage 4 (Deterministic Line Truncation)**:
   If an indivisible monolithic symbol or file exceeds $B$, perform binary search over line boundaries, appending `# [Context budget limit reached]`, strictly guaranteeing $T \le B$.

---

## 3. Empirical Validation Results

The strict budget enforcement mechanism was evaluated across 20 task-budget conditions spanning all 4 benchmark repositories:

| Task ID | Repository | Budget $B$ | MILP Nominal | Serialized Tokens | Trimmed Nodes | Files | Compliant |
|---|---|---|---|---|---|---|---|
| `fastapi_15588` | `fastapi/fastapi` | 2,000 | 2,000 | **1,998** | 23 | 19 | **True** |
| `fastapi_15588` | `fastapi/fastapi` | 4,000 | 3,984 | **3,998** | 14 | 20 | **True** |
| `fastapi_15588` | `fastapi/fastapi` | 8,000 | 7,927 | **7,557** | 0 | 20 | **True** |
| `fastapi_15588` | `fastapi/fastapi` | 16,000 | 11,801 | **11,431** | 0 | 20 | **True** |
| `fastapi_14964` | `fastapi/fastapi` | 2,000 | 2,000 | **1,914** | 0 | 19 | **True** |
| `fastapi_14964` | `fastapi/fastapi` | 4,000 | 3,957 | **3,698** | 0 | 22 | **True** |
| `fastapi_14964` | `fastapi/fastapi` | 8,000 | 7,958 | **5,529** | 0 | 23 | **True** |
| `fastapi_14964` | `fastapi/fastapi` | 16,000 | 15,751 | **13,062** | 0 | 23 | **True** |
| `requests_7328` | `psf/requests` | 2,000 | 1,992 | **1,942** | 0 | 8 | **True** |
| `requests_7328` | `psf/requests` | 4,000 | 3,995 | **3,542** | 0 | 9 | **True** |
| `requests_7328` | `psf/requests` | 8,000 | 7,993 | **6,233** | 0 | 10 | **True** |
| `requests_7328` | `psf/requests` | 16,000 | 15,718 | **10,416** | 0 | 10 | **True** |
| `rich_3905` | `Textualize/rich` | 2,000 | 1,997 | **1,984** | 14 | 22 | **True** |
| `rich_3905` | `Textualize/rich` | 4,000 | 3,988 | **3,564** | 0 | 23 | **True** |
| `rich_3905` | `Textualize/rich` | 8,000 | 7,978 | **6,673** | 0 | 24 | **True** |
| `rich_3905` | `Textualize/rich` | 16,000 | 15,928 | **13,490** | 0 | 24 | **True** |
| `httpx_3672` | `encode/httpx` | 2,000 | 1,994 | **1,528** | 0 | 17 | **True** |
| `httpx_3672` | `encode/httpx` | 4,000 | 3,995 | **2,639** | 0 | 18 | **True** |
| `httpx_3672` | `encode/httpx` | 8,000 | 7,894 | **5,697** | 0 | 18 | **True** |
| `httpx_3672` | `encode/httpx` | 16,000 | 13,905 | **7,631** | 0 | 19 | **True** |

**Summary**: Across all 20 runs, budget compliance is **100.0%**. In tight conditions (e.g. `fastapi_15588` at $B=2000$), trimming 23 peripheral STUB nodes successfully absorbed 100% of formatting overhead, bringing serialized tokens to 1,998 without losing any high-utility core candidates.

