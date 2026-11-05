with open('paper/final_submission_candidate.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'## References', text)]
print('References occurrences at indices:', matches)

