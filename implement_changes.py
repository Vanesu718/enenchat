#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive implementation script for all 5 steps of changes.
Reads main.js, makes targeted replacements, writes back.
"""

import re
import shutil
import os
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'
MAIN_JS = os.path.join(BASE, 'js', 'main.js')
INDEX_HTML = os.path.join(BASE, 'index.html')

# ── Backup ──────────────────────────────────────────────────────────────────
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = os.path.join(BASE, f'backup_{ts}')
os.makedirs(backup_dir, exist_ok=True)
for f in [MAIN_JS, INDEX_HTML]:
    shutil.copy2(f, os.path.join(backup_dir, os.path.basename(f)))
print(f'[OK] Backup created: {backup_dir}')

# ── Read files ───────────────────────────────────────────────────────────────
with open(MAIN_JS, 'r', encoding='utf-8') as f:
    js = f.read()

with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    html = f.read()

print(f'[OK] Read main.js ({len(js)} chars), index.html ({len(html)} chars)')

changes_made = []

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2A: World Book UI – rename 语言规范 → 世界观, add 其他
# ═══════════════════════════════════════════════════════════════════════════

# In HTML: worldbook category filter tabs
old_tab = "'语言规范'"
new_tab = "'世界观'"
if old_tab in html:
    html = html.replace(old_tab, new_tab)
    changes_made.append('HTML: replaced 语言规范 → 世界观 in tab strings')

# Also plain text in option values
for pattern, replacement in [
    ('value="语言规范"', 'value="世界观"'),
    ('>语言规范<', '>世界观<'),
]:
    if pattern in html:
        html = html.replace(pattern, replacement)
        changes_made.append(f'HTML: {pattern} → {replacement}')

# Add 其他 option after 世界观 in select dropdowns for worldbook category
# Pattern: after the 世界观 option in worldbook-category select
for old_opt, new_opt in [
    ('<option value="世界观">世界观</option>\n                    </select>',
     '<option value="世界观">世界观</option>\n                    <option value="其他">其他</option>\n                    </select>'),
    ('<option value="世界观">世界观</option>\n                </select>',
     '<option value="世界观">世界观</option>\n                <option value="其他">其他</option>\n                </select>'),
]:
    if old_opt in html:
        html = html.replace(old_opt, new_opt)
        changes_made.append('HTML: Added 其他 option to worldbook category select')

# In JS: replace category string literals
for old, new in [
    ("'语言规范'", "'世界观'"),
    ('"语言规范"', '"世界观"'),
    ('语言规范', '世界观'),  # catch remaining bare references  
]:
    # Only replace in worldbook-related context; use careful replacement
    pass

# Replace all occurrences of 语言规范 in JS (it's a category value)
js = js.replace('语言规范', '世界观')
changes_made.append('JS: replaced all 语言规范 → 世界观')

# Add 其他 to the categories array/list in JS if present
for old, new in [
    ("['记忆总结', '世界观']", "['记忆总结', '世界观', '其他']"),
    ('["记忆总结", "世界观"]', '["记忆总结", "世界观", "其他"]'),
    ("categories = ['记忆总结', '世界观']", "categories = ['记忆总结', '世界观', '其他']"),
    ("WORLDBOOK_CATEGORIES = ['记忆总结', '世界观']", "WORLDBOOK_CATEGORIES = ['记忆总结', '世界观', '其他']"),
]:
    if old in js:
        js = js.replace(old, new)
        changes_made.append(f'JS: categories array updated with 其他')

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2B: Fix 记忆总结 trigger logic
# The old code pushes 记忆总结 entries for ALL contacts.
# New logic: only push if the entry.id is in contactSettings.selectedWorldBooks
# ═══════════════════════════════════════════════════════════════════════════

# Find the getContactWorldBookPrompt function and fix the 记忆总结 branch
# Old pattern (approximate):
old_memory_logic = """        if (entry.category === '记忆总结') {
          activeWorldBooks.push(`[${entry.name}]\\n${entry.content}`);"""
new_memory_logic = """        if (entry.category === '记忆总结') {
          // 记忆总结: only inject if explicitly selected for this contact
          if (contactSettings.selectedWorldBooks && contactSettings.selectedWorldBooks.includes(entry.id)) {
            activeWorldBooks.push(`[${entry.name}]\\n${entry.content}`);
          }"""

if old_memory_logic in js:
    js = js.replace(old_memory_logic, new_memory_logic)
    changes_made.append('JS: Fixed 记忆总结 trigger to only fire for selected contacts')
else:
    # Try without the push line being exact - search for the pattern
    pattern = r"if \(entry\.category === '记忆总结'\) \{"
    match = re.search(pattern, js)
    if match:
        # Find the next push line
        pos = match.start()
        snippet = js[pos:pos+300]
        print(f'[DEBUG] Found 记忆总结 block: {repr(snippet[:150])}')
    changes_made.append('JS: WARNING - could not find exact 记忆总结 pattern, manual check needed')

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: Writing Style (文风设置) – add data + functions to JS
# ═══════════════════════════════════════════════════════════════════════════

WRITING_STYLE_JS = """
// ═══════════════════════════════════════════════════════════════════
// 文风设置 (Writing Style) Module
// ═══════════════════════════════════════════════════════════════════

let writingStyleEntries = [];

async function loadWritingStyleEntries() {
  const raw = await getFromStorage('WRITING_STYLE_ENTRIES');
  writingStyleEntries = raw ? (typeof raw === 'string' ? JSON.parse(raw) : raw) : [];
  return writingStyleEntries;
}

async function saveWritingStyleEntries() {
  await saveToStorage('WRITING_STYLE_ENTRIES', JSON.stringify(writingStyleEntries));
}

function generateWritingStyleId() {
  return 'ws_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

async function showWritingStylePage() {
  await loadWritingStyleEntries();
  const container = document.getElementById('main-content') || document.getElementById('app');
  if (!container) return;

  container.innerHTML = `
    <div class="writing-style-page" style="height:100%;display:flex;flex-direction:column;">
      <div class="page-header" style="display:flex;align-items:center;padding:12px 16px;background:#fff;border-bottom:1px solid #e5e5e5;">
        <button onclick="showContactsPage()" style="background:none;border:none;font-size:20px;cursor:pointer;margin-right:12px;">←</button>
        <h2 style="margin:0;font-size:18px;font-weight:600;">文风设置</h2>
        <button onclick="showAddWritingStyleModal()" style="margin-left:auto;background:#07c160;color:#fff;border:none;border-radius:6px;padding:8px 16px;cursor:pointer;font-size:14px;">+ 新增文风</button>
      </div>
      <div id="writing-style-list" style="flex:1;overflow-y:auto;padding:12px;">
        ${writingStyleEntries.length === 0
          ? '<div style="text-align:center;color:#999;padding:40px;">暂无文风条目，点击右上角新增</div>'
          : writingStyleEntries.map(entry => `
            <div class="ws-entry-card" style="background:#fff;border-radius:10px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.08);">
              <div style="display:flex;align-items:center;justify-content:space-between;">
                <span style="font-weight:600;font-size:15px;">${entry.name}</span>
                <div>
                  <button onclick="showEditWritingStyleModal('${entry.id}')" style="background:#f0f0f0;border:none;border-radius:5px;padding:5px 12px;cursor:pointer;margin-right:6px;font-size:13px;">编辑</button>
                  <button onclick="deleteWritingStyleEntry('${entry.id}')" style="background:#ff4d4f;color:#fff;border:none;border-radius:5px;padding:5px 12px;cursor:pointer;font-size:13px;">删除</button>
                </div>
              </div>
              <div style="margin-top:8px;color:#666;font-size:13px;line-height:1.5;max-height:60px;overflow:hidden;text-overflow:ellipsis;">${entry.content.substring(0, 120)}${entry.content.length > 120 ? '...' : ''}</div>
            </div>
          `).join('')
        }
      </div>
    </div>
  `;
}

function showAddWritingStyleModal(editId) {
  const existing = editId ? writingStyleEntries.find(e => e.id === editId) : null;
  const modal = document.createElement('div');
  modal.id = 'ws-modal';
  modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';
  modal.innerHTML = `
    <div style="background:#fff;border-radius:12px;padding:20px;width:90%;max-width:500px;max-height:80vh;display:flex;flex-direction:column;">
      <h3 style="margin:0 0 16px 0;font-size:17px;">${existing ? '编辑文风' : '新增文风'}</h3>
      <label style="font-size:13px;color:#666;margin-bottom:4px;">文风名称</label>
      <input id="ws-name-input" value="${existing ? existing.name : ''}" placeholder="请输入文风名称" style="border:1px solid #ddd;border-radius:6px;padding:8px 12px;margin-bottom:12px;font-size:14px;outline:none;" />
      <label style="font-size:13px;color:#666;margin-bottom:4px;">文风内容（详细描述文风规范）</label>
      <textarea id="ws-content-input" placeholder="请输入详细的文风描述和行为规范..." style="border:1px solid #ddd;border-radius:6px;padding:8px 12px;font-size:14px;line-height:1.6;resize:vertical;min-height:200px;outline:none;flex:1;">${existing ? existing.content : ''}</textarea>
      <div style="display:flex;justify-content:flex-end;margin-top:16px;gap:10px;">
        <button onclick="document.getElementById('ws-modal').remove()" style="background:#f0f0f0;border:none;border-radius:6px;padding:9px 20px;cursor:pointer;font-size:14px;">取消</button>
        <button onclick="saveWritingStyleModal('${editId || ''}')" style="background:#07c160;color:#fff;border:none;border-radius:6px;padding:9px 20px;cursor:pointer;font-size:14px;">保存</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

function showEditWritingStyleModal(id) {
  showAddWritingStyleModal(id);
}

async function saveWritingStyleModal(editId) {
  const name = document.getElementById('ws-name-input').value.trim();
  const content = document.getElementById('ws-content-input').value.trim();
  if (!name) { alert('请输入文风名称'); return; }
  if (!content) { alert('请输入文风内容'); return; }
  
  await loadWritingStyleEntries();
  if (editId) {
    const idx = writingStyleEntries.findIndex(e => e.id === editId);
    if (idx >= 0) {
      writingStyleEntries[idx] = { ...writingStyleEntries[idx], name, content, updatedAt: Date.now() };
    }
  } else {
    writingStyleEntries.push({ id: generateWritingStyleId(), name, content, createdAt: Date.now(), updatedAt: Date.now() });
  }
  await saveWritingStyleEntries();
  document.getElementById('ws-modal').remove();
  await showWritingStylePage();
}

async function deleteWritingStyleEntry(id) {
  if (!confirm('确定删除该文风条目吗？')) return;
  await loadWritingStyleEntries();
  writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
  await saveWritingStyleEntries();
  await showWritingStylePage();
}

// ═══════════════════════════════════════════════════════════════════
// 文风单选 for chat settings
// ═══════════════════════════════════════════════════════════════════

async function getWritingStyleOptions() {
  await loadWritingStyleEntries();
  return writingStyleEntries;
}

async function getContactWritingStyle(contactId) {
  const key = 'CONTACT_WRITING_STYLE_' + contactId;
  const raw = await getFromStorage(key);
  return raw ? (typeof raw === 'string' ? JSON.parse(raw) : raw) : { styleId: '', compressedStyle: '' };
}

async function saveContactWritingStyle(contactId, styleId, compressedStyle) {
  const key = 'CONTACT_WRITING_STYLE_' + contactId;
  await saveToStorage(key, JSON.stringify({ styleId, compressedStyle }));
}

async function compressWritingStyle(content) {
  // Call AI API to compress the writing style to ~50 chars
  const systemPrompt = '你是一个文本压缩助手。请将以下文风规范压缩成一句话的行为准则，不超过50个字，直接输出压缩后的内容，不要任何前缀或解释。';
  try {
    const apiKey = await getFromStorage('API_KEY') || window.currentApiKey || '';
    const apiUrl = await getFromStorage('API_URL') || window.currentApiUrl || 'https://api.openai.com/v1/chat/completions';
    const model = await getFromStorage('API_MODEL') || window.currentModel || 'gpt-3.5-turbo';
    
    if (!apiKey) {
      console.warn('No API key for writing style compression');
      return content.substring(0, 50);
    }
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apiKey },
      body: JSON.stringify({
        model: model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: content }
        ],
        max_tokens: 100,
        temperature: 0.3
      })
    });
    
    if (!response.ok) throw new Error('API error: ' + response.status);
    const data = await response.json();
    return data.choices[0].message.content.trim();
  } catch (err) {
    console.error('Writing style compression failed:', err);
    return content.substring(0, 50);
  }
}

async function onWritingStyleSelected(contactId, styleId) {
  if (!styleId) {
    await saveContactWritingStyle(contactId, '', '');
    return;
  }
  
  await loadWritingStyleEntries();
  const entry = writingStyleEntries.find(e => e.id === styleId);
  if (!entry) return;
  
  // Show loading indicator
  const btn = document.getElementById('ws-select-status');
  if (btn) btn.textContent = '正在压缩文风…';
  
  const compressed = await compressWritingStyle(entry.content);
  await saveContactWritingStyle(contactId, styleId, compressed);
  
  if (btn) btn.textContent = '✓ 文风已设置: ' + compressed.substring(0, 20) + '…';
  console.log('[WritingStyle] Compressed style saved for contact', contactId, ':', compressed);
}

function getWritingStyleTailInstruction(compressedStyle) {
  if (!compressedStyle) return '';
  return '\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：' + compressedStyle + ')';
}

"""

# Insert writing style JS before the last closing lines or at the end
# Find a good injection point - before the DOMContentLoaded or at the end before final comment
injection_marker = '// End of main.js'
if injection_marker in js:
    js = js.replace(injection_marker, WRITING_STYLE_JS + '\n' + injection_marker)
    changes_made.append('JS: Injected writing style module before end marker')
else:
    # Inject before the last occurrence of a major function or at the end
    js = js + '\n' + WRITING_STYLE_JS
    changes_made.append('JS: Appended writing style module to end of main.js')

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: Inject writing style tail into user message building
# Find where user message content is assembled for API call
# ═══════════════════════════════════════════════════════════════════════════

# Look for patterns where the final user message is built for API
# Common patterns: messages.push({role:'user', content: ...}) or similar
# We need to inject the writing style tail into the last user message

# Try to find the API call construction to inject the tail
inject_tail_code = """
  // Inject writing style tail instruction
  try {
    const currentContactId = window.currentChatContact || window.selectedContact;
    if (currentContactId) {
      const wsData = await getContactWritingStyle(currentContactId);
      if (wsData && wsData.compressedStyle) {
        const tail = getWritingStyleTailInstruction(wsData.compressedStyle);
        if (tail && messages && messages.length > 0) {
          // Find last user message and append tail
          for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].role === 'user') {
              messages[i] = { ...messages[i], content: messages[i].content + tail };
              break;
            }
          }
        }
      }
    }
  } catch (wsErr) {
    console.warn('Writing style tail injection error:', wsErr);
  }
"""

# Find the API call site - look for fetch call with messages
api_call_patterns = [
    "const response = await fetch(apiUrl",
    "const response = await fetch(API_URL",
    "await fetch(apiUrl, {",
]

injected_tail = False
for pattern in api_call_patterns:
    if pattern in js and not injected_tail:
        js = js.replace(pattern, inject_tail_code + '\n  ' + pattern, 1)
        changes_made.append(f'JS: Injected writing style tail before API fetch call')
        injected_tail = True
        break

if not injected_tail:
    changes_made.append('JS: WARNING - could not find API fetch call for tail injection, manual needed')

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3+4: Add Writing Style to contacts menu (HTML) and chat settings
# ═══════════════════════════════════════════════════════════════════════════

# Add 文风设置 to contacts menu in HTML
ws_menu_item = '''        <div class="contacts-menu-item" onclick="showWritingStylePage()" style="display:flex;align-items:center;padding:14px 16px;cursor:pointer;border-bottom:1px solid #f0f0f0;">
          <span style="font-size:22px;margin-right:12px;">✍️</span>
          <span style="font-size:15px;">文风设置</span>
          <span style="margin-left:auto;color:#ccc;">›</span>
        </div>'''

# Look for worldbook menu item to insert after it
worldbook_menu_patterns = [
    'showWorldBookPage()',
    'worldbook-menu',
    '世界书',
]

menu_inserted = False
for pattern in worldbook_menu_patterns:
    if pattern in html and not menu_inserted:
        # Find the closing </div> after this pattern
        idx = html.find(pattern)
        if idx >= 0:
            # Find the end of this menu item's div
            end_div = html.find('</div>', idx)
            if end_div >= 0:
                insert_pos = end_div + len('</div>')
                html = html[:insert_pos] + '\n' + ws_menu_item + html[insert_pos:]
                changes_made.append('HTML: Added 文风设置 menu item after 世界书 menu item')
                menu_inserted = True

if not menu_inserted:
    changes_made.append('HTML: WARNING - could not find worldbook menu item to insert after')

# Add writing style selector to chat settings
chat_settings_ws_html = """
          <!-- 文风设置选择器 -->
          <div class="chat-setting-section" style="padding:14px 16px;border-bottom:1px solid #f5f5f5;">
            <div style="font-size:15px;font-weight:600;margin-bottom:8px;">当前聊天文风</div>
            <div style="background:#fff7e6;border:1px solid #ffd591;border-radius:6px;padding:8px 12px;margin-bottom:10px;font-size:12px;color:#d46b08;">
              ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
            </div>
            <select id="writing-style-select" onchange="handleWritingStyleChange(this.value)" style="width:100%;border:1px solid #ddd;border-radius:6px;padding:8px 12px;font-size:14px;background:#fff;outline:none;">
              <option value="">── 不使用文风 ──</option>
            </select>
            <div id="ws-select-status" style="margin-top:6px;font-size:12px;color:#07c160;min-height:18px;"></div>
          </div>"""

# Find chat settings modal/panel
chat_settings_patterns = [
    'chat-settings-panel',
    'id="chat-settings"',
    'chatSettingsModal',
    '聊天设置',
]

settings_inserted = False
for pattern in chat_settings_patterns:
    if pattern in html and not settings_inserted:
        idx = html.find(pattern)
        if idx >= 0:
            # Find the next div close and insert after the header
            next_div = html.find('>', idx)
            if next_div >= 0:
                insert_pos = next_div + 1
                html = html[:insert_pos] + chat_settings_ws_html + html[insert_pos:]
                changes_made.append('HTML: Added writing style selector to chat settings')
                settings_inserted = True

if not settings_inserted:
    changes_made.append('HTML: WARNING - could not find chat settings panel for writing style selector')

# ═══════════════════════════════════════════════════════════════════════════
# Add JS handler for writing style change in chat settings
# ═══════════════════════════════════════════════════════════════════════════

CHAT_SETTINGS_WS_JS = """
async function handleWritingStyleChange(styleId) {
  const contactId = window.currentChatContact || window.selectedContact;
  if (!contactId) return;
  await onWritingStyleSelected(contactId, styleId);
}

async function populateWritingStyleSelect(contactId) {
  const select = document.getElementById('writing-style-select');
  if (!select) return;
  const styles = await getWritingStyleOptions();
  const current = await getContactWritingStyle(contactId);
  
  // Clear and repopulate
  select.innerHTML = '<option value="">── 不使用文风 ──</option>';
  styles.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.id;
    opt.textContent = s.name;
    if (current.styleId === s.id) opt.selected = true;
    select.appendChild(opt);
  });
  
  const statusEl = document.getElementById('ws-select-status');
  if (statusEl && current.compressedStyle) {
    statusEl.textContent = '✓ 当前文风: ' + current.compressedStyle.substring(0, 25) + '…';
  }
}
"""

js = js + '\n' + CHAT_SETTINGS_WS_JS
changes_made.append('JS: Added handleWritingStyleChange and populateWritingStyleSelect functions')

# ═══════════════════════════════════════════════════════════════════════════
# Write back files
# ═══════════════════════════════════════════════════════════════════════════

with open(MAIN_JS, 'w', encoding='utf-8') as f:
    f.write(js)
print(f'[OK] main.js written ({len(js)} chars)')

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'[OK] index.html written ({len(html)} chars)')

print('\n=== Changes Made ===')
for i, c in enumerate(changes_made, 1):
    print(f'{i}. {c}')

print('\n=== DONE ===')
print('Please manually verify:')
print('1. World book 记忆总结 trigger logic in getContactWorldBookPrompt()')
print('2. Writing style selector appears in chat settings UI')
print('3. 文风设置 appears in contacts menu')
print('4. Writing style tail appends to last user message before API call')
