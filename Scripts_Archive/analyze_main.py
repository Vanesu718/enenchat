
import re

with open('js/main.js', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print(f"Total lines: {len(lines)}")

keywords = ['语言规范', '记忆', '世界书', 'worldBook', 'lorebook', 'category', 'writing', 'worldbook']
for i, line in enumerate(lines):
    if any(k in line for k in keywords):
        print(f"{i+1}: {line.rstrip()}")
