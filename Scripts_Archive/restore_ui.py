import os

# Read the backup index.html
with open('backup_before_writing_style_fix/index.html', 'r', encoding='utf-8') as f:
    backup_lines = f.readlines()

# Read the current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    current_lines = f.readlines()

# Find the block for contactMemo in backup
contact_memo_block = []
in_block = False
for line in backup_lines:
    if '<div class="form-section">' in line and '核心设定与环境备忘录' in backup_lines[backup_lines.index(line) + 2]:
        in_block = True
    if in_block:
        contact_memo_block.append(line)
        if '</div>' in line and len(contact_memo_block) > 5:  # closing div for form-section
            break

# Block 1 is lines 908 to 915 in backup
contact_memo_block = backup_lines[907:915]

# Block 2 is lines 1170 to 1178 in backup
chat_contact_memo_block = backup_lines[1169:1178]

# Insert block 1 into current index.html before <button class="save-btn" onclick="saveContact()">创建角色</button>
new_lines = []
for i, line in enumerate(current_lines):
    if '<button class="save-btn" onclick="saveContact()">创建角色</button>' in line:
        new_lines.extend(contact_memo_block)
    if '<!-- 关联世界书设置 -->' in line:
        new_lines.extend(chat_contact_memo_block)
        new_lines.append('\n')
    new_lines.append(line)

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Restored UI elements successfully.")
