
import re

with open(r'c:\Users\Administrator\Desktop\111\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

keywords = ['好感', 'affection', 'favor', '心声', 'innerVoice', 'inner_voice', 
            'themeMode', '普通模式', '简约模式', '闲聊', 'chatMode', 'currentMode',
            'regenerate', '重新生成', 'currentTheme', 'theme']

for kw in keywords:
    matches = [(i+1, line.rstrip()) for i, line in enumerate(lines) if kw.lower() in line.lower()]
    if matches:
        print(f'\n=== {kw}: {len(matches)} matches ===')
        for lineno, line in matches[:5]:
            print(f'  Line {lineno}: {line[:120]}')
