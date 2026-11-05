with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('## 4. Experimental Setup')
idx2 = text.find('## 5. Results')
print(text[idx1:idx2])

