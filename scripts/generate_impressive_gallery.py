"""
Generate Five Impressive, Highly Polished 1200x675 Gallery Figures for Kaggle Writeup.

Outputs:
1. paper/figures/gallery_1_architecture.png (1200x675)
2. paper/figures/gallery_2_recall_benchmark.png (1200x675)
3. paper/figures/gallery_3_gemma4_latency.png (1200x675)
4. paper/figures/gallery_4_scope_deduplication.png (1200x675)
5. paper/figures/gallery_5_solver_scaling.png (1200x675)
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

os.makedirs('paper/figures', exist_ok=True)

# Common styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#30363d'
plt.rcParams['axes.linewidth'] = 1.0

DARK_BG = '#070a13'
CARD_BG = '#0f172a'
BORDER_COL = '#1e293b'
TEXT_WHITE = '#f8fafc'
TEXT_MUTED = '#94a3b8'
CYAN = '#38bdf8'
PURPLE = '#c084fc'
PINK = '#f472b6'
EMERALD = '#34d399'
AMBER = '#fbbf24'
CORAL = '#f43f5e'

def save_fig(fig, path):
    plt.tight_layout(pad=1.5)
    fig.savefig(path, dpi=150, facecolor=DARK_BG, edgecolor='none')
    plt.close(fig)
    print(f"Generated {path} (1200x675)")

# -------------------------------------------------------------
# Figure 1: Architecture
# -------------------------------------------------------------
def make_fig1_architecture():
    # 8 x 4.5 inches @ 150 dpi = 1200 x 675 px
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.axis('off')

    # Title & Subtitle
    ax.text(0.5, 0.94, 'MR-AST: Context Compilation Architecture',
            color=TEXT_WHITE, fontsize=15, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.88, 'From Raw Repository Forest to Grammar-Preserving Token Working Memory',
            color=TEXT_MUTED, fontsize=9.5, ha='center', va='center')

    # 4 Pipeline Boxes
    boxes = [
        {'title': '1. AST Forest', 'color': CYAN, 'x': 0.04, 'w': 0.20,
         'text': '• Tree-sitter AST\n• Module -> Class -> Def\n• Hierarchical containment\n• Monotonic token costs'},
        {'title': '2. 4-Tier Lattice', 'color': PURPLE, 'x': 0.28, 'w': 0.20,
         'text': '• T3: Full Code (100%)\n• T2: Skeleton (Signatures)\n• T1: Stub (Headers)\n• T0: Excluded (0 tokens)'},
        {'title': '3. Pure MCKP', 'color': PINK, 'x': 0.52, 'w': 0.20,
         'text': '• max sum a_r * u_i * x_ir\n• Schedule K_step(B) depth\n• Dynamic pool [60, 400]\n• Pure Greedy in O(N log N)'},
        {'title': '4. Serializer C(x)', 'color': EMERALD, 'x': 0.76, 'w': 0.20,
         'text': '• Shared parent recovery\n• 56.05% deduplication\n• Invariant 1: ast.parse != Err\n• Atomic monotonic pruning'}
    ]

    for b in boxes:
        rect = FancyBboxPatch((b['x'], 0.24), b['w'], 0.58, facecolor=CARD_BG, edgecolor=b['color'],
                              linewidth=1.8, transform=ax.transAxes, zorder=2,
                              boxstyle="round,pad=0.012")
        ax.add_patch(rect)
        ax.text(b['x'] + b['w']/2, 0.76, b['title'], color=b['color'], fontsize=10.5, fontweight='bold',
                ha='center', va='center', transform=ax.transAxes, zorder=3)
        ax.plot([b['x']+0.02, b['x']+b['w']-0.02], [0.71, 0.71], color='#334155', linewidth=1, transform=ax.transAxes, zorder=3)
        ax.text(b['x'] + 0.015, 0.48, b['text'], color=TEXT_WHITE, fontsize=8.2, ha='left', va='center',
                transform=ax.transAxes, zorder=3, linespacing=1.45)

    # Connecting arrows
    for i in range(len(boxes) - 1):
        x1 = boxes[i]['x'] + boxes[i]['w']
        x2 = boxes[i+1]['x']
        ax.annotate('', xy=(x2, 0.53), xytext=(x1, 0.53), xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color='#64748b', lw=2.0), zorder=4)

    # Downstream Agent Banner
    agent_rect = FancyBboxPatch((0.10, 0.04), 0.80, 0.14, facecolor='#1e1b4b', edgecolor='#6366f1',
                                linewidth=1.5, transform=ax.transAxes, zorder=2,
                                boxstyle="round,pad=0.012")
    ax.add_patch(agent_rect)
    ax.text(0.5, 0.12, 'Downstream Agent: Google Gemma 4 31B (Vertex AI Inferences)',
            color='#c7d2fe', fontsize=10, fontweight='bold', ha='center', va='center', transform=ax.transAxes)
    ax.text(0.5, 0.07, '-28.3% Generation Latency (p=0.038) • 1.55x Retained Implementations • 100% Valid Syntax',
            color='#a5b4fc', fontsize=8.2, ha='center', va='center', transform=ax.transAxes)

    save_fig(fig, 'paper/figures/gallery_1_architecture.png')

# -------------------------------------------------------------
# Figure 2: Recall & Cross-Validation
# -------------------------------------------------------------
def make_fig2_recall():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5), facecolor=DARK_BG)

    for ax in (ax1, ax2):
        ax.set_facecolor(CARD_BG)
        ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
        ax.tick_params(colors=TEXT_MUTED, labelsize=8.5)
        for spine in ax.spines.values():
            spine.set_color('#334155')

    budgets = ['2k', '4k', '8k', '16k']
    x = np.arange(len(budgets))
    mr_ast = [49.88, 64.76, 71.72, 76.92]
    scoped_bm25 = [41.30, 44.78, 58.22, 60.48]
    aider = [39.15, 51.77, 53.06, 62.74]
    static_k60 = [49.88, 55.94, 55.94, 56.16]

    # Left Plot
    ax1.plot(x, mr_ast, marker='o', linewidth=2.4, color=CYAN, label='MR-AST (Dynamic)', zorder=5)
    ax1.plot(x, scoped_bm25, marker='s', linewidth=1.8, color=AMBER, linestyle='--', label='Scoped BM25', zorder=4)
    ax1.plot(x, aider, marker='^', linewidth=1.8, color=PURPLE, linestyle='-.', label='Aider RepoMap', zorder=3)
    ax1.plot(x, static_k60, marker='x', linewidth=1.6, color=CORAL, linestyle=':', label='Static K=60', zorder=2)

    ax1.set_title('Gold Recall Across Budgets (66-Task Partition)', color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=10)
    ax1.set_xlabel('Token Budget (Gemma 4 Tokenizer)', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax1.set_ylabel('Cluster-Aggregated Gold Recall (%)', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax1.set_xticks(x)
    ax1.set_xticklabels(budgets)
    ax1.set_ylim(34, 82)
    leg1 = ax1.legend(facecolor='#1e293b', edgecolor='#334155', fontsize=8.0, loc='lower right')
    for text in leg1.get_texts():
        text.set_color(TEXT_WHITE)

    ax1.annotate('+16.44 pp (p=0.0043)', xy=(3, 76.92), xytext=(1.8, 77.5),
                 color=CYAN, fontsize=8.2, fontweight='bold',
                 arrowprops=dict(arrowstyle="->", color=CYAN, lw=1.2))

    # Right Plot: Cross Validation
    fold1_test = [47.61, 67.63, 73.36, 76.92]
    fold2_test = [46.24, 62.31, 71.53, 76.47]

    ax2.plot(x, fold1_test, marker='o', linewidth=2.2, color=EMERALD, label='Fold 1 Test (Heldout 66 tasks)')
    ax2.plot(x, fold2_test, marker='D', linewidth=2.2, color=PINK, linestyle='--', label='Fold 2 Test (Dev 63 tasks)')

    ax2.set_title('Zero-Leakage 2-Fold Cross-Validation', color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=10)
    ax2.set_xlabel('Token Budget', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax2.set_ylabel('Out-of-Fold Test Recall (%)', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax2.set_xticks(x)
    ax2.set_xticklabels(budgets)
    ax2.set_ylim(40, 82)
    leg2 = ax2.legend(facecolor='#1e293b', edgecolor='#334155', fontsize=8.0, loc='lower right')
    for text in leg2.get_texts():
        text.set_color(TEXT_WHITE)

    ax2.annotate('Parity: 76.9% vs 76.5%', xy=(3, 76.92), xytext=(1.6, 52),
                 color=TEXT_WHITE, fontsize=8.2,
                 arrowprops=dict(arrowstyle="->", color='#94a3b8', lw=1.0))

    save_fig(fig, 'paper/figures/gallery_2_recall_benchmark.png')

# -------------------------------------------------------------
# Figure 3: Gemma 4 Latency & Taxonomy
# -------------------------------------------------------------
def make_fig3_latency():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5), facecolor=DARK_BG)

    for ax in (ax1, ax2):
        ax.set_facecolor(CARD_BG)
        for spine in ax.spines.values():
            spine.set_color('#334155')

    # Left: Latency
    ax1.grid(True, linestyle='--', alpha=0.25, color='#475569', axis='y')
    ax1.tick_params(colors=TEXT_MUTED, labelsize=8.5)

    paradigms = ['Raw BM25', 'Scoped BM25', 'MR-AST']
    latencies = [10.22, 10.55, 7.57]
    errors = [0.85, 0.92, 0.64]
    colors = ['#64748b', AMBER, CYAN]

    bars = ax1.bar(paradigms, latencies, yerr=errors, capsize=4, color=colors, width=0.52, edgecolor='#334155')
    ax1.set_title('Gemma 4 31B Latency at B=2,000 (s)', color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=10)
    ax1.set_ylabel('Mean Latency (s)', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax1.set_ylim(0, 13)

    for bar, val in zip(bars, latencies):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 1.1, f'{val:.2f}s',
                 ha='center', va='bottom', color=TEXT_WHITE, fontsize=8.5, fontweight='bold')

    ax1.annotate('-28.3% Latency\n(p=0.038)', xy=(2, 7.57), xytext=(1.4, 3.8),
                 color=CYAN, fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle="->", color=CYAN, lw=1.2))

    # Right: Taxonomy
    labels = ['Line Drift\n(61.1%)', 'Indentation\n(22.2%)', 'Missing Hunk\n(16.7%)']
    sizes = [61.1, 22.2, 16.7]
    donut_colors = [CORAL, '#f97316', AMBER]

    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
                                      colors=donut_colors, pctdistance=0.72,
                                      wedgeprops=dict(width=0.42, edgecolor=CARD_BG, linewidth=2.0))

    for t in texts:
        t.set_color(TEXT_MUTED)
        t.set_fontsize(8.0)
    for at in autotexts:
        at.set_color('#ffffff')
        at.set_fontsize(8.0)
        at.set_fontweight('bold')

    ax2.set_title('Single-Turn Diff Failures (0% git apply)', color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=10)

    save_fig(fig, 'paper/figures/gallery_3_gemma4_latency.png')

# -------------------------------------------------------------
# Figure 4: Scope Taxation & Parent Deduplication
# -------------------------------------------------------------
def make_fig4_scope_dedup():
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.axis('off')

    ax.text(0.5, 0.94, 'Scope Taxation Breakdown & Post-Hoc Reconstruction',
            color=TEXT_WHITE, fontsize=15, fontweight='bold', ha='center', va='center')
    ax.text(0.5, 0.88, 'How MR-AST Eliminates Redundant Enclosing Scopes to Reclaim Working Memory',
            color=TEXT_MUTED, fontsize=9.5, ha='center', va='center')

    # Left: The Problem
    prob_rect = FancyBboxPatch((0.05, 0.16), 0.42, 0.66, facecolor=CARD_BG, edgecolor=CORAL,
                               linewidth=1.8, transform=ax.transAxes, zorder=2,
                               boxstyle="round,pad=0.015")
    ax.add_patch(prob_rect)
    ax.text(0.26, 0.76, 'Problem: Monolithic Scoping Tax', color=CORAL, fontsize=11, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes)
    ax.plot([0.08, 0.44], [0.71, 0.71], color='#334155', linewidth=1, transform=ax.transAxes)
    prob_text = (
        "• Redundant class headers repeated for every method\n"
        "• Monolithic class scoping exhausts budget rapidly\n"
        "• Caps symbol retention at ~12.5 symbols at 2k\n"
        "• Starves LLM of necessary peripheral context\n"
        "• Whole-file fallbacks displace target modules (Paradox)"
    )
    ax.text(0.08, 0.46, prob_text, color=TEXT_WHITE, fontsize=8.5, ha='left', va='center',
            transform=ax.transAxes, linespacing=1.6)

    # Right: The Solution
    sol_rect = FancyBboxPatch((0.53, 0.16), 0.42, 0.66, facecolor=CARD_BG, edgecolor=EMERALD,
                              linewidth=1.8, transform=ax.transAxes, zorder=2,
                              boxstyle="round,pad=0.015")
    ax.add_patch(sol_rect)
    ax.text(0.74, 0.76, 'Solution: Post-Hoc Reconstruction', color=EMERALD, fontsize=11, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes)
    ax.plot([0.56, 0.92], [0.71, 0.71], color='#334155', linewidth=1, transform=ax.transAxes)
    sol_text = (
        "• Optimizer omits parent classes (zero taxation)\n"
        "• Serializer C(x) reconstructs parent headers post-hoc\n"
        "• Median reconstruction cost: only 5.0 tokens per class\n"
        "• 56.05% pooled token deduplication rate\n"
        "• Retains 1.55x more full code implementations at 2k!"
    )
    ax.text(0.56, 0.46, sol_text, color=TEXT_WHITE, fontsize=8.5, ha='left', va='center',
            transform=ax.transAxes, linespacing=1.6)

    # Bottom Callout Pill
    callout_rect = FancyBboxPatch((0.15, 0.04), 0.70, 0.09, facecolor='#1e293b', edgecolor=CYAN,
                                  linewidth=1.2, transform=ax.transAxes, zorder=2,
                                  boxstyle="round,pad=0.01")
    ax.add_patch(callout_rect)
    ax.text(0.5, 0.085, 'Eliminated 12,224 redundant definitions across 493 reconstructed method runs',
            color=CYAN, fontsize=9.0, fontweight='bold', ha='center', va='center', transform=ax.transAxes)

    save_fig(fig, 'paper/figures/gallery_4_scope_deduplication.png')

# -------------------------------------------------------------
# Figure 5: Solver Complexity & Scaling
# -------------------------------------------------------------
def make_fig5_solver():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5), facecolor=DARK_BG)

    for ax in (ax1, ax2):
        ax.set_facecolor(CARD_BG)
        ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
        ax.tick_params(colors=TEXT_MUTED, labelsize=8.5)
        for spine in ax.spines.values():
            spine.set_color('#334155')

    N_vals = [20, 60, 200, 800]
    highs_mean = [2.89, 2.80, 8.05, 317.11]
    greedy_mean = [1.20, 9.90, 101.62, 6582.98]
    speedups = [0.42, 3.53, 12.62, 20.76]

    x = np.arange(len(N_vals))

    # Left Plot: Latency on log scale
    ax1.plot(x, highs_mean, marker='o', linewidth=2.2, color=CYAN, label='HiGHS Exact MILP')
    ax1.plot(x, greedy_mean, marker='s', linewidth=2.2, color=AMBER, linestyle='--', label='Python Greedy Loop')
    ax1.set_yscale('log')
    ax1.set_title('Solver Execution Latency (ms, log scale)', color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=10)
    ax1.set_xlabel('Candidate Pool Size (N)', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax1.set_ylabel('Mean Solve Time (ms)', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax1.set_xticks(x)
    ax1.set_xticklabels(N_vals)
    leg1 = ax1.legend(facecolor='#1e293b', edgecolor='#334155', fontsize=8.0, loc='upper left')
    for text in leg1.get_texts():
        text.set_color(TEXT_WHITE)

    # Right Plot: HiGHS Speedup Factor
    bars = ax2.bar(x, speedups, width=0.52, color=[CORAL if s < 1 else EMERALD for s in speedups],
                   edgecolor='#334155')
    ax2.set_title('HiGHS Speedup over Python Loop (x)', color=TEXT_WHITE, fontsize=9.5, fontweight='bold', pad=10)
    ax2.set_xlabel('Candidate Pool Size (N)', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax2.set_ylabel('Speedup Factor', color=TEXT_MUTED, fontsize=8.5, labelpad=6)
    ax2.set_xticks(x)
    ax2.set_xticklabels(N_vals)
    ax2.set_ylim(0, 24)

    for bar, val in zip(bars, speedups):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.8, f'{val:.1f}x',
                 ha='center', va='bottom', color=TEXT_WHITE, fontsize=8.5, fontweight='bold')

    ax2.annotate('20.8x Speedup\n0.0% Gap', xy=(3, 20.76), xytext=(2.0, 16),
                 color=EMERALD, fontsize=8.5, fontweight='bold',
                 arrowprops=dict(arrowstyle="->", color=EMERALD, lw=1.2))

    save_fig(fig, 'paper/figures/gallery_5_solver_scaling.png')

if __name__ == '__main__':
    make_fig1_architecture()
    make_fig2_recall()
    make_fig3_latency()
    make_fig4_scope_dedup()
    make_fig5_solver()

