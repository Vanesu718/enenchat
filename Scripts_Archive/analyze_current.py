
# Analyze the current state of index.html and js/main.js
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()
    html_lines = html_content.split('\n')

# Find contacts menu section
print("=== CONTACTS MENU SECTION ===")
for i, line in enumerate(html_lines):
    if 'page-contacts' in line or 'openSub' in line or 'menu-item' in line or 'world-win' in line or 'writing-style' in line:
        print(f"Line {i+1}: {line}")

print("\n=== WORLD BOOK SECTION (world-win) ===")
in_world_win = False
for i, line in enumerate(html_lines):
    if 'world-win' in line:
        in_world_win = True
        start = max(0, i-2)
        print(f"Found at line {i+1}: {line}")
    if in_world_win and i > 0:
        if 'id="world-win"' in line or 'world-win' in line.strip()[:20]:
            for j in range(max(0,i-1), min(len(html_lines), i+80)):
                print(f"Line {j+1}: {html_lines[j]}")
            in_world_win = False
            break

print("\n=== CHAT SETTINGS SECTION ===")
for i, line in enumerate(html_lines):
    if 'chat-setting' in line.lower() or 'chatSetting' in line or 'contact-setting' in line:
        for j in range(max(0,i-1), min(len(html_lines), i+5)):
            print(f"Line {j+1}: {html_lines[j]}")
        print("---")

print("\n=== WRITING STYLE SEARCH ===")
for i, line in enumerate(html_lines):
    if 'writingStyle' in line or 'writing-style' in line or '文风' in line:
        print(f"Line {i+1}: {line}")
