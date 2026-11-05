with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('### 2.3')
idx2 = text.find('## 3. Methodology')
print(text[idx1:idx2])

