with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('### 5.2 Information Preservation & Resolution Distribution')
idx2 = text.find('### 5.3 Candidate Saturation')

new_table2_block = """### 5.2 Information Preservation & Resolution Breakdown
As shown in Table 1, MR-TopoS's symbol capacity advantage does not sacrifice implementation depth. At $B=2,000$, MR-TopoS retains **$1.55\\times$ more full implementations** ($19.47$ vs $12.55$) than Scoped BM25, allocating $1,849$ tokens to full executable bodies versus $1,192$. Because monolithic inclusion consumes scarce capacity on non-target code, compressing intermediate symbols into contract skeletons ($30.00$ at $2\\text{k}$) and stubs ($1.39$) frees budget to retain genuinely more full implementations of high-priority targets alongside structural context."""

text = text[:idx1] + new_table2_block + "\n\n" + text[idx2:]

# Check word count
words = text.split()
print("New total word count:", len(words))

with open('paper/final_submission_candidate.md', 'w', encoding='utf-8') as f:
    f.write(text)

import subprocess, sys
subprocess.run([sys.executable, 'scripts/generate_pdf.py'], capture_output=True)
import fitz
doc = fitz.open('paper/final_submission_candidate.pdf')
print('PDF pages:', len(doc))
doc.close()

