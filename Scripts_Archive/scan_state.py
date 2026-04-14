
import re

with open('c:/Users/Administrator/Desktop/111/js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
keywords = ['语言规范', '世界观', 'worldbook-category', 'writingStyle', 'compressedStyle', '记忆总结', '文风', 'writing-style', 'writingstyle']
print(f"Total lines: {len(lines)}")
print("="*60)
for i, line in enumerate(lines):
    line_lower = line.lower()
    for kw in keywords:
        if kw in line or kw.lower() in line_lower:
            print(f"Line {i+1}: {line[:150]}")
            break
