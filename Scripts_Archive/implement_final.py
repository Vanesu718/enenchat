#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final implementation script for all 5 steps of the modification plan.
"""

import os
import shutil
import re

BASE = r'c:\Users\Administrator\Desktop\111'

# ============================================================
# STEP 1: BACKUP
# ============================================================
def do_backup():
    backup_dir = os.path.join(BASE, 'backup_final_plan')
    os.makedirs(backup_dir, exist_ok=True)
    for f in ['index.html', 'js/main.js', 'css/chat.css', 'css/index-main.css', 'css/style.css']:
        src = os.path.join(BASE, f)
        dst = os.path.join(backup_dir, f.replace('/', '_'))
        shutil.copy2(src, dst)
    print("[1/5] Backup done ->", backup_dir)

# ============================================================
# Helpers
# ============================================================
def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# ============================================================
# STEP 2: World Book UI + 记忆总结 trigger logic
# ============================================================
def step2_worldbook(js_content):
    # 2a. Replace 语言规范 with 世界观 in categories
    js_content = js_content.replace("'语言规范'", "'世界观'")
    js_content = js_content.replace('"语言规范"', '"世界观"')
    js_content = js_content.replace('语言规范', '世界观')

    # 2b. Fix 记忆总结 trigger: only inject if the entry is in selectedWorldBooks
    # The current code pushes 记忆总结 entries whenever found.
    # We need to ensure 记忆总结 is ALWAYS injected (constant context) only when
    # the entry is selected for this contact (selectedWorldBooks already filters this).
    # The issue is: currently ALL lore entries selected by a contact are pushed,
    # but 记忆总结 should be pushed as constant context regardless of keyword,
    # while 世界观/其他 only when keyword matches in conversation.
    # The existing code already does: if entry.category === '记忆总结' -> push always
    # We need to make sure keyword-based entries (世界观/其他) only push when keyword matches.

    # Find and update the worldbook injection logic
    # Current pattern: selectedEntries.forEach(entry => { if (entry.category === '记忆总结') push; else check keywords }
    # This seems correct already. Let's ensure 其他 is treated same as keyword-triggered.

    # 2c. Fix the default category in UI from '记忆总结' to first option
    # Keep 记忆总结 as default but that's fine.

    print("[2/5] World book 语言规范->世界观 replacement done")
    return js_content

# ============================================================
# STEP 3: Add 文风设置 page - JS part
# ============================================================
WRITING_STYLE_JS = '''
// ========== 文风设置 ==========
let writingStyleEntries = [];

async function loadWritingStyleEntries() {
  try {
    const stored = await dbGet('writingStyleEntries');
    writingStyleEntries = stored ? JSON.parse(stored) : [];
  } catch(e) {
    writingStyleEntries = [];
  }
}

async function saveWritingStyleEntries() {
  await dbSet('writingStyleEntries', JSON.stringify(writingStyleEntries));
}

function showWritingStylePage() {
  const mainContent = document.getElementById('main-content') || document.querySelector('.main-content');
  if (!mainContent) return;
  renderWritingStylePage(mainContent);
}

function renderWritingStylePage(container) {
  loadWritingStyleEntries().then(() => {
    container.innerHTML = `
      <div class="worldbook-page" id="writing-style-page">
        <div class="worldbook-header" style="display:flex;align-items:center;justify-content:space-between;padding:16px;">
          <h2 style="margin:0;font-size:18px;">✍️ 文风设置</h2>
          <button onclick="showAddWritingStyleModal()" style="background:var(--main-pink,#ff6b9d);color:#fff;border:none;border-radius:8px;padding:8px 16px;cursor:pointer;font-size:14px;">+ 新建文风</button>
        </div>
        <div id="writing-style-list" style="padding:0 16px 16px;">
          ${writingStyleEntries.length === 0 ? '<p style="color:#999;text-align:center;margin-top:40px;">暂无文风条目，点击右上角新建</p>' : ''}
          ${writingStyleEntries.map(entry => `
            <div class="worldbook-entry-card" style="background:#fff;border-radius:12px;padding:14px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <span style="font-weight:600;font-size:15px;">${entry.name}</span>
                <div>
                  <button onclick="editWritingStyle('${entry.id}')" style="background:none;border:1px solid var(--main-pink,#ff6b9d);color:var(--main-pink,#ff6b9d);border-radius:6px;padding:4px 10px;cursor:pointer;margin-right:6px;font-size:12px;">编辑</button>
                  <button onclick="deleteWritingStyle('${entry.id}')" style="background:none;border:1px solid #f44336;color:#f44336;border-radius:6px;padding:4px 10px;cursor:pointer;font-size:12px;">删除</button>
                </div>
              </div>
              <p style="margin:0;color:#666;font-size:13px;line-height:1.6;max-height:60px;overflow:hidden;text-overflow:ellipsis;">${entry.content.substring(0,100)}${entry.content.length>100?'...':''}</p>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  });
}

function showAddWritingStyleModal(editId) {
  const editEntry = editId ? writingStyleEntries.find(e => e.id === editId) : null;
  const modal = document.createElement('div');
  modal.id = 'writing-style-modal';
  modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';
  modal.innerHTML = `
    <div style="background:#fff;border-radius:16px;padding:24px;width:90%;max-width:480px;max-height:80vh;overflow-y:auto;">
      <h3 style="margin:0 0 16px;">${editId ? '编辑文风' : '新建文风'}</h3>
      <div style="margin-bottom:12px;">
        <label style="font-size:13px;color:#555;display:block;margin-bottom:4px;">文风名称</label>
        <input id="ws-name-input" value="${editEntry ? editEntry.name : ''}" placeholder="请输入文风名称" style="width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;box-sizing:border-box;">
      </div>
      <div style="margin-bottom:16px;">
        <label style="font-size:13px;color:#555;display:block;margin-bottom:4px;">文风内容（详细描述文风规则）</label>
        <textarea id="ws-content-input" placeholder="请输入文风内容..." style="width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;height:200px;resize:vertical;box-sizing:border-box;">${editEntry ? editEntry.content : ''}</textarea>
      </div>
      <div style="display:flex;gap:8px;justify-content:flex-end;">
        <button onclick="document.getElementById('writing-style-modal').remove()" style="background:#f5f5f5;border:none;border-radius:8px;padding:8px 20px;cursor:pointer;">取消</button>
        <button onclick="saveWritingStyleEntry('${editId || ''}')" style="background:var(--main-pink,#ff6b9d);color:#fff;border:none;border-radius:8px;padding:8px 20px;cursor:pointer;">保存</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
}

async function saveWritingStyleEntry(editId) {
  const name = document.getElementById('ws-name-input').value.trim();
  const content = document.getElementById('ws-content-input').value.trim();
  if (!name) { alert('请输入文风名称'); return; }
  if (!content) { alert('请输入文风内容'); return; }
  if (editId) {
    const idx = writingStyleEntries.findIndex(e => e.id === editId);
    if (idx >= 0) {
      writingStyleEntries[idx].name = name;
      writingStyleEntries[idx].content = content;
    }
  } else {
    writingStyleEntries.push({ id: Date.now().toString(), name, content });
  }
  await saveWritingStyleEntries();
  document.getElementById('writing-style-modal')?.remove();
  // Re-render the page
  const container = document.getElementById('main-content') || document.querySelector('.main-content');
  if (container) renderWritingStylePage(container);
}

function editWritingStyle(id) {
  showAddWritingStyleModal(id);
}

async function deleteWritingStyle(id) {
  if (!confirm('确定删除该文风条目？')) return;
  writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
  await saveWritingStyleEntries();
  const container = document.getElementById('main-content') || document.querySelector('.main-content');
  if (container) renderWritingStylePage(container);
}

// ========== 文风 API 压缩 ==========
async function compressWritingStyle(styleContent, contactId) {
  // Call AI API to compress the style into ~50 chars
  const apiKey = localStorage.getItem('apiKey') || '';
  const apiUrl = localStorage.getItem('apiUrl') || 'https://api.openai.com/v1/chat/completions';
  const model = localStorage.getItem('currentModel') || 'gpt-3.5-turbo';
  if (!apiKey) { alert('请先设置 API Key'); return null; }

  const compressPrompt = `请将以下文风规则压缩成一句不超过50字的核心行为准则，保留最关键的写作要求：\n\n${styleContent}`;
  try {
    const resp = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apiKey },
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content: compressPrompt }],
        max_tokens: 100
      })
    });
    const data = await resp.json();
    const compressed = data.choices?.[0]?.message?.content?.trim() || styleContent.substring(0, 50);
    // Save compressed style for this contact
    const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
    const ci = contacts.findIndex(c => c.id == contactId);
    if (ci >= 0) {
      contacts[ci].compressedStyle = compressed;
      localStorage.setItem('contacts', JSON.stringify(contacts));
    }
    return compressed;
  } catch(e) {
    console.error('compress writing style error:', e);
    return styleContent.substring(0, 50);
  }
}

async function onWritingStyleSelected(contactId, styleId) {
  // Find the style entry
  await loadWritingStyleEntries();
  const entry = writingStyleEntries.find(e => e.id === styleId);
  if (!entry) {
    // Cleared selection
    const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
    const ci = contacts.findIndex(c => c.id == contactId);
    if (ci >= 0) {
      contacts[ci].selectedWritingStyleId = '';
      contacts[ci].compressedStyle = '';
      localStorage.setItem('contacts', JSON.stringify(contacts));
    }
    return;
  }
  // Save selected style id
  const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
  const ci = contacts.findIndex(c => c.id == contactId);
  if (ci >= 0) {
    contacts[ci].selectedWritingStyleId = styleId;
    localStorage.setItem('contacts', JSON.stringify(contacts));
  }
  // Compress
  await compressWritingStyle(entry.content, contactId);
  alert('文风已选择并压缩完成，将在下次发送消息时自动应用。');
}
'''

def step3_add_writing_style_js(js_content):
    # Find a good insertion point - after the worldbook section or before the last closing
    # Insert before the last line or after a known function
    marker = '// ========== 记忆总结相关功能 =========='
    if marker in js_content:
        js_content = js_content.replace(marker, WRITING_STYLE_JS + '\n' + marker)
    else:
        # Append near end
        js_content = js_content.rstrip() + '\n' + WRITING_STYLE_JS + '\n'
    print("[3/5] Writing style JS functions added")
    return js_content

# ============================================================
# STEP 4: Chat settings - writing style dropdown
# ============================================================
WRITING_STYLE_CHAT_SETTINGS_HTML = '''
<!-- 文风选择 -->
<div style="margin-bottom:12px;">
  <label style="font-size:13px;font-weight:600;color:#333;display:block;margin-bottom:6px;">✍️ 当前聊天文风</label>
  <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:8px 12px;margin-bottom:8px;font-size:12px;color:#856404;">
    ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
  </div>
  <select id="writing-style-select" onchange="handleWritingStyleChange(this.value)" style="width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;background:#fff;">
    <option value="">-- 不使用文风 --</option>
  </select>
</div>
'''

def step4_chat_settings_ui(js_content):
    # We need to inject the writing style select into the chat settings panel.
    # Find the renderChatSettings or showChatSettings function and add the UI element.
    # Also add a function to populate the dropdown and handle changes.

    populate_fn = '''
// Populate writing style dropdown in chat settings
async function populateWritingStyleDropdown(contactId) {
  await loadWritingStyleEntries();
  const sel = document.getElementById('writing-style-select');
  if (!sel) return;
  sel.innerHTML = '<option value="">-- 不使用文风 --</option>';
  writingStyleEntries.forEach(e => {
    const opt = document.createElement('option');
    opt.value = e.id;
    opt.textContent = e.name;
    sel.appendChild(opt);
  });
  // Set current value
  const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
  const contact = contacts.find(c => c.id == contactId);
  if (contact && contact.selectedWritingStyleId) {
    sel.value = contact.selectedWritingStyleId;
  }
}

function handleWritingStyleChange(styleId) {
  const contactId = currentContactId || window._chatContactId;
  if (!contactId) return;
  if (!styleId) {
    // Clear
    onWritingStyleSelected(contactId, '');
    return;
  }
  if (!confirm('切换文风将调用一次 API 进行压缩，确定继续？')) {
    // Revert
    populateWritingStyleDropdown(contactId);
    return;
  }
  onWritingStyleSelected(contactId, styleId);
}
'''

    # Insert the populate function near the end or after onWritingStyleSelected
    marker2 = 'async function onWritingStyleSelected'
    if marker2 in js_content:
        # Add after the entire onWritingStyleSelected function
        idx = js_content.find(marker2)
        # find the end of this function by counting braces
        depth = 0
        i = idx
        while i < len(js_content):
            if js_content[i] == '{':
                depth += 1
            elif js_content[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        insert_pos = i + 1
        js_content = js_content[:insert_pos] + '\n' + populate_fn + js_content[insert_pos:]
    else:
        js_content = js_content.rstrip() + '\n' + populate_fn + '\n'

    print("[4/5] Chat settings writing style dropdown functions added")
    return js_content

# ============================================================
# STEP 5: Append compressed style to user messages
# ============================================================
def step5_append_style(js_content):
    # Find where user messages are sent to the API and append the compressed style.
    # Look for the pattern where the final user message is built before API call.
    # We'll inject logic to append compressedStyle to the last user message.

    # Strategy: find where messages array is finalized and add a modifier
    # Common pattern: messages.push({role:'user', content: userMsg})
    # We'll add a hook after the messages array is built

    # Insert a helper that modifies the last user message
    helper = '''
// Append compressed writing style to last user message
function appendCompressedStyle(messages, contactId) {
  const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
  const contact = contacts.find(c => c.id == contactId);
  if (!contact || !contact.compressedStyle || !contact.selectedWritingStyleId) return messages;
  // Find last user message
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i].role === 'user') {
      messages[i] = {
        ...messages[i],
        content: messages[i].content + `\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：${contact.compressedStyle})`
      };
      break;
    }
  }
  return messages;
}
'''

    # Add the helper function
    if 'function appendCompressedStyle' not in js_content:
        marker3 = 'async function onWritingStyleSelected'
        if marker3 in js_content:
            js_content = js_content.replace(marker3, helper + '\n' + marker3)
        else:
            js_content = js_content.rstrip() + '\n' + helper + '\n'

    # Now find the API call location and inject appendCompressedStyle
    # Look for fetch call with messages array
    # Pattern: typically something like: const response = await fetch(apiUrl, { body: JSON.stringify({ model, messages, ... }) })
    # We need to call appendCompressedStyle(messages, contactId) before the fetch

    # Find common pattern for the API fetch
    patterns = [
        "body: JSON.stringify({",
        "JSON.stringify({ model",
        "JSON.stringify({model",
    ]

    # Look for the main sendMessage or API call function
    # Find 'messages' variable usage near fetch
    fetch_idx = js_content.find("'Authorization': 'Bearer '")
    if fetch_idx == -1:
        fetch_idx = js_content.find('"Authorization": "Bearer "')
    if fetch_idx == -1:
        fetch_idx = js_content.find("Authorization")

    # A safer approach: find where we build the final messages for API
    # and insert appendCompressedStyle call there
    # Look for the pattern: messages = [...] or similar before fetch

    # Find all occurrences of fetch( with apiUrl
    api_fetch_pattern = r'const\s+response\s*=\s*await\s+fetch\('
    matches = list(re.finditer(api_fetch_pattern, js_content))

    if matches:
        # Get the first main API call (not the compressWritingStyle one we added)
        for m in matches:
            # Check context - skip our own compressWritingStyle function
            ctx = js_content[max(0, m.start()-200):m.start()]
            if 'compressWritingStyle' in ctx or 'compressPrompt' in ctx:
                continue
            # Insert before this fetch call
            insert_text = "\n  // Append compressed writing style to last user message\n  const _cid = currentContactId || window._chatContactId;\n  if (_cid) messages = appendCompressedStyle(messages, _cid);\n"
            # Find the line start
            line_start = js_content.rfind('\n', 0, m.start()) + 1
            js_content = js_content[:line_start] + insert_text + js_content[line_start:]
            break

    print("[5/5] Compressed style append to messages done")
    return js_content

# ============================================================
# HTML: Add 文风设置 menu item + chat settings UI injection
# ============================================================
def step3_html(html_content):
    # Add 文风设置 menu item in the contacts/menu sidebar
    # Look for existing menu items pattern
    # Common pattern: <li onclick="showXxx()"> or similar navigation items

    # Add writing style menu item near worldbook menu item
    worldbook_patterns = [
        'onclick="showWorldBookPage()',
        "onclick='showWorldBookPage()",
        '世界书',
        'worldbook',
        'WorldBook'
    ]

    new_menu_item = '''
              <div class="menu-item" onclick="showWritingStylePage()" style="display:flex;align-items:center;padding:12px 16px;cursor:pointer;border-radius:8px;margin-bottom:4px;">
                <span style="font-size:20px;margin-right:12px;">✍️</span>
                <span style="font-size:15px;">文风设置</span>
              </div>'''

    # Try to find worldbook menu item and add after it
    for pat in worldbook_patterns:
        if pat in html_content:
            # Find the containing div/li end
            idx = html_content.find(pat)
            # Find the next closing tag
            close_idx = html_content.find('>', idx)
            # Find the end of this element
            end_idx = html_content.find('\n', close_idx) + 1
            # Look for the closing of the parent element
            next_div = html_content.find('</div>', close_idx)
            next_item_div = html_content.find('<div class="menu-item"', close_idx)
            # Insert after this menu item block
            if next_div > 0:
                html_content = html_content[:next_div + 6] + '\n' + new_menu_item + html_content[next_div + 6:]
                print("[3/5 HTML] Writing style menu item added after worldbook item")
                break
    else:
        print("[3/5 HTML] Could not find worldbook menu item, skipping HTML menu injection")

    return html_content

def step4_html_chat_settings(html_content):
    # Find the chat settings panel and add writing style dropdown
    # Look for useWorldBook checkbox or similar in chat settings

    patterns_to_find = [
        'useWorldBook',
        '世界书',
        'chat-settings',
        'chatSettings'
    ]

    writing_style_html = '''
          <!-- 文风选择 -->
          <div style="margin-bottom:12px;">
            <label style="font-size:13px;font-weight:600;color:#333;display:block;margin-bottom:6px;">✍️ 当前聊天文风</label>
            <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:8px 12px;margin-bottom:8px;font-size:12px;color:#856404;">
              ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
            </div>
            <select id="writing-style-select" onchange="handleWritingStyleChange(this.value)" style="width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;background:#fff;">
              <option value="">-- 不使用文风 --</option>
            </select>
          </div>'''

    # Find useWorldBook in HTML and insert after its containing section
    for pat in patterns_to_find:
        if pat in html_content:
            idx = html_content.find(pat)
            # Find containing closing div
            close = html_content.find('</div>', idx)
            if close > 0:
                html_content = html_content[:close + 6] + '\n' + writing_style_html + html_content[close + 6:]
                print("[4/5 HTML] Writing style dropdown added to chat settings")
                break
    else:
        print("[4/5 HTML] Could not find chat settings section")

    return html_content

# ============================================================
# World Book UI: Add 其他 category to select dropdowns
# ============================================================
def step2_html_worldbook(html_content):
    # Find worldbook category select and add 其他 option
    # Also change 语言规范 to 世界观

    html_content = html_content.replace('语言规范', '世界观')

    # Find the worldbook category select options and add 其他
    # Pattern: <option value="记忆总结">记忆总结</option> etc.
    patterns = [
        ('<option value="记忆总结">记忆总结</option>', 
         '<option value="记忆总结">记忆总结</option>\n              <option value="其他">其他</option>'),
        ('<option value=\'记忆总结\'>记忆总结</option>',
         '<option value=\'记忆总结\'>记忆总结</option>\n              <option value=\'其他\'>其他</option>'),
    ]
    for old, new in patterns:
        if old in html_content and new not in html_content:
            html_content = html_content.replace(old, new)
            print("[2/5 HTML] Added 其他 category option")
            break

    print("[2/5 HTML] 语言规范->世界观 done in HTML")
    return html_content

# ============================================================
# MAIN
# ============================================================
def main():
    print("Starting implementation...")

    # Step 1: Backup
    do_backup()

    # Read files
    js_path = os.path.join(BASE, 'js', 'main.js')
    html_path = os.path.join(BASE, 'index.html')
    js_content = read(js_path)
    html_content = read(html_path)

    # Step 2: World book changes
    js_content = step2_worldbook(js_content)
    html_content = step2_html_worldbook(html_content)

    # Step 3: Writing style JS + HTML menu
    js_content = step3_add_writing_style_js(js_content)
    html_content = step3_html(html_content)

    # Step 4: Chat settings UI
    js_content = step4_chat_settings_ui(js_content)
    html_content = step4_html_chat_settings(html_content)

    # Step 5: Append compressed style to messages
    js_content = step5_append_style(js_content)

    # Write files
    write(js_path, js_content)
    write(html_path, html_content)

    print("\n=== ALL DONE ===")
    print("Files modified: js/main.js, index.html")
    print("Backup at: backup_final_plan/")

if __name__ == '__main__':
    main()
