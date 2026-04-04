
content = open('c:/Users/Administrator/Desktop/111/index.html', 'r', encoding='utf-8').read()

# Find the theme-text-setting page-body section and insert theme selector as first item
old = '      <div class="page-body">\n        <div class="setting-desc" style="margin-bottom:15px;">支持针对普通正文以及被 {}、"" 或 \u201c\u201d 包裹的文字分别设置样式。</div>'

new = '      <div class="page-body">\n        <div class="menu-item" onclick="openSub(\'theme-selector\')" style="padding:16px; margin-bottom:16px;">\n          <div style="display:flex; justify-content:space-between; align-items:center;">\n            <span style="font-weight:500;">选择主题</span>\n            <span style="color:var(--text-light);">></span>\n          </div>\n        </div>\n        <div class="setting-desc" style="margin-bottom:15px;">支持针对普通正文以及被 {}、"" 或 \u201c\u201d 包裹的文字分别设置样式。</div>'

if old in content:
    content = content.replace(old, new, 1)
    open('c:/Users/Administrator/Desktop/111/index.html', 'w', encoding='utf-8').write(content)
    print('SUCCESS')
else:
    print('NOT FOUND')
    idx = content.find('支持针对普通正文以及被')
    if idx >= 0:
        print(repr(content[idx-200:idx+300]))
    else:
        print('String not found at all')
