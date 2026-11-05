# MR-TopoS: Strategic Reset Definitive Statistical Analysis

**Total Tasks Analyzed:** 129
**Budgets Evaluated:** [np.int64(2000), np.int64(4000), np.int64(8000), np.int64(16000)]
**Total Executed Ledger Records:** 5160

## 1. Factorial Ablation Analysis (Conditions A-F)
A: Scoped BM25 (Baseline)
B: Multi-Resolution Only (No Containment, No Topo)
C: MR + AST Containment (No Topo)
D: MR + AST Containment + Dependency (Full PC-MCKP)
E: Constraint-Aware Greedy Heuristic
F: Exact MILP Context Compiler (MR-TopoS Final)

### Mean Performance by Condition and Budget
| Budget | Condition | Recall (All) | Recall (Pre-exist) | Retained Symbols | Full | Skel | Stub | Syntax Valid % | Solve Time (ms) |
|---|---|---|---|---|---|---|---|---|---|
| 2000 | `A_scoped_bm25` | 37.28% | 43.62% | 12.6 | 12.6 | 0.0 | 0.0 | 75.2% | 127.01ms |
| 2000 | `B_mr_only` | 53.89% | 63.26% | 52.9 | 19.5 | 32.2 | 1.1 | 100.0% | 66.46ms |
| 2000 | `C_mr_containment` | 48.46% | 57.12% | 50.9 | 19.5 | 30.0 | 1.4 | 100.0% | 91.37ms |
| 2000 | `D_mr_containment_dep` | 48.46% | 57.12% | 50.9 | 19.5 | 30.0 | 1.4 | 100.0% | 83.92ms |
| 2000 | `E_mrtopos_con_greedy` | 47.30% | 55.80% | 50.4 | 19.6 | 29.5 | 1.3 | 100.0% | 26.05ms |
| 2000 | `F_mrtopos_milp` | 48.46% | 57.12% | 50.9 | 19.5 | 30.0 | 1.4 | 100.0% | 77.94ms |
| 4000 | `A_scoped_bm25` | 42.82% | 50.11% | 20.0 | 20.0 | 0.0 | 0.0 | 66.7% | 158.82ms |
| 4000 | `B_mr_only` | 55.89% | 65.79% | 56.5 | 33.6 | 22.7 | 0.2 | 100.0% | 50.75ms |
| 4000 | `C_mr_containment` | 54.34% | 64.03% | 55.2 | 32.5 | 22.1 | 0.5 | 100.0% | 70.22ms |
| 4000 | `D_mr_containment_dep` | 54.08% | 63.74% | 55.1 | 32.5 | 22.1 | 0.5 | 100.0% | 62.43ms |
| 4000 | `E_mrtopos_con_greedy` | 49.39% | 58.43% | 54.3 | 33.2 | 20.7 | 0.4 | 100.0% | 23.69ms |
| 4000 | `F_mrtopos_milp` | 54.08% | 63.74% | 55.1 | 32.5 | 22.1 | 0.5 | 100.0% | 57.65ms |
| 8000 | `A_scoped_bm25` | 55.55% | 64.81% | 33.1 | 33.1 | 0.0 | 0.0 | 77.5% | 244.59ms |
| 8000 | `B_mr_only` | 56.67% | 66.67% | 58.7 | 46.1 | 12.6 | 0.0 | 100.0% | 35.78ms |
| 8000 | `C_mr_containment` | 55.20% | 65.01% | 58.3 | 44.5 | 13.3 | 0.4 | 100.0% | 61.28ms |
| 8000 | `D_mr_containment_dep` | 55.20% | 65.01% | 58.3 | 44.5 | 13.3 | 0.4 | 100.0% | 65.99ms |
| 8000 | `E_mrtopos_con_greedy` | 55.31% | 65.13% | 57.3 | 45.1 | 12.0 | 0.2 | 100.0% | 39.06ms |
| 8000 | `F_mrtopos_milp` | 55.20% | 65.01% | 58.3 | 44.5 | 13.3 | 0.4 | 100.0% | 58.27ms |
| 16000 | `A_scoped_bm25` | 59.61% | 70.00% | 47.8 | 47.8 | 0.0 | 0.0 | 87.6% | 330.92ms |
| 16000 | `B_mr_only` | 57.05% | 67.11% | 59.7 | 54.2 | 5.4 | 0.0 | 100.0% | 21.19ms |
| 16000 | `C_mr_containment` | 57.05% | 67.11% | 59.9 | 53.6 | 6.0 | 0.3 | 100.0% | 25.72ms |
| 16000 | `D_mr_containment_dep` | 57.05% | 67.11% | 59.9 | 53.6 | 6.0 | 0.3 | 100.0% | 23.00ms |
| 16000 | `E_mrtopos_con_greedy` | 56.67% | 66.67% | 59.5 | 53.6 | 5.6 | 0.3 | 100.0% | 27.81ms |
| 16000 | `F_mrtopos_milp` | 57.05% | 67.11% | 59.9 | 53.6 | 6.0 | 0.3 | 100.0% | 22.34ms |

### Paired Marginal Contributions (Step-by-Step)
| Budget | Transition | Marginal Mechanism | Mean Recall Delta | 95% Confidence Interval | p-value | Significance |
|---|---|---|---|---|---|---|
| 2000 | `A_scoped_bm25` &rarr; `B_mr_only` | A -> B: Multi-Resolution Representation | +16.61% | [+8.46%, +24.75%] | 9.3077e-05 | *** |
| 2000 | `B_mr_only` &rarr; `C_mr_containment` | B -> C: AST Precedence / Containment | -5.43% | [-9.19%, -1.67%] | 0.0050 | ** |
| 2000 | `C_mr_containment` &rarr; `D_mr_containment_dep` | C -> D: Topological Dependency Scoring | +0.00% | [+0.00%, +0.00%] | 1.0000 | n.s. |
| 2000 | `D_mr_containment_dep` &rarr; `E_mrtopos_con_greedy` | D -> E: Greedy Context Packing | -1.16% | [-2.87%, +0.55%] | 0.1807 | n.s. |
| 2000 | `E_mrtopos_con_greedy` &rarr; `F_mrtopos_milp` | E -> F: Exact MILP vs Greedy | +1.16% | [-0.55%, +2.87%] | 0.1807 | n.s. |
| 2000 | `A_scoped_bm25` &rarr; `F_mrtopos_milp` | A -> F: Total Net MR-TopoS Gain | +11.18% | [+2.58%, +19.78%] | 0.0112 | * |
| 4000 | `A_scoped_bm25` &rarr; `B_mr_only` | A -> B: Multi-Resolution Representation | +13.07% | [+6.77%, +19.37%] | 7.1374e-05 | *** |
| 4000 | `B_mr_only` &rarr; `C_mr_containment` | B -> C: AST Precedence / Containment | -1.55% | [-3.32%, +0.21%] | 0.0840 | n.s. |
| 4000 | `C_mr_containment` &rarr; `D_mr_containment_dep` | C -> D: Topological Dependency Scoring | -0.26% | [-0.77%, +0.25%] | 0.3192 | n.s. |
| 4000 | `D_mr_containment_dep` &rarr; `E_mrtopos_con_greedy` | D -> E: Greedy Context Packing | -4.69% | [-8.37%, -1.01%] | 0.0130 | * |
| 4000 | `E_mrtopos_con_greedy` &rarr; `F_mrtopos_milp` | E -> F: Exact MILP vs Greedy | +4.69% | [+1.01%, +8.37%] | 0.0130 | * |
| 4000 | `A_scoped_bm25` &rarr; `F_mrtopos_milp` | A -> F: Total Net MR-TopoS Gain | +11.26% | [+5.18%, +17.35%] | 0.0004 | *** |
| 8000 | `A_scoped_bm25` &rarr; `B_mr_only` | A -> B: Multi-Resolution Representation | +1.12% | [-3.06%, +5.30%] | 0.5965 | n.s. |
| 8000 | `B_mr_only` &rarr; `C_mr_containment` | B -> C: AST Precedence / Containment | -1.47% | [-3.23%, +0.29%] | 0.1013 | n.s. |
| 8000 | `C_mr_containment` &rarr; `D_mr_containment_dep` | C -> D: Topological Dependency Scoring | +0.00% | [+0.00%, +0.00%] | 1.0000 | n.s. |
| 8000 | `D_mr_containment_dep` &rarr; `E_mrtopos_con_greedy` | D -> E: Greedy Context Packing | +0.11% | [-0.11%, +0.33%] | 0.3192 | n.s. |
| 8000 | `E_mrtopos_con_greedy` &rarr; `F_mrtopos_milp` | E -> F: Exact MILP vs Greedy | -0.11% | [-0.33%, +0.11%] | 0.3192 | n.s. |
| 8000 | `A_scoped_bm25` &rarr; `F_mrtopos_milp` | A -> F: Total Net MR-TopoS Gain | -0.35% | [-4.13%, +3.44%] | 0.8563 | n.s. |
| 16000 | `A_scoped_bm25` &rarr; `B_mr_only` | A -> B: Multi-Resolution Representation | -2.55% | [-6.29%, +1.19%] | 0.1790 | n.s. |
| 16000 | `B_mr_only` &rarr; `C_mr_containment` | B -> C: AST Precedence / Containment | +0.00% | [+0.00%, +0.00%] | 1.0000 | n.s. |
| 16000 | `C_mr_containment` &rarr; `D_mr_containment_dep` | C -> D: Topological Dependency Scoring | +0.00% | [+0.00%, +0.00%] | 1.0000 | n.s. |
| 16000 | `D_mr_containment_dep` &rarr; `E_mrtopos_con_greedy` | D -> E: Greedy Context Packing | -0.39% | [-1.15%, +0.38%] | 0.3192 | n.s. |
| 16000 | `E_mrtopos_con_greedy` &rarr; `F_mrtopos_milp` | E -> F: Exact MILP vs Greedy | +0.39% | [-0.38%, +1.15%] | 0.3192 | n.s. |
| 16000 | `A_scoped_bm25` &rarr; `F_mrtopos_milp` | A -> F: Total Net MR-TopoS Gain | -2.55% | [-6.29%, +1.19%] | 0.1790 | n.s. |

## 2. Candidate Pool Saturation Analysis (K in {60, 100, 200, 400})
| Budget | Pool Size K | Recall (All) | Recall (Pre-exist) | Retained Symbols | Solve Time (ms) |
|---|---|---|---|---|---|
| 2000 | K =  60 | 48.46% | 57.12% | 50.9 | 77.94ms |
| 2000 | K = 100 | 51.94% | 60.81% | 73.6 | 104.08ms |
| 2000 | K = 200 | 45.62% | 52.63% | 103.8 | 146.82ms |
| 2000 | K = 400 | 35.29% | 40.67% | 131.5 | 194.72ms |
| 4000 | K =  60 | 54.08% | 63.74% | 55.1 | 57.65ms |
| 4000 | K = 100 | 60.08% | 70.89% | 88.0 | 100.28ms |
| 4000 | K = 200 | 65.03% | 76.21% | 145.7 | 281.87ms |
| 4000 | K = 400 | 60.89% | 70.66% | 205.5 | 280.51ms |
| 8000 | K =  60 | 55.20% | 65.01% | 58.3 | 58.27ms |
| 8000 | K = 100 | 63.70% | 74.98% | 94.4 | 135.05ms |
| 8000 | K = 200 | 70.46% | 82.64% | 173.4 | 237.31ms |
| 8000 | K = 400 | 72.47% | 85.06% | 286.2 | 435.13ms |
| 16000 | K =  60 | 57.05% | 67.11% | 59.9 | 22.34ms |
| 16000 | K = 100 | 65.94% | 77.51% | 99.2 | 71.92ms |
| 16000 | K = 200 | 72.55% | 85.76% | 189.1 | 181.83ms |
| 16000 | K = 400 | 76.70% | 90.57% | 340.5 | 256.19ms |

### Paired Candidate Pool Scaling (K=60 -> K=400)
| Budget | Transition | Mean Recall Delta | 95% Confidence Interval | p-value | Significance |
|---|---|---|---|---|---|
| 2000 | K=60 &rarr; K=100 | +3.49% | [-2.38%, +9.35%] | 0.2416 | n.s. |
| 2000 | K=60 &rarr; K=200 | -2.84% | [-10.29%, +4.61%] | 0.4523 | n.s. |
| 2000 | K=60 &rarr; K=400 | -13.17% | [-21.22%, -5.12%] | 0.0015 | ** |
| 4000 | K=60 &rarr; K=100 | +6.00% | [+0.28%, +11.72%] | 0.0398 | * |
| 4000 | K=60 &rarr; K=200 | +10.95% | [+3.45%, +18.45%] | 0.0045 | ** |
| 4000 | K=60 &rarr; K=400 | +6.81% | [-1.24%, +14.86%] | 0.0965 | n.s. |
| 8000 | K=60 &rarr; K=100 | +8.50% | [+3.44%, +13.55%] | 0.0011 | ** |
| 8000 | K=60 &rarr; K=200 | +15.26% | [+8.48%, +22.05%] | 1.8484e-05 | *** |
| 8000 | K=60 &rarr; K=400 | +17.27% | [+9.96%, +24.58%] | 7.4051e-06 | *** |
| 16000 | K=60 &rarr; K=100 | +8.88% | [+4.03%, +13.74%] | 0.0004 | *** |
| 16000 | K=60 &rarr; K=200 | +15.50% | [+9.07%, +21.93%] | 4.8679e-06 | *** |
| 16000 | K=60 &rarr; K=400 | +19.65% | [+12.74%, +26.55%] | 1.0924e-07 | *** |

## 3. Authentic Aider RepoMap Baseline Comparison
| Budget | Method | Recall (All) | Recall (Pre-exist) | Retained Symbols | Syntax Valid % | Solve Time (ms) | Compliant % |
|---|---|---|---|---|---|---|---|
| 2000 | Scoped BM25 | 37.28% | 43.62% | 12.6 | 75.2% | 127.01ms | 100.0% |
| 2000 | Aider RepoMap | 44.53% | 53.06% | 161.8 | 0.0% | 1195.59ms | 100.0% |
| 2000 | MR-TopoS (MILP) | 48.46% | 57.12% | 50.9 | 100.0% | 77.94ms | 100.0% |
| 4000 | Scoped BM25 | 42.82% | 50.11% | 20.0 | 66.7% | 158.82ms | 100.0% |
| 4000 | Aider RepoMap | 52.79% | 62.42% | 302.5 | 0.0% | 1162.08ms | 100.0% |
| 4000 | MR-TopoS (MILP) | 54.08% | 63.74% | 55.1 | 100.0% | 57.65ms | 100.0% |
| 8000 | Scoped BM25 | 55.55% | 64.81% | 33.1 | 77.5% | 244.59ms | 100.0% |
| 8000 | Aider RepoMap | 56.19% | 67.00% | 580.4 | 0.0% | 1283.00ms | 100.0% |
| 8000 | MR-TopoS (MILP) | 55.20% | 65.01% | 58.3 | 100.0% | 58.27ms | 100.0% |
| 16000 | Scoped BM25 | 59.61% | 70.00% | 47.8 | 87.6% | 330.92ms | 100.0% |
| 16000 | Aider RepoMap | 67.85% | 80.55% | 1105.7 | 0.0% | 1425.04ms | 100.0% |
| 16000 | MR-TopoS (MILP) | 57.05% | 67.11% | 59.9 | 100.0% | 22.34ms | 100.0% |

### Paired Head-to-Head: MR-TopoS vs Aider RepoMap
| Budget | MR-TopoS Mean Recall | Aider Mean Recall | Mean Difference | 95% CI | p-value | Verdict |
|---|---|---|---|---|---|---|
| 2000 | 48.46% | 44.53% | +3.93% | [-7.85%, +15.71%] | 0.5100 | Parity (p >= 0.05) |
| 4000 | 54.08% | 52.79% | +1.28% | [-9.13%, +11.70%] | 0.8076 | Parity (p >= 0.05) |
| 8000 | 55.20% | 56.19% | -0.99% | [-11.18%, +9.19%] | 0.8474 | Parity (p >= 0.05) |
| 16000 | 57.05% | 67.85% | -10.79% | [-20.11%, -1.48%] | 0.0235 | Disadvantage (p < 0.05) |
