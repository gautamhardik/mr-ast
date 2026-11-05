with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('### 5.4')
print(text[idx:idx+1200])

