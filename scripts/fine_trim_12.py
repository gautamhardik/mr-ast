with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Section 4.2
old_s42 = "We enforce four strict token budgets: $B \\in \\{2000, 4000, 8000, 16000\\}$ subwords. All token counts are computed using the official **Google Gemma 4 tokenizer** (`google/gemma-4-31B-it-qat-w4a16-ct`, vocabulary 262,144)."
new_s42 = "We enforce four strict token budgets: $B \\in \\{2000, 4000, 8000, 16000\\}$ subwords. All token counts are measured using the official **Google Gemma 4 tokenizer** (vocabulary 262,144)."
text = text.replace(old_s42, new_s42)

# 2. Section 6 lead-in
old_s6_lead = "To investigate downstream prompt utility, we executed a controlled generation-latency pilot on **`google/gemma-4-31b-it`** across 6 SWE benchmark tasks under $B=2,000$ tokens (18 live API inferences):"
new_s6_lead = "To investigate prompt utility, we executed a generation-latency pilot on **`google/gemma-4-31b-it`** across 6 SWE benchmark tasks under $B=2,000$ tokens (18 live API inferences):"
text = text.replace(old_s6_lead, new_s6_lead)

# 3. Section 9 lead-in
old_s9_lead = "We examined the combinatorial bottleneck of context assembly in autonomous software engineering agents and introduced **MR-TopoS**, a multi-resolution context compiler."
new_s9_lead = "We addressed context assembly bottlenecks in software engineering agents and introduced **MR-TopoS**, a multi-resolution context compiler."
text = text.replace(old_s9_lead, new_s9_lead)

words = text.split()
print("Final word count:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved candidate.")

