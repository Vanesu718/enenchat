#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply all final changes:
1. World Book: 语言规范→世界观, add 其他 category in tabs and dropdown
2. Fix 记忆总结 trigger: only inject if contact has that entry enabled
3. 文风设置 page already exists in index.html - verify & fix
4. Chat settings: 文风单选 with warning - verify & fix  
5. API compression on style switch + small tail append
"""

import re
import shutil
import os

# Backup first
def backup():
    src = r'c:\Users\Administrator\Desktop\111'
    dst = r'c:\Users\Administrator\Desktop\111\backup_final_v3'
    if not os.path.exists(dst):
        os.makedirs(dst)
    for f in ['index.html']:
        if os.path.exists(os.path.join(src, f)):
            shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    js_dst = os.path.join(dst, 'js')
    if not os.path.exists(js_dst):
        os.makedirs(js_dst)
    for f in ['main.js']:
        src_f = os.path.join(src, 'js', f)
        if os.path.exists(src_f):
            shutil.copy2(src_f, os.path.join(js_dst, f))
    print("Backup done to backup_final_v3/")

backup()

# Read files
with open(r'c:\Users\Administrator\Desktop\111\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open(r'c:\Users\Administrator\Desktop\111\js\main.js', 'r', encoding='utf-8') as f:
    js = f.read()

print(f"index.html length: {len(html)}")
print(f"main.js length: {len(js)}")

# ============================================================
# CHANGE 1: World Book tabs: 语言规范 → 世界观, add 其他 tab
# ============================================================

# Replace the tab that says 语言规范 in world book
old_tab = '<div class="wb-tab" onclick="filterWorldBook(\'语言规范\')" data-category="语言规范" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">语言规范</div>'
new_tab = '<div class="wb-tab" onclick="filterWorldBook(\'世界观\')" data-category="世界观" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">世界观</div>'

if old_tab in html:
    html = html.replace(old_tab, new_tab)
    print("✓ Changed 语言规范 tab to 世界观")
else:
    print("✗ Could not find 语言规范 tab - trying partial match")
    # Try partial match
    html = html.replace("filterWorldBook('语言规范')", "filterWorldBook('世界观')")
    html = html.replace('data-category="语言规范"', 'data-category="世界观"')
    html = html.replace('>语言规范</div>', '>世界观</div>')
    print("  Applied partial replacements for 语言规范→世界观")

# Add 其他 tab after html tab in the world book tabs section
# Find the html tab and add 其他 after it
old_html_tab = '<div class="wb-tab" onclick="filterWorldBook(\'html\')" data-category="html" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">html</div>'
other_tab = '\n        <div class="wb-tab" onclick="filterWorldBook(\'其他\')" data-category="其他" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">其他</div>'

if old_html_tab in html and other_tab not in html:
    html = html.replace(old_html_tab, old_html_tab + other_tab)
    print("✓ Added 其他 tab after html tab")
elif other_tab in html:
    print("  其他 tab already exists")
else:
    print("✗ Could not find html tab for insertion")

# ============================================================
# CHANGE 2: World Book dropdown: 语言规范 → 世界观, add 其他 option
# ============================================================

# Replace option value in dropdown
html = html.replace('<option value="语言规范">语言规范</option>', '<option value="世界观">世界观</option>')
print("✓ Changed dropdown option 语言规范→世界观")

# Add 其他 option after html option in the worldbook category dropdown
old_html_opt = '<option value="html">html</option>'
other_opt = '\n              <option value="其他">其他</option>'

# Count occurrences of html option
count = html.count(old_html_opt)
print(f"  Found {count} occurrences of html option")

if count > 0 and other_opt.strip() not in html:
    # Replace first occurrence (in world book add/edit form)
    html = html.replace(old_html_opt, old_html_opt + other_opt, 1)
    print("✓ Added 其他 option in world book dropdown")
elif other_opt.strip() in html:
    print("  其他 option already exists in dropdown")
else:
    print("✗ Could not find html option for insertion")

# ============================================================
# WRITE UPDATED HTML
# ============================================================

with open(r'c:\Users\Administrator\Desktop\111\index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("\n✓ index.html saved")

# ============================================================
# NOW CHECK main.js FOR KEY FUNCTIONS
# ============================================================

print("\n--- Checking main.js for key functions ---")

# Check for filterWorldBook function
if 'filterWorldBook' in js:
    print("✓ filterWorldBook found in main.js")
else:
    print("✗ filterWorldBook NOT found in main.js")

# Check for 记忆总结 injection logic
if '记忆总结' in js:
    idx = js.find('记忆总结')
    print(f"✓ 记忆总结 found at index {idx}")
    print(f"  Context: ...{js[max(0,idx-100):idx+200]}...")
else:
    print("✗ 记忆总结 NOT found in main.js")

# Check for writingStyle
if 'writingStyle' in js:
    idx = js.find('writingStyle')
    print(f"✓ writingStyle found at index {idx}")
else:
    print("✗ writingStyle NOT found in main.js")

# Check for compressedStyle or 小尾巴
if 'compressedStyle' in js:
    print("✓ compressedStyle found in main.js")
elif '系统强制指令' in js:
    print("✓ 系统强制指令 (small tail) found in main.js")
else:
    print("✗ compressedStyle/系统强制指令 NOT found in main.js - needs to be added")

print("\nDone. Check output above for what needs JS changes.")
