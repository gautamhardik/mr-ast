with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.split(r'\n(?=## )', text)
print('--- SECTION 5 ---')
print(sections[6][:1500])

