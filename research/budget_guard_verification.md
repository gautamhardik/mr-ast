# Budget Guard Mechanism and Fallback Trimming Verification

**Project**: MR-TopoS (Multi-Resolution Dual-View Program Topology Context Induction)  
**Author**: Independent Principal Research Scientist  
**Date**: November 5, 2026  
**Status**: Empirically Verified & Traced  

---

## 1. Executive Summary & Reviewer Vulnerability

In earlier drafts of the manuscript, the budget guard was described using the ambiguous shorthand:
> *"a deterministic 4-stage fallback trimming loop downgrades STUB $\to$ SKELETON $\to$ FULL $\to$ line truncation"*

To an adversarial reviewer, this phrasing creates an immediate red flag: since representation token costs satisfy $c_{\text{STUB}} \le c_{\text{SKELETON}} \le c_{\text{FULL}}$, "downgrading STUB to SKELETON to FULL" would *increase* token cost, which is mathematically absurd.

This audit inspects the production implementation in `src/mrtopos/context_serializer.py`, presents an empirical trace of an intentionally over-budget test, verifies AST preservation, clarifies the relationship between the optimizer output and the serializer fallback, and provides precise, unassailable scientific language for the manuscript.

---

## 2. Code Inspection: The Real Downgrade Mechanism

In `src/mrtopos/context_serializer.py` (lines 68–102), the budget guard executes if and only if the jointly assembled context exceeds the token budget ($T > B$):

```python
# 1. Sort active non-excluded symbols by (tier_order ascending, utility ascending)
def sort_key(sid: str) -> Tuple[int, float]:
    tier = active_tiers[sid]
    # STUB (1) < SKELETON (2) < FULL (3)
    return (int(tier), utils.get(sid, 0.0))

prunable_sids = sorted(active_tiers.keys(), key=sort_key)

# 2. Iterate through candidate symbols and apply monotonic resolution downgrade
for sid in prunable_sids:
    curr_tier = active_tiers[sid]
    if curr_tier == ResolutionTier.STUB:
        active_tiers[sid] = ResolutionTier.EXCLUDED
    elif curr_tier == ResolutionTier.SKELETON:
        active_tiers[sid] = ResolutionTier.STUB
    elif curr_tier == ResolutionTier.FULL:
        active_tiers[sid] = ResolutionTier.SKELETON

    context_str, included_sids = self._assemble_context(graph, active_tiers)
    raw_tokens = self.tokenizer_fn(context_str)
    if raw_tokens <= budget:
        break

# 3. Stage 4 Fail-Safe: Line truncation if still over budget
if raw_tokens > budget:
    context_str = self._line_truncate_to_budget(context_str, budget)
```

### Clarification of Terminology:
1. **Target Selection Order (Which symbols are pruned first)**:
   - Lowest-utility symbols currently at **STUB** are targeted first (downgraded to **EXCLUDED**).
   - Lowest-utility symbols currently at **SKELETON** are targeted second (downgraded to **STUB**).
   - Lowest-utility symbols currently at **FULL** are targeted third (downgraded to **SKELETON**).
2. **Individual Entity Transition (Monotonic Cost Reduction)**:
   - For every symbol, the resolution transitions strictly downward:
     $$\text{FULL} \longrightarrow \text{SKELETON} \longrightarrow \text{STUB} \longrightarrow \text{EXCLUDED}$$
   - This guarantees that token cost strictly decreases ($\Delta c \le 0$) at each trimming step.

---

## 3. Empirical Over-Budget Test & Step-by-Step Trace

To empirically verify this mechanism under controlled conditions, we constructed an intentionally over-budget repository context (`scripts/verify_budget_guard_detailed.py`, output in `results/budget_guard_trace.json`):
- **Graph Setup**: Parent class `ParentClass` containing method `critical_method` (FULL, utility 50.0), method `secondary_method` (SKELETON, utility 25.0), and standalone function `low_priority_helper` (STUB, utility 2.0).
- **Unconstrained Serialized Size**: 89 Gemma 4 BPE tokens.
- **Target Budget**: 40 tokens (forcing aggressive multi-stage reduction).

### Traced Downgrade Steps:

| Step | Candidate Symbol | Pre-Tier | Action Taken | Post-Tier | Tokens After Step | Target Budget | Under Budget? |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Initial** | *All 4 symbols* | — | Optimizer Selection | — | **89** | 40 | No |
| **Step 1** | `mod.low_priority_helper` | STUB (1) | Prune lowest-utility STUB | EXCLUDED (0) | 80 | 40 | No |
| **Step 2** | `mod.ParentClass` | STUB (1) | Prune container STUB | EXCLUDED (0) | 80* | 40 | No |
| **Step 3** | `mod.ParentClass.secondary_method` | SKELETON (2) | Prune lowest-utility SKELETON | STUB (1) | 73 | 40 | No |
| **Step 4** | `mod.ParentClass.critical_method` | FULL (3) | Prune lowest-utility FULL | SKELETON (2) | 42 | 40 | No |
| **Stage 4** | *Fail-Safe Line Truncation* | — | Truncate bottom lines | — | **39** | 40 | **YES** |

*\*Note on Step 2*: Even though the optimizer's explicit node for `ParentClass` was excluded, the context serializer detects that child methods `critical_method` and `secondary_method` remain active. To satisfy AST grammar and prevent syntax errors, the serializer automatically synthesizes the minimal container header `class ParentClass:`. Thus, child methods are never rendered as orphan syntax blocks.

### AST Syntactic Validation of Output Context:
The final context text after Stage 4 line truncation:
```python
# File: mod.py
class ParentClass:
    def critical_method(self, x: int) -> int:
        ...

# [Context budget limit reached]
```
Running `ast.parse()` on this materialized string succeeds with **Zero Syntax Errors** (`is_valid_ast = True`).

---

## 4. Relationship Between Optimizer Output and Budget Guard Fallback

A key peer-review question is: **Does the mathematical optimizer output change when fallback occurs?**

- **The Optimizer Output Vector $\mathbf{x}^*$**: The HiGHS MILP solver produces the globally optimal binary assignment vector $\mathbf{x}^* \in \{0, 1\}^{|\mathcal{V}| \times |\mathcal{R}|}$ based on additive token costs $\sum c(i, r) x_{ir} \le B$. The optimizer does not re-solve during the fallback loop; its static mathematical output vector remains unchanged.
- **The Materialized Context $\mathcal{C}(\mathbf{x})$**: The serializer operates as a post-optimization compilation stage. In $98.41\%$ of benchmark tasks (2,539 / 2,580 evaluations), the optimizer's selected tiers fit strictly within the real-token budget with zero trimming required.
- **Why Fallback is Necessary**: In the remaining $1.59\%$ of evaluations (41 tasks), subword tokenizer boundary effects (such as whitespace merging across `# File:` banners) cause the serialized token count to exceed $B$ by $1\text{--}12$ tokens. The fallback loop modifies `active_tiers` locally to absorb these boundary discrepancies.
- **Guarantee Status**: The budget ceiling $T \le B$ is guaranteed by **algorithmic termination of the serializer loop**, where Stage 4 monotonically truncates lines until $T \le B$ is satisfied.

---

## 5. Required Manuscript Prose Revision

Replace the ambiguous phrase:
> *"a deterministic 4-stage fallback trimming loop downgrades STUB $\to$ SKELETON $\to$ FULL $\to$ line truncation"*

with the exact, unambiguous scientific specification:
> *"If subword boundary effects across file banners cause joint context size to exceed the budget ($T > B$), a deterministic fallback trimming loop monotonically reduces entity resolutions in ascending order of (tier, utility)—pruning STUBs to omission, SKELETONs to STUBs, and FULL implementations to SKELETONs—with bottom-line truncation as a strict fail-safe, guaranteeing $T \le B$ with $100.0\%$ zero violations."*

