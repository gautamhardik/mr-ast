with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Table 2 block with concise prose referencing Table 1
old_table2_block = """### 5.2 Information Preservation & Resolution Distribution
Table 2 details representation breakdown between Scoped BM25 and MR-TopoS:

**Table 2: Representation Distribution & Code Retention**

| Budget $B$ | Paradigm | Total Symbols | Full Impls | Skeletons | Stubs | Pre-Existing Gold Recall |
|---|---|---|---|---|---|---|
| **2,000** | Scoped BM25 | 12.55 | 12.55 | 0.0 | 0.0 | 0.3728 |
| | **MR-TopoS MILP** | **50.85** ($4.05\times$) | **19.47** ($1.55\times$) | **30.00** | **1.39** | **0.4846** ($+29.98\%$) |
| **4,000** | Scoped BM25 | 19.98 | 19.98 | 0.0 | 0.0 | 0.4282 |
| | **MR-TopoS MILP** | **55.15** ($2.76\times$) | **32.50** ($1.63\times$) | **22.11** | **0.53** | **0.5408** ($+26.30\%$) |
| **8,000** | Scoped BM25 | 33.09 | 33.09 | 0.0 | 0.0 | **0.5555** |
| | **MR-TopoS MILP** | **58.29** ($1.76\times$) | **44.53** ($1.35\times$) | **13.33** | **0.43** | 0.5520 |
| **16,000** | Scoped BM25 | 47.76 | 47.76 | 0.0 | 0.0 | **0.5961** |
| | **MR-TopoS MILP** | **59.90** ($1.25\times$) | **53.60** ($1.12\times$) | **5.98** | **0.32** | 0.5705 |

**Core Finding**: MR-TopoS retains **$1.55\times$ more full implementations** (19.47 vs 12.55) at $B=2,000$, while simultaneously providing 30.00 contract skeletons. Pruning intermediate candidates into skeletons frees capacity to pack genuinely more executable implementations alongside architectural context."""

new_table2_block = """### 5.2 Information Preservation & Resolution Distribution
As shown in Table 1, MR-TopoS's symbol capacity advantage does not sacrifice implementation depth. At $B=2,000$, MR-TopoS retains **$1.55\times$ more full implementations** ($19.47$ vs $12.55$) than Scoped BM25, allocating $1,849$ tokens to full executable bodies versus $1,192$. Because monolithic inclusion consumes scarce capacity on non-target code, compressing intermediate symbols into contract skeletons ($30.00$ at $2\text{k}$) and stubs ($1.39$) frees budget to retain genuinely more full implementations of high-priority targets alongside structural context."""

text = text.replace(old_table2_block, new_table2_block)

# Fix saturation section to candidly describe dynamic K as an unverified hypothesis / future work
text = text.replace("Dynamically scaling candidate pool depth ($K = \\min(200, B/30)$) resolves this boundary effect.", "Dynamically scaling candidate pool depth ($K = \\min(200, B/30)$) is an unverified hypothesis and remains future work.")

# Ensure Table 2 (solver) and Table 3 (gemma pilot) are cleanly numbered
text = text.replace("Table 3 compares HiGHS MILP", "Table 2 compares HiGHS MILP")

print("New total words:", len(text.split()))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

import subprocess, sys
subprocess.run([sys.executable, 'scripts/generate_pdf.py'], capture_output=True)
import fitz
doc = fitz.open('paper/final_submission_candidate.pdf')
print('PDF pages:', len(doc))
doc.close()

