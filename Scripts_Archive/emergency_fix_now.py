import os

def fix_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if filepath == 'index.html':
        content = content.replace('🔄 刷新', '<img src="ICON/刷新.png" style="width:18px;height:18px;vertical-align:middle;"> 刷新')
        # Just in case
        content = content.replace('<div style="cursor:pointer;" onclick="refreshChatWindow()">🔄 刷新</div>', '<div style="cursor:pointer;" onclick="refreshChatWindow()"><img src="ICON/刷新.png" style="width:18px;height:18px;vertical-align:middle;"> 刷新</div>')
    
    if filepath == 'js/main.js':
        content = content.replace('src="ICON/点赞前.png" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">已赞', 'src="ICON/点赞.png" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">已赞')
        content = content.replace('src="ICON/更多.png" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">删除', 'src="ICON/删除.png" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">删除')
        # If there are any other places with ICON/点赞前.png inside "已赞"
        content = content.replace('ICON/点赞前.png" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">已赞', 'ICON/点赞.png" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">已赞')
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file('index.html')
fix_file('js/main.js')
