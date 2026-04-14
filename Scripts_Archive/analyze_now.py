#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

filepath = r'c:\Users\Administrator\Desktop\111\js\main.js'

with open(filepath, encoding='utf-8-sig') as f:
    content = f.read()

print(f'File length: {len(content)}')

patterns = ['worldBook', 'WorldBook', '语言规范', '记忆总结', 'writingStyle', 'memorySummary', 
            'worldbook', 'category', 'worldBookEntries', 'WorldBookModal', 'worldBookModal',
            'addWorldBook', 'editWorldBook', 'saveWorldBook', '世界观', '其他']

for p in patterns:
    idx = content.find(p)
    if idx >= 0:
        snippet = repr(content[idx:idx+120])
        print(f'Found [{p}] at {idx}: {snippet}')
    else:
        print(f'NOT FOUND: {p}')

# Get all occurrences of 记忆总结
import re
print('\n--- All occurrences of 记忆总结 ---')
for m in re.finditer('记忆总结', content):
    start = max(0, m.start()-100)
    end = min(len(content), m.end()+200)
    print(f'At {m.start()}: ...{content[start:end]}...')
    print('---')

# worldBook categories
print('\n--- worldBook category usages ---')
for m in re.finditer(r'category', content):
    start = max(0, m.start()-50)
    end = min(len(content), m.end()+100)
    snippet = content[start:end]
    if 'world' in snippet.lower() or '语言' in snippet or '记忆' in snippet or 'World' in snippet:
        print(f'At {m.start()}: ...{snippet}...')
        print('---')
