import re

with open('index.html', encoding='utf-8', errors='replace') as f:
    content = f.read()

lines = content.split('\n')
keywords = ['favor', 'affection', 'innerVoice', 'isRegen', 'chatMode', 'themeMode', 
            'regenerat', 'reroll', 'inner_voice', 'innervoice', 'currentMode',
            'modeSelect', 'affinity', 'heart', '好感']

results = []
for i, line in enumerate(lines):
    for kw in keywords:
        if kw.lower() in line.lower():
            results.append(f'{i+1}: {line.rstrip()}')
            break

print(f'Total matches: {len(results)}')
print('\n'.join(results[:100]))
