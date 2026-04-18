
import sys
content = open('js/main.js', encoding='utf-8', errors='replace').read()
print(f"Total length: {len(content)}")
terms = ['worldBook', 'WorldBook', '语言规范', '记忆总结', '文风', 'writingStyle', 'worldbook', 'world_book', 'lore', 'category', 'Category']
for t in terms:
    idx = content.find(t)
    if idx >= 0:
        print(f'FOUND [{t}] at {idx}: ...{repr(content[max(0,idx-30):idx+80])}')
    else:
        print(f'NOT FOUND: {t}')
