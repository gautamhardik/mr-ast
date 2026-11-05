with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('## 5. Results')
idx2 = text.find('## 6. Controlled Gemma')
print(text[idx1:idx2])

