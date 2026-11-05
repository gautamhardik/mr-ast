with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('## 6. Controlled Gemma')
print(text[idx:])

