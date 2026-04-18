import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all garbled AI icon filenames
content = re.sub(r'ICON/AI[^\x00-\x7F"\']+\.png', 'ICON/AI提炼图标.png', content)

# Fix garbled text after manualAiCompress button
content = re.sub(
    r'(onclick="manualAiCompress\(\)"><img src="ICON/AI提炼图标\.png" style="[^"]+">)\s*[^\x00-\x7F<]+',
    r'\1 一键提取</span>',
    content
)

# Fix garbled text after generatePersonaMemo contactMemo button
content = re.sub(
    r"(onclick=\"generatePersonaMemo\('contactMemo', 'contactPersona'\)\"><img src=\"ICON/AI提炼图标\.png\" style=\"[^\"]+\">)\s*[^\x00-\x7F<]+",
    r'\1 AI 一键提取</button>',
    content
)

# Fix garbled text after generatePersonaMemo chatContactMemo button
content = re.sub(
    r"(onclick=\"generatePersonaMemo\('chatContactMemo', 'contactMaskTextarea'\)\"><img src=\"ICON/AI提炼图标\.png\" style=\"[^\"]+\">)\s*[^\x00-\x7F<]+",
    r'\1 AI 提取</button>',
    content
)

# Fix garbled text after generateBoardAI button
content = re.sub(
    r'(onclick="generateBoardAI\(\)"><img src="ICON/AI提炼图标\.png" style="[^"]+">)\s*[^\x00-\x7F<]+',
    r'\1 AI 生成</button>',
    content
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

for fn in ['manualAiCompress', 'generatePersonaMemo', 'generateBoardAI']:
    idx = c.find(fn)
    if idx >= 0:
        print(f'{fn}: {c[idx:idx+180]}')
        print('---')

ai_refs = re.findall(r'ICON/AI[^"]+\.png', c)
print('AI icon refs:', ai_refs)
