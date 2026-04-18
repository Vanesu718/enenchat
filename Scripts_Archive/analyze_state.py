
import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} chars")

patterns = [
    '语言规范', 'worldBook', 'world_book',
    '记忆总结', 'compressedStyle', '文风',
    'writingStyle', 'contactSettings', 'chatSettings',
    'systemPrompt', 'buildPrompt',
    'showContacts', 'showWorldBook', 'worldBookEntries',
    'categoryFilter', 'worldbookCategory'
]

for p in patterns:
    matches = list(re.finditer(p, content))
    if matches:
        print(f'\n=== {p} ({len(matches)} matches) ===')
        for m in matches[:3]:
            ctx = content[max(0,m.start()-60):m.start()+120]
            print(f'  pos={m.start()}: {repr(ctx)}')
