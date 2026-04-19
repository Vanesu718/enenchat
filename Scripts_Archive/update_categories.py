import io
import re

with io.open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('语言规范', '世界观')

# Insert the '其他' option next to '世界观' for wb-tab
tab_search = '<div class="wb-tab" onclick="filterWorldBook(\'世界观\')" data-category="世界观" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">世界观</div>'
tab_replace = tab_search + '\n        <div class="wb-tab" onclick="filterWorldBook(\'其他\')" data-category="其他" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">其他</div>'

content = content.replace(tab_search, tab_replace)

# Insert the '其他' option in select
opt_search = '<option value="世界观">世界观</option>'
opt_replace = opt_search + '\n            <option value="其他">其他</option>'

content = content.replace(opt_search, opt_replace)

with io.open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html")
