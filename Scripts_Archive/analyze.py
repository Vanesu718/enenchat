import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

keywords = ['worldbook', 'worldBook', 'WorldBook', '记忆总结', '语言规范', 'worldbookEntries', 'writingStyle', '世界书', 'loreBook', '世界观', 'categoryFilter']
count = 0
for i, line in enumerate(lines):
    for kw in keywords:
        if kw in line:
            print(f'{i+1}: {line[:120]}')
            count += 1
            break
    if count >= 100:
        print('...truncated...')
        break
