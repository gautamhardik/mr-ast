with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('## 3. Methodology')
idx2 = text.find('## 4. Experimental Setup')
print(text[idx1:idx2])

