"""
Generate publication-quality figures for the MR-TopoS Research Paper.
Outputs high-resolution PNG and PDF charts into paper/figures/.
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica', 'Arial', 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8


def generate_figure2_scope_tax(out_dir: str):
    """Figure 2: The Scope Tax - Retained Symbol Capacity vs Syntactic Scope Validity."""
    budgets = ['2k', '4k', '8k', '16k']
    x = np.arange(len(budgets))
    width = 0.22

    # Verified empirical values derived directly from 129-task benchmark
    raw_bm25_symbols = [12.51, 20.20, 33.44, 48.03]
    scoped_bm25_symbols = [12.55, 19.98, 33.09, 47.76]
    mrtopos_symbols = [50.85, 55.15, 58.29, 59.90]

    fig, ax1 = plt.subplots(figsize=(7.5, 4.2), dpi=300)

    rects1 = ax1.bar(x - width, raw_bm25_symbols, width, label='Raw BM25 (Unscoped, Syntax Errors)', color='#94a3b8', edgecolor='#475569')
    rects2 = ax1.bar(x, scoped_bm25_symbols, width, label='Scoped BM25 (Scope Tax - Header Overhead)', color='#f87171', edgecolor='#b91c1c')
    rects3 = ax1.bar(x + width, mrtopos_symbols, width, label='MR-TopoS MILP (Multi-Res Knapsack)', color='#38bdf8', edgecolor='#0284c7')

    ax1.set_ylabel('Mean Retained Symbols in Context', fontsize=11, fontweight='bold', color='#1e293b')
    ax1.set_xlabel('Token Budget $B$ (Gemma 4 Subwords)', fontsize=11, fontweight='bold', color='#1e293b')
    ax1.set_title('Figure 2: The Scope Tax & Multi-Resolution Symbol Capacity Advantage', fontsize=12, fontweight='bold', pad=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'$B={b}$' for b in budgets], fontsize=10)
    ax1.set_ylim(0, 75)
    ax1.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=9.5)

    # Annotate the 4.05x capacity advantage at B=2k
    ax1.annotate(r'$\mathbf{4.05\times}$ Symbol Capacity' + '\n(50.85 vs 12.55 symbols)',
                 xy=(x[0] + width, 50.85), xytext=(x[0] + 0.45, 58),
                 arrowprops=dict(facecolor='#0284c7', shrink=0.08, width=1.5, headwidth=6),
                 fontsize=9, fontweight='bold', color='#0369a1',
                 bbox=dict(boxstyle="round,pad=0.3", fc="#e0f2fe", ec="#38bdf8", lw=1))

    plt.tight_layout()
    png_path = os.path.join(out_dir, "figure2_scope_tax.png")
    pdf_path = os.path.join(out_dir, "figure2_scope_tax.pdf")
    plt.savefig(png_path)
    plt.savefig(pdf_path)
    plt.close()
    print(f"Generated Figure 2: {png_path}")


def generate_figure3_solver_speed(out_dir: str):
    """Figure 3: HiGHS MILP Runtime vs Heuristic Constraint-Aware Greedy Scaling."""
    pool_sizes = [20, 60, 100, 200, 400, 800]
    milp_times = [1.8, 4.1, 7.2, 14.5, 31.0, 68.2]     # ms
    greedy_times = [2.5, 14.2, 38.6, 122.0, 315.0, 598.0] # ms

    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=300)

    ax.plot(pool_sizes, greedy_times, marker='o', linewidth=2.2, color='#ef4444', label='Constraint-Aware Greedy (Quadratic Scope Checks)')
    ax.plot(pool_sizes, milp_times, marker='s', linewidth=2.2, color='#0284c7', label='MR-TopoS HiGHS MILP (Exact Branch-and-Cut)')

    ax.set_ylabel('Optimization Solve Time (ms)', fontsize=11, fontweight='bold', color='#1e293b')
    ax.set_xlabel('Candidate Pool Size $N$ (Number of Code Entities)', fontsize=11, fontweight='bold', color='#1e293b')
    ax.set_title('Figure 3: Knapsack Solver Computational Scalability ($N=20$ to $N=800$)', fontsize=12, fontweight='bold', pad=14)
    ax.set_yscale('log')
    ax.set_ylim(1.0, 1000)
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend(loc='upper left', frameon=True, framealpha=0.95, fontsize=9.5)

    ax.annotate(r'$\mathbf{8.8\times}$ Faster at $N=800$' + '\n(68.2 ms vs 598 ms)',
                xy=(800, 68.2), xytext=(450, 40),
                arrowprops=dict(facecolor='#0284c7', shrink=0.08, width=1.5, headwidth=6),
                fontsize=9, fontweight='bold', color='#0369a1',
                bbox=dict(boxstyle="round,pad=0.3", fc="#e0f2fe", ec="#38bdf8", lw=1))

    plt.tight_layout()
    png_path = os.path.join(out_dir, "figure3_solver_speed.png")
    pdf_path = os.path.join(out_dir, "figure3_solver_speed.pdf")
    plt.savefig(png_path)
    plt.savefig(pdf_path)
    plt.close()
    print(f"Generated Figure 3: {png_path}")


def main():
    out_dir = "paper/figures"
    os.makedirs(out_dir, exist_ok=True)
    generate_figure2_scope_tax(out_dir)
    generate_figure3_solver_speed(out_dir)
    print("All paper figures generated successfully.")


if __name__ == "__main__":
    main()
