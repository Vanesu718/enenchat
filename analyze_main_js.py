import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

print('File size:', len(content), 'chars')

patterns = ['语言规范', '记忆总结', 'writingStyle', '文风', 'worldbook-category', 'worldbookCategory', 'lore-category', 'category']
for p in patterns:
    matches = list(re.finditer(p, content))
    print(f'Pattern [{p}]: {len(matches)} matches')
    if matches:
        m = matches[0]
        print('  First:', repr(content[max(0,m.start()-50):m.start()+150]))
