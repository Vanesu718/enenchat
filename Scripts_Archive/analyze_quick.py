
import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

print('File length:', len(content))

patterns = ['语言规范', 'worldbook-category', 'WORLDBOOK_ENTRIES', '记忆总结', 'getContactWorldBookPrompt', 'selectedWorldBooks', 'compressedStyle', 'writingStyle', '文风']

for pat in patterns:
    matches = list(re.finditer(re.escape(pat), content))
    print(f'\n--- Pattern: {pat} ({len(matches)} matches) ---')
    for m in matches[:3]:
        ctx = content[max(0, m.start()-80):m.start()+160]
        print(repr(ctx))
