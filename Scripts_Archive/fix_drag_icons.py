import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace drag handle icon
content = re.sub(r'class="drag-handle"([^>]+)>.*?</div>', r'class="drag-handle"\1>☰</div>', content)

# Replace group list header
# Use strict string replacement to avoid regex compilation issues with nested string literals
old_header = """    header.style.cssText = 'display:flex; align-items:center; padding:10px 5px 6px; cursor:grab; user-select:none;';
    header.innerHTML = `
      <span style="font-size:12px; color:var(--text-dark); margin-right:6px; transition:transform 0.2s; display:inline-block; transform:rotate(${isCollapsed ? '0' : '90'}deg);">?</span>
      <span style="font-size:14px; font-weight:600; color:var(--text-dark); pointer-events:none;">${groupName}</span>
      <span style="font-size:12px; color:var(--text-dark); margin-left:6px; pointer-events:none;">(${sorted.length})</span>
    `;"""

new_header = """    header.style.cssText = 'display:flex; align-items:center; padding:10px 5px 6px; cursor:grab; user-select:none; color:var(--text-dark);';
    header.innerHTML = `
      <span style="font-size:12px; color:inherit; margin-right:6px; transition:transform 0.2s; display:inline-block; transform:rotate(${isCollapsed ? '0' : '90'}deg);">▶</span>
      <span style="font-size:14px; font-weight:600; color:inherit; pointer-events:none;">${groupName}</span>
      <span style="font-size:12px; color:inherit; margin-left:6px; pointer-events:none;">(${sorted.length})</span>
    `;"""

content = content.replace(old_header, new_header)

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement script executed.")
