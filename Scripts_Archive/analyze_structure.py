
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('js/main.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

keywords = ['语言规范', '记忆总结', '世界观', 'writingStyle', '文风', 
            'filterWorldBook', 'renderWorldBook', 'worldbook-category',
            'worldBookEntries', 'getContactWorldBook', 'selectedWorldBooks',
            'chat-settings', 'chatSettings', 'openChatSettings',
            'contacts-menu', 'contactsMenu', '通讯录',
            'WORLD_BOOK_PRIORITY']

for i, line in enumerate(lines):
    for kw in keywords:
        if kw in line:
            print(f'Line {i+1}: {line.rstrip()}')
            break
