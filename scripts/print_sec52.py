with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('### 5.2')
idx2 = text.find('### 5.3')
print(repr(text[idx1:idx2]))

