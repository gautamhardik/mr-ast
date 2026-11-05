with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

words = text.split()
print('Total word count in final_submission_candidate.md:', len(words))

import re
sections = re.split(r'\n(?=## )', text)
for i, s in enumerate(sections):
    h = s.split('\n')[0]
    w = len(s.split())
    print(f'{i:2d}. {h[:45]}: {w} words')

