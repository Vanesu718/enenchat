import os

content = open('c:/Users/Administrator/Desktop/111/js/main.js', encoding='utf-8', errors='replace').read()
print('File size:', len(content))
terms = ['writingStyle', '文风', '世界观', '语言规范', '记忆总结', 'worldBookEntries', 'worldBook']
for t in terms:
    idx = content.find(t)
    if idx >= 0:
        print(f'Found "{t}" at position {idx}')
        print('  Context:', repr(content[max(0,idx-50):idx+100]))
    else:
        print(f'NOT FOUND: "{t}"')
