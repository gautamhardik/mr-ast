with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.split(r'\n(?=## )', text)
print('--- SECTION 1 ---')
print(sections[2][:1000])

