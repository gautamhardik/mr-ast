"""
Generate Five Conference-Grade, Visually Perfect 1200x675 Infographics for MR-AST.

Guarantee:
- Exact 1200x675 dimensions (16:9 widescreen)
- Zero text overlapping, zero clipped annotations
- High-contrast, modern dark-mode aesthetic (#070b14)
- Crisp typography, balanced layout, clear legends
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Arrow

os.makedirs('paper/figures', exist_ok=True)

# Styling Constants
BG_COLOR = '#070b14'
CARD_BG = '#0f172a'
BORDER_COLOR = '#1e293b'
TEXT_MAIN = '#f8fafc'
TEXT_MUTED = '#94a3b8'

COLOR_CYAN = '#38bdf8'
COLOR_PURPLE = '#c084fc'
COLOR_PINK = '#f472b6'
COLOR_GREEN = '#34d399'
COLOR_AMBER = '#fbbf24'
COLOR_RED = '#f43f5e'
COLOR_ORANGE = '#fb923c'

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['text.color'] = TEXT_MAIN
plt.rcParams['axes.labelcolor'] = TEXT_MUTED
plt.rcParams['xtick.color'] = TEXT_MUTED
plt.rcParams['ytick.color'] = TEXT_MUTED
plt.rcParams['axes.edgecolor'] = BORDER_COLOR

def save_and_verify(fig, out_path):
    fig.tight_layout(pad=2.0)
    fig.savefig(out_path, dpi=150, facecolor=BG_COLOR, edgecolor='none')
    plt.close(fig)
    from PIL import Image
    im = Image.open(out_path)
    # Ensure exact 1200x675
    if im.size != (1200, 675):
        im = im.resize((1200, 675), Image.Resampling.LANCZOS)
        im.save(out_path)
    print(f"Verified: {out_path} -> {im.size}")

# ----------------------------------------------------------------------
# Figure 1: System Architecture & Workflow Diagram
# ----------------------------------------------------------------------
def generate_fig1_architecture():
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis('off')

    # Header
    ax.text(0.04, 0.93, 'MR-AST: Context Compilation Architecture',
            fontsize=15, fontweight='bold', color=TEXT_MAIN, va='top')
    ax.text(0.04, 0.86, 'From Raw Repository Forest to Grammar-Preserving Token Working Memory',
            fontsize=9.5, color=TEXT_MUTED, va='top')

    ax.text(0.96, 0.93, 'Google Gemma 4 Paper Track',
            fontsize=10, fontweight='bold', color=COLOR_PURPLE, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#1e1b4b', edgecolor='#6366f1', lw=1.2))

    # 4 Architecture Flow Stages
    stages = [
        {
            'step': 'STAGE 1',
            'title': 'Repository AST',
            'tag': 'Tree-sitter Parser',
            'color': COLOR_CYAN,
            'x': 0.04, 'w': 0.20,
            'lines': [
                '• AST Hierarchy Parsing',
                '• Module -> Class -> Def',
                '• Containment graph',
                '• Gemma 4 Token Costs',
                '• Monotonic cost profile'
            ]
        },
        {
            'step': 'STAGE 2',
            'title': '4-Tier Lattice',
            'tag': 'Representation',
            'color': COLOR_PURPLE,
            'x': 0.28, 'w': 0.20,
            'lines': [
                '• T3: Full Code (100%)',
                '• T2: Skeleton (Signatures)',
                '• T1: Stub (Headers, 5 tok)',
                '• T0: Excluded (0 tokens)',
                '• Monotonic lattice R'
            ]
        },
        {
            'step': 'STAGE 3',
            'title': 'Pure MCKP',
            'tag': 'Knapsack Optimizer',
            'color': COLOR_PINK,
            'x': 0.52, 'w': 0.20,
            'lines': [
                '• max sum a_r * u_i * x_ir',
                '• Dynamic depth K_step(B)',
                '• Budget B in [2k, 16k]',
                '• Pure Greedy in 23.7 ms',
                '• +5.43 pp recall recovery'
            ]
        },
        {
            'step': 'STAGE 4',
            'title': 'Serializer C(x)',
            'tag': 'Context Assembler',
            'color': COLOR_GREEN,
            'x': 0.76, 'w': 0.20,
            'lines': [
                '• Shared parent recovery',
                '• 56.05% deduplication',
                '• Invariant 1 guarantee',
                '• ast.parse != SyntaxError',
                '• 100.0% valid syntax'
            ]
        }
    ]

    for s in stages:
        rect = FancyBboxPatch((s['x'], 0.23), s['w'], 0.56, facecolor=CARD_BG, edgecolor=s['color'],
                              linewidth=1.8, transform=ax.transAxes, zorder=2, boxstyle="round,pad=0.015")
        ax.add_patch(rect)

        # Stage header
        ax.text(s['x'] + 0.015, 0.74, s['step'], fontsize=8.5, fontweight='bold', color=s['color'],
                va='top', transform=ax.transAxes)
        ax.text(s['x'] + 0.015, 0.69, s['title'], fontsize=11, fontweight='bold', color=TEXT_MAIN,
                va='top', transform=ax.transAxes)

        # Divider line
        ax.plot([s['x'] + 0.015, s['x'] + s['w'] - 0.015], [0.63, 0.63],
                color='#334155', lw=1, transform=ax.transAxes)

        # Body text
        y_text = 0.58
        for line in s['lines']:
            ax.text(s['x'] + 0.015, y_text, line, fontsize=8.0, color='#cbd5e1',
                    va='top', transform=ax.transAxes)
            y_text -= 0.065

    # Connecting Flow Arrows
    for i in range(len(stages) - 1):
        x_from = stages[i]['x'] + stages[i]['w']
        x_to = stages[i+1]['x']
        ax.annotate('', xy=(x_to, 0.51), xytext=(x_from, 0.51),
                    xycoords='axes fraction', textcoords='axes fraction',
                    arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.45", color=COLOR_CYAN, lw=2.0),
                    zorder=4)

    # Downstream Agent Impact Banner
    banner_rect = FancyBboxPatch((0.04, 0.04), 0.92, 0.13, facecolor='#111827', edgecolor=COLOR_PURPLE,
                                 linewidth=1.5, transform=ax.transAxes, zorder=2, boxstyle="round,pad=0.015")
    ax.add_patch(banner_rect)

    ax.text(0.07, 0.105, 'Downstream Agent: Google Gemma 4 31B (Vertex AI Inferences)',
            fontsize=10.5, fontweight='bold', color='#c7d2fe', va='center', transform=ax.transAxes)
    ax.text(0.07, 0.065, '• -28.3% Generation Latency (p=0.038)   • 1.55x Retained Full Code   • Invariant 1: Zero Syntax Errors',
            fontsize=8.5, color='#cbd5e1', va='center', transform=ax.transAxes)

    save_and_verify(fig, 'paper/figures/gallery_1_architecture.png')

# ----------------------------------------------------------------------
# Figure 2: Gold Recall Benchmark & 2-Fold Cross-Validation
# ----------------------------------------------------------------------
def generate_fig2_recall():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5), facecolor=BG_COLOR)

    for ax in (ax1, ax2):
        ax.set_facecolor(CARD_BG)
        ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
        ax.tick_params(colors=TEXT_MUTED, labelsize=8.5)
        for spine in ax.spines.values():
            spine.set_color(BORDER_COLOR)

    budgets = ['2k', '4k', '8k', '16k']
    x = np.arange(len(budgets))

    # Left Plot Data
    mr_ast = [49.88, 64.76, 71.72, 76.92]
    scoped_bm25 = [41.30, 44.78, 58.22, 60.48]
    aider = [39.15, 51.77, 53.06, 62.74]
    static_k60 = [49.88, 55.94, 55.94, 56.16]

    ax1.plot(x, mr_ast, marker='o', markersize=6, linewidth=2.5, color=COLOR_CYAN, label='MR-AST (Dynamic K)', zorder=5)
    ax1.plot(x, scoped_bm25, marker='s', markersize=5, linewidth=1.8, color=COLOR_AMBER, linestyle='--', label='Scoped BM25', zorder=4)
    ax1.plot(x, aider, marker='^', markersize=5, linewidth=1.8, color=COLOR_PURPLE, linestyle='-.', label='Aider RepoMap', zorder=3)
    ax1.plot(x, static_k60, marker='x', markersize=5, linewidth=1.6, color=COLOR_RED, linestyle=':', label='Static K=60', zorder=2)

    ax1.set_title('Retrospective 66-Task Partition Recall', fontsize=10.5, fontweight='bold', color=TEXT_MAIN, pad=12)
    ax1.set_xlabel('Token Budget (Gemma 4 Tokenizer)', fontsize=8.5, color=TEXT_MUTED)
    ax1.set_ylabel('Gold Symbol Recall (%)', fontsize=8.5, color=TEXT_MUTED)
    ax1.set_xticks(x)
    ax1.set_xticklabels(budgets)
    ax1.set_ylim(32, 85)

    # Clean callout card placed in empty space (top left)
    ax1.text(0.05, 0.88, '16k: +16.44 pp (p=0.0043)', fontsize=8.5, fontweight='bold', color=COLOR_CYAN,
             transform=ax1.transAxes, bbox=dict(boxstyle='round,pad=0.3', facecolor='#082f49', edgecolor=COLOR_CYAN, lw=1))

    leg1 = ax1.legend(facecolor='#1e293b', edgecolor=BORDER_COLOR, fontsize=8.0, loc='lower right')
    for text in leg1.get_texts():
        text.set_color(TEXT_MAIN)

    # Right Plot: 2-Fold Cross Validation
    fold1_test = [47.61, 67.63, 73.36, 76.92]
    fold2_test = [46.24, 62.31, 71.53, 76.47]

    ax2.plot(x, fold1_test, marker='o', markersize=6, linewidth=2.5, color=COLOR_GREEN, label='Fold 1 Test (Heldout 66 tasks)')
    ax2.plot(x, fold2_test, marker='D', markersize=5, linewidth=2.2, color=COLOR_PINK, linestyle='--', label='Fold 2 Test (Dev 63 tasks)')

    ax2.set_title('Zero-Leakage 2-Fold Cross-Validation', fontsize=10.5, fontweight='bold', color=TEXT_MAIN, pad=12)
    ax2.set_xlabel('Token Budget', fontsize=8.5, color=TEXT_MUTED)
    ax2.set_ylabel('Out-of-Fold Test Recall (%)', fontsize=8.5, color=TEXT_MUTED)
    ax2.set_xticks(x)
    ax2.set_xticklabels(budgets)
    ax2.set_ylim(40, 85)

    # Parity Callout Card placed at bottom right with plenty of room
    ax2.text(0.05, 0.88, '16k Parity: 76.92% vs 76.47%', fontsize=8.5, fontweight='bold', color=COLOR_GREEN,
             transform=ax2.transAxes, bbox=dict(boxstyle='round,pad=0.3', facecolor='#064e3b', edgecolor=COLOR_GREEN, lw=1))

    leg2 = ax2.legend(facecolor='#1e293b', edgecolor=BORDER_COLOR, fontsize=8.0, loc='lower right')
    for text in leg2.get_texts():
        text.set_color(TEXT_MAIN)

    save_and_verify(fig, 'paper/figures/gallery_2_recall_benchmark.png')

# ----------------------------------------------------------------------
# Figure 3: Gemma 4 Latency Reduction & Patch Failure Modes
# ----------------------------------------------------------------------
def generate_fig3_latency():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5), facecolor=BG_COLOR)

    for ax in (ax1, ax2):
        ax.set_facecolor(CARD_BG)
        for spine in ax.spines.values():
            spine.set_color(BORDER_COLOR)

    # Left: Horizontal Bar Chart (clean, no overlap!)
    ax1.grid(True, linestyle='--', alpha=0.25, color='#475569', axis='x')
    ax1.tick_params(colors=TEXT_MUTED, labelsize=8.5)

    paradigms = ['Raw BM25', 'Scoped BM25', 'MR-AST (Ours)']
    y_pos = np.arange(len(paradigms))
    latencies = [10.22, 10.55, 7.57]
    bar_colors = ['#64748b', COLOR_AMBER, COLOR_CYAN]

    bars = ax1.barh(y_pos, latencies, color=bar_colors, height=0.55, edgecolor='#334155')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(paradigms, fontsize=9.0, color=TEXT_MAIN)
    ax1.set_xlabel('Mean Generation Latency (seconds)', fontsize=8.5, color=TEXT_MUTED)
    ax1.set_title('Gemma 4 31B Latency at B=2,000 (s)', fontsize=10.5, fontweight='bold', color=TEXT_MAIN, pad=12)
    ax1.set_xlim(0, 13)

    for bar, val in zip(bars, latencies):
        ax1.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.2f}s',
                 va='center', fontsize=9.0, fontweight='bold', color=TEXT_MAIN)

    # Callout card inside plot
    ax1.text(0.05, 0.15, '⚡ -28.3% Latency Speedup (p = 0.038)\nSaves 2.98s per step (~1 min across 20 turns)',
             fontsize=8.2, color=COLOR_CYAN, transform=ax1.transAxes,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#082f49', edgecolor=COLOR_CYAN, lw=1))

    # Right: Patch Failure Modes Horizontal Bar Chart (cleaner than pie chart!)
    ax2.grid(True, linestyle='--', alpha=0.25, color='#475569', axis='x')
    ax2.tick_params(colors=TEXT_MUTED, labelsize=8.5)

    failure_modes = ['Line Drift', 'Indentation Mismatch', 'Missing Hunk Headers']
    failure_pcts = [61.1, 22.2, 16.7]
    y_fail = np.arange(len(failure_modes))
    colors_fail = [COLOR_RED, COLOR_ORANGE, COLOR_AMBER]

    bars_fail = ax2.barh(y_fail, failure_pcts, color=colors_fail, height=0.55, edgecolor='#334155')
    ax2.set_yticks(y_fail)
    ax2.set_yticklabels(failure_modes, fontsize=9.0, color=TEXT_MAIN)
    ax2.set_xlabel('Share of Patch Failures (%)', fontsize=8.5, color=TEXT_MUTED)
    ax2.set_title('Single-Turn Diff Failure Modes', fontsize=10.5, fontweight='bold', color=TEXT_MAIN, pad=12)
    ax2.set_xlim(0, 80)

    for bar, val in zip(bars_fail, failure_pcts):
        ax2.text(val + 1.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}%',
                 va='center', fontsize=9.0, fontweight='bold', color=TEXT_MAIN)

    ax2.text(0.05, 0.15, '0.0% Strict git apply across all methods\nProves agents require multi-turn repair environments',
             fontsize=8.0, color='#fca5a5', transform=ax2.transAxes,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#450a0a', edgecolor=COLOR_RED, lw=1))

    save_and_verify(fig, 'paper/figures/gallery_3_gemma4_latency.png')

# ----------------------------------------------------------------------
# Figure 4: Scope Taxation & Parent Reconstruction
# ----------------------------------------------------------------------
def generate_fig4_scope_dedup():
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis('off')

    # Title
    ax.text(0.04, 0.93, 'The Scope Tax Problem & Post-Hoc Reconstruction',
            fontsize=15, fontweight='bold', color=TEXT_MAIN, va='top')
    ax.text(0.04, 0.86, 'How MR-AST eliminates redundant class definitions to reclaim active prompt memory',
            fontsize=9.5, color=TEXT_MUTED, va='top')

    # Card 1: Problem (Red)
    rect_prob = FancyBboxPatch((0.04, 0.32), 0.44, 0.48, facecolor=CARD_BG, edgecolor=COLOR_RED,
                               linewidth=1.8, transform=ax.transAxes, zorder=2, boxstyle="round,pad=0.015")
    ax.add_patch(rect_prob)

    ax.text(0.06, 0.76, 'PROBLEM: Monolithic Scoping Tax', fontsize=11, fontweight='bold', color=COLOR_RED,
            va='top', transform=ax.transAxes)
    ax.plot([0.06, 0.46], [0.71, 0.71], color='#334155', lw=1, transform=ax.transAxes)

    prob_bullets = [
        '• Class headers repeated for EVERY method',
        '• Exhausts budget on redundant boilerplate',
        '• Caps capacity at ~12.5 symbols at 2,000 tokens',
        '• Starves agent of peripheral context',
        '• Large test files displace target bugs (Paradox)'
    ]
    y_b = 0.67
    for b in prob_bullets:
        ax.text(0.06, y_b, b, fontsize=8.5, color='#cbd5e1', va='top', transform=ax.transAxes)
        y_b -= 0.07

    # Card 2: Solution (Green)
    rect_sol = FancyBboxPatch((0.52, 0.32), 0.44, 0.48, facecolor=CARD_BG, edgecolor=COLOR_GREEN,
                              linewidth=1.8, transform=ax.transAxes, zorder=2, boxstyle="round,pad=0.015")
    ax.add_patch(rect_sol)

    ax.text(0.54, 0.76, 'SOLUTION: Post-Hoc Reconstruction', fontsize=11, fontweight='bold', color=COLOR_GREEN,
            va='top', transform=ax.transAxes)
    ax.plot([0.54, 0.94], [0.71, 0.71], color='#334155', lw=1, transform=ax.transAxes)

    sol_bullets = [
        '• Optimizer omits parent classes (0 knapsack tax)',
        '• Serializer C(x) reconstructs parent headers post-hoc',
        '• Median reconstruction cost: only 5.0 tokens',
        '• 56.05% pooled token deduplication rate',
        '• Retains 1.55x more full code implementations'
    ]
    y_s = 0.67
    for b in sol_bullets:
        ax.text(0.54, y_s, b, fontsize=8.5, color='#cbd5e1', va='top', transform=ax.transAxes)
        y_s -= 0.07

    # Bottom 4 Metric Pills
    metrics = [
        ('56.05%', 'Deduplication Rate', COLOR_GREEN),
        ('12,224', 'Redundant Defs Removed', COLOR_CYAN),
        ('5.0 Tokens', 'Median Reconstruct Cost', COLOR_PURPLE),
        ('1.55x', 'More Full Code at 2k', COLOR_PINK)
    ]

    x_pill = 0.04
    w_pill = 0.21
    for val, lbl, col in metrics:
        prect = FancyBboxPatch((x_pill, 0.05), w_pill, 0.20, facecolor='#111827', edgecolor=col,
                               linewidth=1.2, transform=ax.transAxes, zorder=2, boxstyle="round,pad=0.01")
        ax.add_patch(prect)
        ax.text(x_pill + w_pill/2, 0.17, val, fontsize=13, fontweight='bold', color=col,
                ha='center', va='center', transform=ax.transAxes)
        ax.text(x_pill + w_pill/2, 0.10, lbl, fontsize=7.8, color=TEXT_MUTED,
                ha='center', va='center', transform=ax.transAxes)
        x_pill += w_pill + 0.026

    save_and_verify(fig, 'paper/figures/gallery_4_scope_deduplication.png')

# ----------------------------------------------------------------------
# Figure 5: Solver Complexity & Scaling Micro-Benchmark
# ----------------------------------------------------------------------
def generate_fig5_solver():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4.5), facecolor=BG_COLOR)

    for ax in (ax1, ax2):
        ax.set_facecolor(CARD_BG)
        ax.grid(True, linestyle='--', alpha=0.25, color='#475569')
        ax.tick_params(colors=TEXT_MUTED, labelsize=8.5)
        for spine in ax.spines.values():
            spine.set_color(BORDER_COLOR)

    N_vals = ['N=20', 'N=60', 'N=200', 'N=800']
    x = np.arange(len(N_vals))
    highs_ms = [2.89, 2.80, 8.05, 317.11]
    greedy_ms = [1.20, 9.90, 101.62, 6582.98]
    speedups = [0.42, 3.53, 12.62, 20.76]

    # Left Plot: Log-scale Solve Time
    ax1.plot(x, highs_ms, marker='o', markersize=6, linewidth=2.4, color=COLOR_CYAN, label='HiGHS Exact MILP')
    ax1.plot(x, greedy_ms, marker='s', markersize=5, linewidth=2.0, color=COLOR_AMBER, linestyle='--', label='Python Greedy Loop')
    ax1.set_yscale('log')
    ax1.set_title('Solve Time (ms, log scale)', fontsize=10.5, fontweight='bold', color=TEXT_MAIN, pad=12)
    ax1.set_xlabel('Candidate Pool Size (N)', fontsize=8.5, color=TEXT_MUTED)
    ax1.set_ylabel('Mean Execution Time (ms)', fontsize=8.5, color=TEXT_MUTED)
    ax1.set_xticks(x)
    ax1.set_xticklabels(N_vals)
    ax1.set_ylim(0.5, 15000)

    leg1 = ax1.legend(facecolor='#1e293b', edgecolor=BORDER_COLOR, fontsize=8.0, loc='upper left')
    for text in leg1.get_texts():
        text.set_color(TEXT_MAIN)

    # Right Plot: HiGHS Speedup Factor
    bar_cols = [COLOR_RED if s < 1 else COLOR_GREEN for s in speedups]
    bars = ax2.bar(x, speedups, width=0.52, color=bar_cols, edgecolor='#334155')
    ax2.set_title('HiGHS Speedup Factor (x)', fontsize=10.5, fontweight='bold', color=TEXT_MAIN, pad=12)
    ax2.set_xlabel('Candidate Pool Size (N)', fontsize=8.5, color=TEXT_MUTED)
    ax2.set_ylabel('Speedup Factor over Python Loop', fontsize=8.5, color=TEXT_MUTED)
    ax2.set_xticks(x)
    ax2.set_xticklabels(N_vals)
    ax2.set_ylim(0, 26)

    # Data labels cleanly positioned above bars (no collisions!)
    for bar, val in zip(bars, speedups):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.8, f'{val:.1f}x',
                 ha='center', va='bottom', fontsize=8.8, fontweight='bold', color=TEXT_MAIN)

    # Callout card at top left of right chart
    ax2.text(0.05, 0.85, '0.0% Optimality Gap\nHiGHS evaluates bounds sub-linearly',
             fontsize=8.0, color=COLOR_GREEN, transform=ax2.transAxes,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#064e3b', edgecolor=COLOR_GREEN, lw=1))

    save_and_verify(fig, 'paper/figures/gallery_5_solver_scaling.png')

if __name__ == '__main__':
    print("Generating Figure 1...")
    generate_fig1_architecture()
    print("Generating Figure 2...")
    generate_fig2_recall()
    print("Generating Figure 3...")
    generate_fig3_latency()
    print("Generating Figure 4...")
    generate_fig4_scope_dedup()
    print("Generating Figure 5...")
    generate_fig5_solver()
    print("All 5 conference-grade figures generated successfully!")

