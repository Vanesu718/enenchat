#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mega fix script - applies all 5 changes:
1. World Book: 语言规范→世界观, add 其他 tab/option
2. Fix 记忆总结 trigger logic (per-contact enable check)
3. 文风设置 page (already exists, verify/ensure)
4. Chat settings: 文风单选 with warning
5. API compression on style switch + tail append
"""
import re, shutil, os

BASE = r'c:\Users\Administrator\Desktop\111'
HTML = os.path.join(BASE, 'index.html')
JS   = os.path.join(BASE, 'js', 'main.js')
BACKUP = os.path.join(BASE, 'backup_mega_fix')

# ── Backup ──────────────────────────────────────────────────
os.makedirs(BACKUP, exist_ok=True)
os.makedirs(os.path.join(BACKUP, 'js'), exist_ok=True)
shutil.copy2(HTML, os.path.join(BACKUP, 'index.html'))
shutil.copy2(JS,   os.path.join(BACKUP, 'js', 'main.js'))
print("✓ Backup done")

with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()
with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

changes = 0

# ════════════════════════════════════════════════════════════
# CHANGE 1a: World Book tabs – replace 语言规范 with 世界观, add 其他
# ════════════════════════════════════════════════════════════

# The tab for 语言规范
old_tab = "onclick=\"filterWorldBook('语言规范')\" data-category=\"语言规范\" style=\"flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);\">语言规范</div>"
new_tab = "onclick=\"filterWorldBook('世界观')\" data-category=\"世界观\" style=\"flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);\">世界观</div>"
if old_tab in html:
    html = html.replace(old_tab, new_tab, 1)
    print("✓ Replaced 语言规范 tab with 世界观")
    changes += 1
else:
    # Try partial match – the terminal showed garbled encoding in grep but file is utf-8
    # Use regex with flexible whitespace
    p = re.compile(r"onclick=\"filterWorldBook\('语言规范'\)\"[^>]*>语言规范</div>")
    m = p.search(html)
    if m:
        html = html[:m.start()] + "onclick=\"filterWorldBook('世界观')\" data-category=\"世界观\" style=\"flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);\">世界观</div>" + html[m.end():]
        print("✓ (regex) Replaced 语言规范 tab with 世界观")
        changes += 1
    else:
        print("✗ Could not find 语言规范 tab – check HTML manually")

# Add 其他 tab after the last wb-tab (before the closing row div)
# Find the pattern of the last tab in the world book filter row
# Look for the 全部 / 记忆总结 / 语言规范(now 世界观) tabs row and append 其他
other_tab = "<div class=\"wb-tab\" onclick=\"filterWorldBook('其他')\" data-category=\"其他\" style=\"flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);\">其他</div>"
if '其他' not in html or "filterWorldBook('其他')" not in html:
    # Insert after 世界观 tab
    marker = "filterWorldBook('世界观')"
    idx = html.find(marker)
    if idx != -1:
        # find the closing </div> of that tab
        end = html.find('</div>', idx)
        if end != -1:
            insert_pos = end + len('</div>')
            html = html[:insert_pos] + '\n        ' + other_tab + html[insert_pos:]
            print("✓ Added 其他 tab")
            changes += 1
    else:
        print("✗ Could not find insertion point for 其他 tab")
else:
    print("- 其他 tab already exists")

# ════════════════════════════════════════════════════════════
# CHANGE 1b: Dropdown option 语言规范 → 世界观, add 其他
# ════════════════════════════════════════════════════════════
old_opt = '<option value="语言规范">语言规范</option>'
new_opt = '<option value="世界观">世界观</option>'
if old_opt in html:
    html = html.replace(old_opt, new_opt + '\n            <option value="其他">其他</option>', 1)
    print("✓ Replaced 语言规范 option, added 其他 option")
    changes += 1
else:
    p2 = re.compile(r'<option value="语言规范">语言规范</option>')
    m2 = p2.search(html)
    if m2:
        html = html[:m2.start()] + new_opt + '\n            <option value="其他">其他</option>' + html[m2.end():]
        print("✓ (regex) Replaced 语言规范 option, added 其他 option")
        changes += 1
    else:
        print("✗ Could not find 语言规范 option")

# Also fix any JS filterWorldBook references if categories array is defined in HTML
html = html.replace("'语言规范'", "'世界观'")
html = html.replace('"语言规范"', '"世界观"')

# ════════════════════════════════════════════════════════════
# CHANGE 2: JS – fix 记忆总结 trigger logic in main.js
# ════════════════════════════════════════════════════════════
# The memory summary entries should only be injected if the current contact
# has explicitly enabled that entry. We look for the world book injection code.

# Pattern: when building context, entries with category=='记忆总结' are included globally
# We need to wrap them with a check:
#   if (entry.category === '记忆总结') { only include if contact has this entry enabled }

# Strategy: find the loop that processes world book entries for context injection
# and add a guard for 记忆总结 entries.

# First, let's find references to worldBookEntries in main.js
wb_mem_pattern = re.compile(
    r"(entry\.category\s*===?\s*['\"]记忆总结['\"])",
    re.DOTALL
)
matches = list(wb_mem_pattern.finditer(js))
print(f"Found {len(matches)} 记忆总结 category checks in main.js")

# Look for the world book context building section
# Typical pattern: entries filtered for context injection
# We want to find where worldbook entries are pushed to context messages

# Find the section that builds world book context injection
# Look for something like: worldBookEntries.filter or similar
context_inject_pattern = re.compile(
    r'(// .*?世界书.*?context|worldBook.*?inject|injectWorldBook|buildWorldBookContext)',
    re.IGNORECASE
)
ci_matches = list(context_inject_pattern.finditer(js))
print(f"Found {len(ci_matches)} world book context injection references")
for m in ci_matches[:5]:
    print(f"  at pos {m.start()}: {js[m.start():m.start()+100]!r}")

# More targeted: find where we iterate worldBookEntries and add to context
# Common pattern in this app:
iterate_wb = re.compile(
    r'(worldBookEntries|wbEntries).*?forEach|for.*?of.*?worldBook',
    re.IGNORECASE | re.DOTALL
)
it_matches = list(iterate_wb.finditer(js))
print(f"Found {len(it_matches)} worldBook iteration patterns")

# Look specifically for the pattern where 记忆总结 category is pushed to context
# The key fix: entries with category '记忆总结' should only be included if 
# current contact settings include this entry's ID in an enabled list.

# Search for any push to messages/context from worldBook
push_pattern = re.compile(
    r'(messages|contextMessages|systemContent|systemPrompt).*?\+?=.*?entry\.(content|text)',
    re.IGNORECASE
)
push_matches = list(push_pattern.finditer(js))
print(f"Found {len(push_matches)} message push patterns from entry")
for m in push_matches[:3]:
    print(f"  at pos {m.start()}: {js[m.start():m.start()+150]!r}")

# ════════════════════════════════════════════════════════════
# CHANGE 2 (targeted): Find the 记忆总结 always-inject block and fix it
# ════════════════════════════════════════════════════════════

# Look for the pattern: category === '记忆总结' combined with pushing to context
# without a contact-specific check
mem_always = re.compile(
    r"(entry\.category\s*===\s*'记忆总结'\s*\|\|[^}]{0,500}?)(//[^\n]*\n\s*)?(messages|systemPrompt|contextParts|injected|worldBookContext)",
    re.DOTALL
)
mem_always_m = list(mem_always.finditer(js))
print(f"Found {len(mem_always_m)} 记忆总结-to-context patterns")

# Since the pattern matching may be complex, let's look for the actual
# world book filtering code more specifically
# Search for lines containing both 记忆总结 and some injection/filter logic
lines = js.split('\n')
mem_lines = [(i, l) for i, l in enumerate(lines) if '记忆总结' in l]
print(f"Lines containing 记忆总结: {len(mem_lines)}")
for i, l in mem_lines[:20]:
    print(f"  line {i+1}: {l[:120]}")

print("\n--- Searching for world book context building code ---")
wb_context_lines = [(i, l) for i, l in enumerate(lines) 
                    if ('worldBook' in l or 'world_book' in l.lower()) 
                    and ('push' in l or 'system' in l.lower() or 'context' in l.lower() or 'inject' in l.lower())]
for i, l in wb_context_lines[:20]:
    print(f"  line {i+1}: {l[:120]}")

print("\n--- Searching for getRelevantWorldBookEntries or similar ---")
wb_func_lines = [(i, l) for i, l in enumerate(lines)
                 if 'getRelevant' in l or 'worldBookFor' in l or 'enabledWorld' in l
                 or 'worldbookEnabled' in l or 'wb_enabled' in l]
for i, l in wb_func_lines[:20]:
    print(f"  line {i+1}: {l[:120]}")

# Save current state of html
with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\n✓ Saved index.html with {changes} changes")

# Save JS analysis log
with open(os.path.join(BASE, 'analysis_log.txt'), 'w', encoding='utf-8') as f:
    f.write(f"=== JS Analysis ===\n")
    f.write(f"Total lines: {len(lines)}\n")
    f.write(f"\n--- 记忆总结 lines ---\n")
    for i, l in mem_lines:
        f.write(f"line {i+1}: {l}\n")
    f.write(f"\n--- WorldBook context lines ---\n")
    for i, l in wb_context_lines:
        f.write(f"line {i+1}: {l}\n")
    f.write(f"\n--- WorldBook func lines ---\n")
    for i, l in wb_func_lines:
        f.write(f"line {i+1}: {l}\n")
print("✓ Saved analysis_log.txt")
print("\nDone phase 1 (HTML changes + JS analysis). Check analysis_log.txt for JS structure.")
