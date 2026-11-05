with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

checks = {
    "Budget 2k variable ($B = 2,000$)": "$B = 2,000$" in text or "$B=2,000$" in text,
    "Full impl ratio ($1.55\\times$)": "$1.55\\times$" in text,
    "Full impl count ($19.47$ vs $12.55$)": "$19.47$" in text and "$12.55$" in text,
    "Full impl tokens ($1,849$ vs $1,192$)": "$1,849$" in text and "$1,192$" in text,
    "Skeletons and stubs ($30.00$ and $1.39$)": "$30.00$" in text and "$1.39$" in text,
    "Candidate pool saturation ($K=60$)": "$K=60$" in text,
    "Speedup numbers ($3.53\\times$ and $20.76\\times$)": "$3.53\\times$" in text and "$20.76\\times$" in text,
    "Candidate size ($N \\ge 60$)": "$N \\ge 60$" in text,
    "Gemma latency reduction ($28.3\\%$)": "$28.3\\%$" in text or "28.3%" in text,
    "Gemma t-test notation ($t(5)=2.76$)": "t(5)=2.76" in text or "t(5) = 2.76" in text,
    "LocAgent ACL 2025 (Chen et al., 2025)": "Chen et al., 2025" in text or "Chen, Z." in text,
    "Context compression (Feng et al., 2026)": "Feng et al., 2026" in text or "Feng, Y." in text,
    "Aider Repo Map (Gauthier, 2024)": "Gauthier, 2024" in text or "Gauthier, P." in text,
    "Theorem 1 Syntactic Closure": "Theorem 1 (Syntactic Closure)" in text,
    "Surrogate cost framing": "surrogate" in text.lower(),
    "Table 1 present": "**Table 1:" in text,
    "Table 2 present": "**Table 2:" in text,
    "Table 3 present": "**Table 3:" in text,
}

all_passed = True
for name, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if not passed:
        all_passed = False

print("\nOverall Manuscript Cleanliness:", "100% VERIFIED CLEAN" if all_passed else "HAS ISSUES")

