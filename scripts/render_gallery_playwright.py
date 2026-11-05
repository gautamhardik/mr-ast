import os
from playwright.sync_api import sync_playwright

WORKSPACE = r"c:\Users\hiten\Downloads\GEMMA"
FIG_DIR = os.path.join(WORKSPACE, "paper", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

COMMON_HEAD = """
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            width: 1200px;
            height: 675px;
            overflow: hidden;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0B0F19;
            color: #F1F5F9;
            position: relative;
        }
        .bg-grid {
            position: absolute;
            inset: 0;
            background-image: 
                linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
        }
        .bg-glow-cyan {
            position: absolute;
            width: 450px;
            height: 450px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0, 229, 255, 0.12) 0%, transparent 70%);
            top: -150px;
            left: -100px;
            pointer-events: none;
        }
        .bg-glow-purple {
            position: absolute;
            width: 500px;
            height: 500px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, transparent 70%);
            bottom: -150px;
            right: -100px;
            pointer-events: none;
        }
        .glass-card {
            background: rgba(19, 29, 49, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        .glass-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.02em;
            white-space: nowrap;
        }
        .badge-cyan { background: rgba(0, 229, 255, 0.12); color: #00E5FF; border: 1px solid rgba(0, 229, 255, 0.3); }
        .badge-purple { background: rgba(168, 85, 247, 0.12); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.3); }
        .badge-amber { background: rgba(245, 158, 11, 0.12); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-green { background: rgba(16, 185, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-rose { background: rgba(244, 63, 94, 0.12); color: #FB7185; border: 1px solid rgba(244, 63, 94, 0.3); }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .gradient-text-cyan {
            background: linear-gradient(135deg, #FFFFFF 0%, #00E5FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
"""

# FIGURE 1: SYSTEM ARCHITECTURE
HTML_FIG1_ARCH = f"""
<!DOCTYPE html>
<html>
{COMMON_HEAD}
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow-cyan"></div>
    <div class="bg-glow-purple"></div>

    <div style="padding: 26px 40px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                    <span class="glass-pill badge-cyan">SYSTEM ARCHITECTURE</span>
                    <span style="color: #64748B; font-size: 14px;">End-to-End Budget-Constrained Context Compiler</span>
                </div>
                <h1 style="font-size: 28px; font-weight: 800; letter-spacing: -0.02em;">
                    MR-AST <span class="gradient-text-cyan">Multi-Resolution Pipeline</span> for Google Gemma 4
                </h1>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span class="glass-pill badge-purple mono">Invariant 1: ast.parse() != Error</span>
                <span class="glass-pill badge-green mono">Pure Greedy: O(N log N)</span>
            </div>
        </div>

        <!-- 4 Architecture Cards connected in pipeline -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 16px 0; position: relative;">
            <!-- Step 1 -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column; border-top: 3px solid #00E5FF;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <span class="glass-pill badge-cyan" style="padding: 3px 10px; font-size: 11px;">STAGE 1</span>
                    <span style="font-size: 22px;">🌲</span>
                </div>
                <h3 style="font-size: 17px; font-weight: 700; margin-bottom: 6px; color: #FFFFFF;">AST Forest Parse</h3>
                <p style="font-size: 12px; color: #94A3B8; line-height: 1.5; margin-bottom: 12px;">
                    Tree-sitter repository parsing extracts hierarchical syntax trees across Python modules.
                </p>
                <div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 10px; margin-top: auto; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 11px; color: #38BDF8; font-weight: 600; margin-bottom: 4px;">Hierarchical Tree</div>
                    <div class="mono" style="font-size: 11px; color: #94A3B8; line-height: 1.6;">
                        • Module [app.py]<br>
                        &nbsp;&nbsp;└─ Class [Model]<br>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ Def [forward]
                    </div>
                </div>
            </div>

            <!-- Step 2 -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column; border-top: 3px solid #A855F7;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <span class="glass-pill badge-purple" style="padding: 3px 10px; font-size: 11px;">STAGE 2</span>
                    <span style="font-size: 22px;">🧬</span>
                </div>
                <h3 style="font-size: 17px; font-weight: 700; margin-bottom: 6px; color: #FFFFFF;">4-Tier Lattice</h3>
                <p style="font-size: 12px; color: #94A3B8; line-height: 1.5; margin-bottom: 12px;">
                    Projects symbols into discrete resolutions with monotonically increasing token costs.
                </p>
                <div style="display: flex; flex-direction: column; gap: 4px; margin-top: auto;">
                    <div style="display: flex; justify-content: space-between; font-size: 11px; background: rgba(0, 229, 255, 0.1); padding: 5px 8px; border-radius: 6px; color: #00E5FF; font-weight: 600;">
                        <span>T3: Full Code</span><span>100% cost</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; background: rgba(168, 85, 247, 0.1); padding: 5px 8px; border-radius: 6px; color: #C084FC; font-weight: 600;">
                        <span>T2: Skeleton</span><span>~35% cost</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; background: rgba(245, 158, 11, 0.1); padding: 5px 8px; border-radius: 6px; color: #FBBF24; font-weight: 600;">
                        <span>T1: Stub</span><span>~12% cost</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; background: rgba(148, 163, 184, 0.08); padding: 5px 8px; border-radius: 6px; color: #94A3B8; font-weight: 600;">
                        <span>T0: Excluded</span><span>0 tokens</span>
                    </div>
                </div>
            </div>

            <!-- Step 3 -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column; border-top: 3px solid #F59E0B;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <span class="glass-pill badge-amber" style="padding: 3px 10px; font-size: 11px;">STAGE 3</span>
                    <span style="font-size: 22px;">⚡</span>
                </div>
                <h3 style="font-size: 17px; font-weight: 700; margin-bottom: 6px; color: #FFFFFF;">Pure MCKP Solver</h3>
                <p style="font-size: 12px; color: #94A3B8; line-height: 1.5; margin-bottom: 12px;">
                    Knapsack optimization maximizes utility under strict prompt budget B in [2k, 16k].
                </p>
                <div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 10px; margin-top: auto; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 11px; color: #FBBF24; font-weight: 700; margin-bottom: 4px;">Dynamic Schedule</div>
                    <div class="mono" style="font-size: 11px; color: #E2E8F0; line-height: 1.5;">
                        K_step(B) ∈ [60, 400]<br>
                        Marginal: Δu_ir / Δc_ir<br>
                        Solve Time: &lt; 0.35s
                    </div>
                </div>
            </div>

            <!-- Step 4 -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column; border-top: 3px solid #10B981;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <span class="glass-pill badge-green" style="padding: 3px 10px; font-size: 11px;">STAGE 4</span>
                    <span style="font-size: 22px;">🛡️</span>
                </div>
                <h3 style="font-size: 17px; font-weight: 700; margin-bottom: 6px; color: #FFFFFF;">Valid Serializer</h3>
                <p style="font-size: 12px; color: #94A3B8; line-height: 1.5; margin-bottom: 12px;">
                    Enforces Invariant 1 via post-hoc parent reconstruction with zero duplicate class headers.
                </p>
                <div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 10px; margin-top: auto; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="font-size: 11px; color: #34D399; font-weight: 700; margin-bottom: 4px;">Audit Guarantee</div>
                    <div class="mono" style="font-size: 11px; color: #E2E8F0; line-height: 1.5;">
                        0% Syntax Errors<br>
                        56.05% Deduplication<br>
                        1.55x Retained Code
                    </div>
                </div>
            </div>
        </div>

        <!-- Downstream Banner -->
        <div class="glass-card" style="padding: 14px 24px; display: flex; align-items: center; justify-content: space-between; background: linear-gradient(90deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(0, 229, 255, 0.25);">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: rgba(0, 229, 255, 0.15); display: flex; align-items: center; justify-content: center; font-size: 20px;">🤖</div>
                <div>
                    <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Downstream Consumer: Google Gemma 4 31B Developer Agent</div>
                    <div style="font-size: 12px; color: #94A3B8;">Evaluated via Vertex AI API on real-world multi-file SWE-bench tasks</div>
                </div>
            </div>
            <div style="display: flex; gap: 14px;">
                <span class="glass-pill badge-cyan" style="font-size: 12px;">⚡ -28.3% Generation Latency (p=0.038)</span>
                <span class="glass-pill badge-green" style="font-size: 12px;">✅ 100% Parsing Pass Rate</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

# FIGURE 2: RECALL BENCHMARK & CROSS-VALIDATION
HTML_FIG2_BENCHMARK = f"""
<!DOCTYPE html>
<html>
{COMMON_HEAD}
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow-cyan"></div>
    <div class="bg-glow-purple"></div>

    <div style="padding: 24px 40px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                    <span class="glass-pill badge-cyan">EMPIRICAL BENCHMARKS</span>
                    <span style="color: #64748B; font-size: 13px;">Factorial Evaluation over 5,160 Runs</span>
                </div>
                <h1 style="font-size: 26px; font-weight: 800;">
                    Gold Symbol Recall & <span class="gradient-text-cyan">Zero-Leakage Cross-Validation</span>
                </h1>
            </div>
            <!-- KPI Badges -->
            <div style="display: flex; gap: 12px;">
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #00E5FF; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #00E5FF;">+16.44 pp</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">Recall Advantage (p=0.004)</div>
                </div>
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #10B981; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #34D399;">76.9% vs 76.5%</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">2-Fold Out-of-Fold Parity</div>
                </div>
            </div>
        </div>

        <!-- 2 Side-by-Side Visual Charts -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 500px; margin-top: 12px;">
            <!-- Chart 1: Gold Recall Across Budgets -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Gold Recall Across Budgets (66-Task Split)</div>
                        <div style="font-size: 11px; color: #94A3B8;">Higher is better • Statistically audited on held-out tasks</div>
                    </div>
                    <span class="glass-pill badge-cyan mono" style="font-size: 11px;">B ∈ [2k, 16k]</span>
                </div>

                <!-- SVG Plot 1 -->
                <div style="flex: 1; position: relative;">
                    <svg viewBox="0 0 500 320" style="width: 100%; height: 100%;">
                        <!-- Grid lines (40% to 80%) -->
                        <line x1="50" y1="40" x2="480" y2="40" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="95" x2="480" y2="95" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="150" x2="480" y2="150" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="205" x2="480" y2="205" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="260" x2="480" y2="260" stroke="rgba(255,255,255,0.15)" />

                        <!-- Y-Labels -->
                        <text x="38" y="44" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">80%</text>
                        <text x="38" y="99" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">70%</text>
                        <text x="38" y="154" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">60%</text>
                        <text x="38" y="209" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">50%</text>
                        <text x="38" y="264" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">40%</text>

                        <!-- X-Labels -->
                        <text x="80" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">2k</text>
                        <text x="200" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">4k</text>
                        <text x="320" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">8k</text>
                        <text x="440" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">16k</text>

                        <!-- Static K=60 (Pink dotted) -->
                        <polyline fill="none" stroke="#F43F5E" stroke-width="2.5" stroke-dasharray="5 3"
                            points="80,206 200,173 320,173 440,172" />
                        
                        <!-- Aider RepoMap (Purple dash) -->
                        <polyline fill="none" stroke="#C084FC" stroke-width="2.5" stroke-dasharray="6 4"
                            points="80,265 200,195 320,188 440,136" />

                        <!-- Scoped BM25 (Amber dash) -->
                        <polyline fill="none" stroke="#FBBF24" stroke-width="2.5" stroke-dasharray="6 4"
                            points="80,252 200,234 320,159 440,147" />

                        <!-- MR-AST Dynamic (Cyan bold glow) -->
                        <defs>
                            <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stop-color="#00E5FF" stop-opacity="0.3"/>
                                <stop offset="100%" stop-color="#00E5FF" stop-opacity="0.0"/>
                            </linearGradient>
                        </defs>
                        <polygon fill="url(#cyanGrad)" points="80,206 200,124 320,87 440,57 440,260 80,260" />
                        <polyline fill="none" stroke="#00E5FF" stroke-width="4"
                            points="80,206 200,124 320,87 440,57" />

                        <!-- Points & Labels -->
                        <circle cx="80" cy="206" r="5" fill="#00E5FF" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="200" cy="124" r="5" fill="#00E5FF" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="320" cy="87" r="5" fill="#00E5FF" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="440" cy="57" r="6" fill="#00E5FF" stroke="#FFFFFF" stroke-width="2" />
                        <text x="440" y="42" fill="#00E5FF" font-size="13" font-weight="bold" text-anchor="middle" font-family="JetBrains Mono">76.92%</text>

                        <!-- Advantage Pill Annotation (placed with plenty of room above line) -->
                        <rect x="180" y="24" width="180" height="28" rx="14" fill="rgba(0, 229, 255, 0.18)" stroke="#00E5FF" stroke-width="1.5"/>
                        <text x="270" y="43" fill="#00E5FF" font-size="11" font-weight="bold" text-anchor="middle">+16.44 pp (p=0.0043)</text>
                    </svg>
                </div>

                <!-- Legend -->
                <div style="display: flex; justify-content: center; gap: 16px; margin-top: 4px; font-size: 11px;">
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#00E5FF; border-radius:2px;"></span><span style="color:#FFFFFF; font-weight:700;">MR-AST (Dynamic)</span></div>
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#FBBF24; border-radius:2px;"></span><span style="color:#94A3B8;">Scoped BM25</span></div>
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#C084FC; border-radius:2px;"></span><span style="color:#94A3B8;">Aider RepoMap</span></div>
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#F43F5E; border-radius:2px;"></span><span style="color:#94A3B8;">Static K=60</span></div>
                </div>
            </div>

            <!-- Chart 2: 2-Fold Cross-Validation -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Zero-Leakage 2-Fold Cross-Validation</div>
                        <div style="font-size: 11px; color: #94A3B8;">Out-of-Fold generalization parity across independent task splits</div>
                    </div>
                    <span class="glass-pill badge-green mono" style="font-size: 11px;">Zero Data Leakage</span>
                </div>

                <!-- SVG Plot 2 -->
                <div style="flex: 1; position: relative;">
                    <svg viewBox="0 0 500 320" style="width: 100%; height: 100%;">
                        <!-- Grid lines -->
                        <line x1="50" y1="40" x2="480" y2="40" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="95" x2="480" y2="95" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="150" x2="480" y2="150" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="205" x2="480" y2="205" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="260" x2="480" y2="260" stroke="rgba(255,255,255,0.15)" />

                        <!-- Y-Labels -->
                        <text x="38" y="44" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">80%</text>
                        <text x="38" y="99" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">70%</text>
                        <text x="38" y="154" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">60%</text>
                        <text x="38" y="209" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">50%</text>
                        <text x="38" y="264" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">40%</text>

                        <!-- X-Labels -->
                        <text x="80" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">2k</text>
                        <text x="200" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">4k</text>
                        <text x="320" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">8k</text>
                        <text x="440" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">16k</text>

                        <!-- Fold 1 Out-of-fold Test (Emerald bold) -->
                        <polyline fill="none" stroke="#10B981" stroke-width="3.5"
                            points="80,219 200,108 320,76 440,57" />
                        <circle cx="80" cy="219" r="5" fill="#10B981" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="200" cy="108" r="5" fill="#10B981" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="320" cy="76" r="5" fill="#10B981" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="440" cy="57" r="6" fill="#10B981" stroke="#FFFFFF" stroke-width="2" />

                        <!-- Fold 2 Out-of-fold Test (Fuchsia dash) -->
                        <polyline fill="none" stroke="#F43F5E" stroke-width="3.5" stroke-dasharray="6 4"
                            points="80,226 200,137 320,86 440,59" />
                        <polygon points="80,226 75,233 85,233" fill="#F43F5E" />
                        <polygon points="200,137 195,144 205,144" fill="#F43F5E" />
                        <polygon points="320,86 315,93 325,93" fill="#F43F5E" />
                        <polygon points="440,59 435,66 445,66" fill="#F43F5E" />

                        <!-- Parity Callout (lower right quadrant, completely clear of curves) -->
                        <rect x="210" y="175" width="240" height="42" rx="10" fill="rgba(15, 23, 42, 0.9)" stroke="rgba(16, 185, 129, 0.4)" stroke-width="1.5"/>
                        <text x="330" y="193" fill="#34D399" font-size="12" font-weight="bold" text-anchor="middle">Out-of-Fold Parity at 16k</text>
                        <text x="330" y="210" fill="#FFFFFF" font-size="11" text-anchor="middle" font-family="JetBrains Mono">76.92% (Fold 1) vs 76.47% (Fold 2)</text>
                    </svg>
                </div>

                <!-- Legend -->
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 4px; font-size: 11px;">
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#10B981; border-radius:2px;"></span><span style="color:#FFFFFF; font-weight:700;">Fold 1 Heldout Test (66 tasks)</span></div>
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#F43F5E; border-radius:2px;"></span><span style="color:#FFFFFF; font-weight:700;">Fold 2 Dev Test (63 tasks)</span></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# FIGURE 3: GEMMA 4 LATENCY & PATCH TAXONOMY
HTML_FIG3_LATENCY = f"""
<!DOCTYPE html>
<html>
{COMMON_HEAD}
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow-cyan"></div>
    <div class="bg-glow-purple"></div>

    <div style="padding: 24px 40px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                    <span class="glass-pill badge-cyan">DOWNSTREAM IMPACT</span>
                    <span style="color: #64748B; font-size: 13px;">Google Gemma 4 31B Vertex AI Inference Pilot</span>
                </div>
                <h1 style="font-size: 26px; font-weight: 800;">
                    Downstream Latency & <span class="gradient-text-cyan">Single-Turn Patch Failure Taxonomy</span>
                </h1>
            </div>
            <div style="display: flex; gap: 12px;">
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #00E5FF; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #00E5FF;">-28.3%</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">Prompt Latency (p=0.038)</div>
                </div>
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #F59E0B; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #FBBF24;">1.55x Retained</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">Full Code at B=2k</div>
                </div>
            </div>
        </div>

        <!-- 2 Side-by-Side Visual Cards -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 500px; margin-top: 12px;">
            <!-- Left: Latency Comparison Bar Chart -->
            <div class="glass-card" style="padding: 22px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Gemma 4 31B Generation Latency (s)</div>
                        <div style="font-size: 11px; color: #94A3B8;">Evaluated at tight budget B = 2,000 tokens (seconds per inference)</div>
                    </div>
                    <span class="glass-pill badge-cyan mono" style="font-size: 11px;">Lower is better</span>
                </div>

                <!-- Horizontal Bars with ample room and zero overlap -->
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; padding: 10px 0;">
                    <!-- Baseline 1 -->
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
                            <span style="color: #94A3B8; font-weight: 600;">Raw BM25 Baseline</span>
                            <span class="mono" style="color: #FFFFFF; font-weight: 700;">10.22s ± 0.85s</span>
                        </div>
                        <div style="height: 38px; background: rgba(148, 163, 184, 0.1); border-radius: 8px; overflow: hidden; position: relative;">
                            <div style="width: 82%; height: 100%; background: linear-gradient(90deg, #475569 0%, #64748B 100%); border-radius: 8px;"></div>
                        </div>
                    </div>

                    <!-- Baseline 2 -->
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
                            <span style="color: #FBBF24; font-weight: 600;">Scoped BM25 (Monolithic)</span>
                            <span class="mono" style="color: #FFFFFF; font-weight: 700;">10.55s ± 0.92s</span>
                        </div>
                        <div style="height: 38px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; overflow: hidden; position: relative;">
                            <div style="width: 85%; height: 100%; background: linear-gradient(90deg, #D97706 0%, #F59E0B 100%); border-radius: 8px;"></div>
                        </div>
                    </div>

                    <!-- MR-AST -->
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
                            <span style="color: #00E5FF; font-weight: 700;">MR-AST (Multi-Resolution)</span>
                            <span class="mono" style="color: #00E5FF; font-weight: 800;">7.57s ± 0.65s</span>
                        </div>
                        <div style="height: 38px; background: rgba(0, 229, 255, 0.1); border-radius: 8px; overflow: hidden; position: relative; border: 1px solid rgba(0, 229, 255, 0.3);">
                            <div style="width: 61%; height: 100%; background: linear-gradient(90deg, #0284C7 0%, #00E5FF 100%); border-radius: 8px;"></div>
                        </div>
                    </div>

                    <!-- Callout Box -->
                    <div style="background: rgba(0, 229, 255, 0.08); border: 1px solid rgba(0, 229, 255, 0.25); border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 13px; color: #E2E8F0; font-weight: 600;">Statistically Significant Latency Reduction</span>
                        <span class="glass-pill badge-cyan mono" style="font-size: 12px; font-weight: 800;">-2.98s (-28.3%, p=0.038)</span>
                    </div>
                </div>
            </div>

            <!-- Right: Failure Taxonomy Donut -->
            <div class="glass-card" style="padding: 22px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Single-Turn Diff Failure Taxonomy</div>
                        <div style="font-size: 11px; color: #94A3B8;">0% git apply pass rate across all zero-shot patching attempts</div>
                    </div>
                    <span class="glass-pill badge-rose mono" style="font-size: 11px;">0% git apply</span>
                </div>

                <!-- SVG Donut Chart + Pills -->
                <div style="flex: 1; display: flex; align-items: center; justify-content: space-between; gap: 20px;">
                    <div style="width: 190px; height: 190px; position: relative;">
                        <svg viewBox="0 0 200 200" style="width: 100%; height: 100%; transform: rotate(-90deg);">
                            <!-- Total perimeter = 2 * pi * 70 ≈ 440 -->
                            <!-- Line drift 61.1% = 269 -->
                            <circle cx="100" cy="100" r="70" fill="none" stroke="#F43F5E" stroke-width="26"
                                stroke-dasharray="269 440" stroke-dashoffset="0" />
                            <!-- Indentation 22.2% = 98 -->
                            <circle cx="100" cy="100" r="70" fill="none" stroke="#F59E0B" stroke-width="26"
                                stroke-dasharray="98 440" stroke-dashoffset="-269" />
                            <!-- Missing hunk 16.7% = 73 -->
                            <circle cx="100" cy="100" r="70" fill="none" stroke="#38BDF8" stroke-width="26"
                                stroke-dasharray="73 440" stroke-dashoffset="-367" />
                        </svg>
                        <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                            <div style="font-size: 22px; font-weight: 800; color: #FFFFFF;">0%</div>
                            <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase;">Apply Pass</div>
                        </div>
                    </div>

                    <!-- Breakdown Legend -->
                    <div style="flex: 1; display: flex; flex-direction: column; gap: 8px;">
                        <div style="background: rgba(244, 63, 94, 0.1); border-left: 3px solid #F43F5E; padding: 7px 10px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #FB7185;">
                                <span>Line Drift</span><span>61.1%</span>
                            </div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 1px;">Truncated scope shifts line indices</div>
                        </div>

                        <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #F59E0B; padding: 7px 10px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #FBBF24;">
                                <span>Indentation Mismatch</span><span>22.2%</span>
                            </div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 1px;">Extracted blocks lose enclosing indents</div>
                        </div>

                        <div style="background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38BDF8; padding: 7px 10px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #38BDF8;">
                                <span>Missing Hunk Headers</span><span>16.7%</span>
                            </div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 1px;">Incomplete unified diff headers</div>
                        </div>
                    </div>
                </div>

                <div style="background: rgba(15, 23, 42, 0.7); border-radius: 8px; padding: 8px 12px; margin-top: 6px; font-size: 11px; color: #94A3B8; line-height: 1.4;">
                    <strong style="color: #E2E8F0;">Paper Thesis §6:</strong> Developer agents strictly require interactive multi-turn search/replace editing rather than zero-shot monolithic diffs.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# FIGURE 4: SCOPE TAXATION & DEDUPLICATION
HTML_FIG4_SCOPE = f"""
<!DOCTYPE html>
<html>
{COMMON_HEAD}
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow-cyan"></div>
    <div class="bg-glow-purple"></div>

    <div style="padding: 24px 40px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                    <span class="glass-pill badge-purple">ARCHITECTURAL DISCOVERY</span>
                    <span style="color: #64748B; font-size: 13px;">Eliminating Redundant Structural Taxation</span>
                </div>
                <h1 style="font-size: 26px; font-weight: 800;">
                    Scope Taxation vs <span class="gradient-text-cyan">Post-Hoc Parent Reconstruction</span>
                </h1>
            </div>
            <div style="display: flex; gap: 12px;">
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #00E5FF; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #00E5FF;">56.05%</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">Deduplication Rate</div>
                </div>
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #10B981; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #34D399;">5.0 tokens</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">Median Reconstruction Cost</div>
                </div>
            </div>
        </div>

        <!-- Before vs After Visual Comparison -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 500px; margin-top: 12px;">
            <!-- Left: Problem (Monolithic Scoping) -->
            <div class="glass-card" style="padding: 22px; display: flex; flex-direction: column; border-top: 3px solid #F43F5E;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FB7185;">Problem: Monolithic Scoping Tax</div>
                        <div style="font-size: 11px; color: #94A3B8;">Standard baselines (BM25 scoped) exhaust token budget</div>
                    </div>
                    <span class="glass-pill badge-rose" style="font-size: 11px;">Budget Bleed</span>
                </div>

                <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
                    <!-- Code Illustration 1 -->
                    <div style="background: rgba(15, 23, 42, 0.85); border-radius: 8px; padding: 10px 12px; border: 1px solid rgba(244, 63, 94, 0.2); font-size: 11px;" class="mono">
                        <div style="color: #FB7185;"># Candidate 1: class NeuralCompiler (280 tokens)</div>
                        <div style="color: #64748B;">class NeuralCompiler(BaseCompiler):</div>
                        <div style="color: #94A3B8; padding-left: 14px;">def method_a(self): ...</div>
                        <div style="margin-top: 6px; color: #FB7185;"># Candidate 2: Repeated Full Class Header (280 tokens!)</div>
                        <div style="color: #64748B;">class NeuralCompiler(BaseCompiler):</div>
                        <div style="color: #94A3B8; padding-left: 14px;">def method_b(self): ...</div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                        <div style="display: flex; gap: 10px; align-items: flex-start;">
                            <span style="color: #FB7185; font-size: 14px;">❌</span>
                            <span style="color: #CBD5E1;">Redundant class headers repeated for every selected method</span>
                        </div>
                        <div style="display: flex; gap: 10px; align-items: flex-start;">
                            <span style="color: #FB7185; font-size: 14px;">❌</span>
                            <span style="color: #CBD5E1;">Caps retention at only ~12.5 symbols at B = 2,000 tokens</span>
                        </div>
                        <div style="display: flex; gap: 10px; align-items: flex-start;">
                            <span style="color: #FB7185; font-size: 14px;">❌</span>
                            <span style="color: #CBD5E1;">Full-file displacement causes localization paradox</span>
                        </div>
                    </div>
                </div>

                <div style="background: rgba(244, 63, 94, 0.1); border-radius: 8px; padding: 10px 14px; margin-top: auto;">
                    <div style="font-size: 12px; color: #FB7185; font-weight: 700;">12,224 Redundant Definitions Audited</div>
                    <div style="font-size: 11px; color: #94A3B8;">Across 493 reconstructed method runs in standard benchmark</div>
                </div>
            </div>

            <!-- Right: Solution (MR-AST Post-Hoc) -->
            <div class="glass-card" style="padding: 22px; display: flex; flex-direction: column; border-top: 3px solid #10B981;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #34D399;">Solution: Post-Hoc Reconstruction</div>
                        <div style="font-size: 11px; color: #94A3B8;">MR-AST separates knapsack optimization from serialization</div>
                    </div>
                    <span class="glass-pill badge-green" style="font-size: 11px;">Zero Waste</span>
                </div>

                <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
                    <!-- Code Illustration 2 -->
                    <div style="background: rgba(15, 23, 42, 0.85); border-radius: 8px; padding: 10px 12px; border: 1px solid rgba(16, 185, 129, 0.2); font-size: 11px;" class="mono">
                        <div style="color: #34D399;"># Optimizer selects methods independently (0 tax)</div>
                        <div style="color: #38BDF8;"># Serializer C(x) reconstructs parent tree once:</div>
                        <div style="color: #E2E8F0;">class NeuralCompiler(BaseCompiler):</div>
                        <div style="color: #00E5FF; padding-left: 14px;">def method_a(self): ... [Selected]</div>
                        <div style="color: #00E5FF; padding-left: 14px;">def method_b(self): ... [Selected]</div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                        <div style="display: flex; gap: 10px; align-items: flex-start;">
                            <span style="color: #34D399; font-size: 14px;">✅</span>
                            <span style="color: #CBD5E1;">Optimizer omits parent classes during item valuation</span>
                        </div>
                        <div style="display: flex; gap: 10px; align-items: flex-start;">
                            <span style="color: #34D399; font-size: 14px;">✅</span>
                            <span style="color: #CBD5E1;">Serializer reconstructs single shared header post-hoc</span>
                        </div>
                        <div style="display: flex; gap: 10px; align-items: flex-start;">
                            <span style="color: #34D399; font-size: 14px;">✅</span>
                            <span style="color: #CBD5E1;">Retains 1.55x more full code implementations at B=2k</span>
                        </div>
                    </div>
                </div>

                <div style="background: rgba(16, 185, 129, 0.1); border-radius: 8px; padding: 10px 14px; margin-top: auto;">
                    <div style="font-size: 12px; color: #34D399; font-weight: 700;">56.05% Pooled Token Savings</div>
                    <div style="font-size: 11px; color: #94A3B8;">Median parent reconstruction cost: only 5.0 tokens per class</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# FIGURE 5: SOLVER SCALING & SPEEDUP
HTML_FIG5_SOLVER = f"""
<!DOCTYPE html>
<html>
{COMMON_HEAD}
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow-cyan"></div>
    <div class="bg-glow-purple"></div>

    <div style="padding: 24px 40px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                    <span class="glass-pill badge-green">COMPUTATIONAL EFFICIENCY</span>
                    <span style="color: #64748B; font-size: 13px;">HiGHS Exact MILP vs Python Greedy Micro-Benchmark</span>
                </div>
                <h1 style="font-size: 26px; font-weight: 800;">
                    Solver Scalability & <span class="gradient-text-cyan">Speedup Micro-Benchmark</span>
                </h1>
            </div>
            <div style="display: flex; gap: 12px;">
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #10B981; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #34D399;">20.8x Speedup</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">HiGHS at N = 800</div>
                </div>
                <div class="glass-card" style="padding: 8px 16px; border-left: 3px solid #00E5FF; text-align: right;">
                    <div style="font-size: 18px; font-weight: 800; color: #00E5FF;">0.0% Gap</div>
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">Zero Optimality Loss</div>
                </div>
            </div>
        </div>

        <!-- 2 Side-by-Side Visual Charts -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 500px; margin-top: 12px;">
            <!-- Left: Latency Curves -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">Solver Execution Latency (ms, log scale)</div>
                        <div style="font-size: 11px; color: #94A3B8;">Across candidate pool sizes N ∈ [20, 800]</div>
                    </div>
                    <span class="glass-pill badge-cyan mono" style="font-size: 11px;">Log10 ms</span>
                </div>

                <div style="flex: 1; position: relative;">
                    <svg viewBox="0 0 500 320" style="width: 100%; height: 100%;">
                        <!-- Grid lines -->
                        <line x1="50" y1="50" x2="480" y2="50" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="120" x2="480" y2="120" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="190" x2="480" y2="190" stroke="rgba(255,255,255,0.07)" stroke-dasharray="4" />
                        <line x1="50" y1="260" x2="480" y2="260" stroke="rgba(255,255,255,0.15)" />

                        <!-- Y-Labels -->
                        <text x="38" y="55" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">10⁴ ms</text>
                        <text x="38" y="125" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">10³ ms</text>
                        <text x="38" y="195" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">10² ms</text>
                        <text x="38" y="265" fill="#64748B" font-size="11" text-anchor="end" font-family="JetBrains Mono">10¹ ms</text>

                        <!-- X-Labels -->
                        <text x="80" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">N=20</text>
                        <text x="200" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">N=60</text>
                        <text x="320" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">N=200</text>
                        <text x="440" y="285" fill="#94A3B8" font-size="12" text-anchor="middle" font-family="JetBrains Mono">N=800</text>

                        <!-- Python Greedy Loop (Amber dash, spikes at N=800) -->
                        <polyline fill="none" stroke="#F59E0B" stroke-width="3" stroke-dasharray="6 4"
                            points="80,270 200,240 320,180 440,70" />
                        <rect x="76" y="266" width="8" height="8" fill="#F59E0B" />
                        <rect x="196" y="236" width="8" height="8" fill="#F59E0B" />
                        <rect x="316" y="176" width="8" height="8" fill="#F59E0B" />
                        <rect x="436" y="66" width="8" height="8" fill="#F59E0B" />
                        <text x="440" y="55" fill="#F59E0B" font-size="12" font-weight="bold" text-anchor="middle" font-family="JetBrains Mono">6,430 ms</text>

                        <!-- HiGHS Exact MILP (Cyan bold) -->
                        <polyline fill="none" stroke="#00E5FF" stroke-width="3.5"
                            points="80,260 200,260 320,245 440,165" />
                        <circle cx="80" cy="260" r="5" fill="#00E5FF" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="200" cy="260" r="5" fill="#00E5FF" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="320" cy="245" r="5" fill="#00E5FF" stroke="#0B0F19" stroke-width="2" />
                        <circle cx="440" cy="165" r="6" fill="#00E5FF" stroke="#FFFFFF" stroke-width="2" />
                        <text x="440" y="152" fill="#00E5FF" font-size="12" font-weight="bold" text-anchor="middle" font-family="JetBrains Mono">309 ms</text>
                    </svg>
                </div>

                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 4px; font-size: 11px;">
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#00E5FF; border-radius:2px;"></span><span style="color:#FFFFFF; font-weight:700;">HiGHS Exact MILP (C++)</span></div>
                    <div style="display: flex; align-items: center; gap: 6px;"><span style="width:12px; height:3px; background:#F59E0B; border-radius:2px;"></span><span style="color:#94A3B8;">Python Greedy Loop</span></div>
                </div>
            </div>

            <!-- Right: Speedup Bars -->
            <div class="glass-card" style="padding: 20px; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">HiGHS Speedup Factor (x)</div>
                        <div style="font-size: 11px; color: #94A3B8;">Linear speedup scaling as candidate pool expands</div>
                    </div>
                    <span class="glass-pill badge-green mono" style="font-size: 11px;">20.8x Max</span>
                </div>

                <div style="flex: 1; display: flex; align-items: flex-end; justify-content: space-around; padding: 20px 20px 35px 20px; border-bottom: 1px solid rgba(255,255,255,0.15);">
                    <!-- Bar 1: N=20 -->
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
                        <span class="mono" style="font-size: 12px; font-weight: 700; color: #FB7185;">0.4x</span>
                        <div style="width: 55px; height: 15px; background: linear-gradient(180deg, #F43F5E 0%, #991B1B 100%); border-radius: 6px 6px 0 0;"></div>
                        <span class="mono" style="font-size: 11px; color: #94A3B8; margin-top: 6px;">N=20</span>
                    </div>

                    <!-- Bar 2: N=60 -->
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
                        <span class="mono" style="font-size: 12px; font-weight: 700; color: #34D399;">3.5x</span>
                        <div style="width: 55px; height: 50px; background: linear-gradient(180deg, #10B981 0%, #065F46 100%); border-radius: 6px 6px 0 0;"></div>
                        <span class="mono" style="font-size: 11px; color: #94A3B8; margin-top: 6px;">N=60</span>
                    </div>

                    <!-- Bar 3: N=200 -->
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
                        <span class="mono" style="font-size: 13px; font-weight: 800; color: #34D399;">12.6x</span>
                        <div style="width: 55px; height: 130px; background: linear-gradient(180deg, #10B981 0%, #065F46 100%); border-radius: 6px 6px 0 0;"></div>
                        <span class="mono" style="font-size: 11px; color: #94A3B8; margin-top: 6px;">N=200</span>
                    </div>

                    <!-- Bar 4: N=800 -->
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
                        <span class="mono" style="font-size: 15px; font-weight: 800; color: #00E5FF;">20.8x</span>
                        <div style="width: 55px; height: 210px; background: linear-gradient(180deg, #00E5FF 0%, #0284C7 100%); border-radius: 6px 6px 0 0; box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);"></div>
                        <span class="mono" style="font-size: 11px; color: #00E5FF; font-weight: 700; margin-top: 6px;">N=800</span>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; font-size: 11px; color: #94A3B8;">
                    <span>Small pools: Python loop has lower startup overhead</span>
                    <span style="color: #34D399; font-weight: 600;">Large pools: C++ solver dominates</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def render_five():
    print("Launching Playwright to render the 5 gallery images...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        pages_to_render = [
            ("gallery_1_architecture.png", HTML_FIG1_ARCH),
            ("gallery_2_recall_benchmark.png", HTML_FIG2_BENCHMARK),
            ("gallery_3_gemma4_latency.png", HTML_FIG3_LATENCY),
            ("gallery_4_scope_deduplication.png", HTML_FIG4_SCOPE),
            ("gallery_5_solver_scaling.png", HTML_FIG5_SOLVER),
        ]
        
        fig_page = browser.new_page(viewport={"width": 1200, "height": 675}, device_scale_factor=1.5)
        for fname, html_content in pages_to_render:
            fig_page.set_content(html_content)
            fig_page.wait_for_timeout(350)
            out_path = os.path.join(FIG_DIR, fname)
            fig_page.screenshot(path=out_path)
            print(f"Rendered: {fname} ({os.path.getsize(out_path)} bytes)")

        browser.close()
    print("ALL 5 GALLERY IMAGES RENDERED SUCCESSFULLY!")

if __name__ == "__main__":
    render_five()
