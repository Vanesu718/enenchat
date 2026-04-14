# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count replacements
count = 0

# 1. Writing style page: replace emoji before "一键提取"
old1 = 'manualAiCompress()">\U0001f4f8\U0001f4f8 \u4e00\u952e\u63d0\u53d6</span>'
if old1 not in content:
    # Try alternate pattern with question marks
    # Search for the actual text around manualAiCompress
    import re
    m = re.search(r'(onclick="manualAiCompress\(\)">)(.*?)(</span>)', content)
    if m:
        old_text = m.group(0)
        new_text = m.group(1) + '<img src="ICON/AI\u63d0\u70bc\u56fe\u6807.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> \u4e00\u952e\u63d0\u53d6' + m.group(3)
        content = content.replace(old_text, new_text)
        count += 1
        print(f"Replaced writing style button: {old_text[:50]}...")
else:
    new1 = 'manualAiCompress()"><img src="ICON/AI\u63d0\u70bc\u56fe\u6807.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> \u4e00\u952e\u63d0\u53d6</span>'
    content = content.replace(old1, new1)
    count += 1

# 2. addContact page: replace robot emoji before "AI 一键提取"
old2 = "generatePersonaMemo('contactMemo', 'contactPersona')\">\U0001f916 AI \u4e00\u952e\u63d0\u53d6</button>"
if old2 in content:
    new2 = "generatePersonaMemo('contactMemo', 'contactPersona')\"><img src=\"ICON/AI\u63d0\u70bc\u56fe\u6807.png\" style=\"width:14px;height:14px;vertical-align:middle;margin-right:2px;\"> AI \u4e00\u952e\u63d0\u53d6</button>"
    content = content.replace(old2, new2)
    count += 1
    print("Replaced addContact AI button")
else:
    # Try regex
    m = re.search(r"(generatePersonaMemo\('contactMemo', 'contactPersona'\)\">)(.*?)(</button>)", content)
    if m:
        old_text = m.group(0)
        new_text = m.group(1) + '<img src="ICON/AI\u63d0\u70bc\u56fe\u6807.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> AI \u4e00\u952e\u63d0\u53d6' + m.group(3)
        content = content.replace(old_text, new_text)
        count += 1
        print(f"Replaced addContact AI button via regex: {old_text[:60]}...")

# 3. Chat settings page: replace robot emoji before "AI 提取"
old3 = "generatePersonaMemo('chatContactMemo', 'contactMaskTextarea')\">\U0001f916 AI \u63d0\u53d6</button>"
if old3 in content:
    new3 = "generatePersonaMemo('chatContactMemo', 'contactMaskTextarea')\"><img src=\"ICON/AI\u63d0\u70bc\u56fe\u6807.png\" style=\"width:14px;height:14px;vertical-align:middle;margin-right:2px;\"> AI \u63d0\u53d6</button>"
    content = content.replace(old3, new3)
    count += 1
    print("Replaced chat settings AI button")
else:
    m = re.search(r"(generatePersonaMemo\('chatContactMemo', 'contactMaskTextarea'\)\">)(.*?)(</button>)", content)
    if m:
        old_text = m.group(0)
        new_text = m.group(1) + '<img src="ICON/AI\u63d0\u70bc\u56fe\u6807.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> AI \u63d0\u53d6' + m.group(3)
        content = content.replace(old_text, new_text)
        count += 1
        print(f"Replaced chat settings AI button via regex: {old_text[:60]}...")

# 4. Forum board page: replace sparkle emoji before "AI 生成"
old4 = 'generateBoardAI()">\u2728 AI \u751f\u6210</button>'
if old4 in content:
    new4 = 'generateBoardAI()"><img src="ICON/AI\u63d0\u70bc\u56fe\u6807.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> AI \u751f\u6210</button>'
    content = content.replace(old4, new4)
    count += 1
    print("Replaced forum board AI button")
else:
    m = re.search(r'(generateBoardAI\(\)">)(.*?)(</button>)', content)
    if m:
        old_text = m.group(0)
        new_text = m.group(1) + '<img src="ICON/AI\u63d0\u70bc\u56fe\u6807.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> AI \u751f\u6210' + m.group(3)
        content = content.replace(old_text, new_text)
        count += 1
        print(f"Replaced forum board AI button via regex: {old_text[:60]}...")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal replacements in index.html: {count}")
