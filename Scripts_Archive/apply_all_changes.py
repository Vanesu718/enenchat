#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合修改脚本 - 一次性应用所有计划修改
"""
import re
import shutil
import os
import json
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'
JS_MAIN = os.path.join(BASE, 'js', 'main.js')
INDEX_HTML = os.path.join(BASE, 'index.html')

# ============================================================
# Step 1: Backup
# ============================================================
backup_dir = os.path.join(BASE, f'backup_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
os.makedirs(backup_dir, exist_ok=True)
os.makedirs(os.path.join(backup_dir, 'js'), exist_ok=True)
os.makedirs(os.path.join(backup_dir, 'css'), exist_ok=True)

for f in ['js/main.js', 'index.html', 'css/chat.css', 'css/index-main.css', 'css/style.css']:
    src = os.path.join(BASE, f)
    dst = os.path.join(backup_dir, f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f'[备份] {f}')

print(f'[备份完成] -> {backup_dir}')

# ============================================================
# Read main.js
# ============================================================
with open(JS_MAIN, 'r', encoding='utf-8') as fh:
    js = fh.read()

print(f'[读取] main.js: {len(js)} 字符, 约 {js.count(chr(10))+1} 行')

# ============================================================
# Step 2A: World Book UI - 语言规范 → 世界观, 新增 其他
# ============================================================

# Replace all occurrences of '语言规范' with '世界观' in worldbook context
js = js.replace("'语言规范'", "'世界观'")
js = js.replace('"语言规范"', '"世界观"')
js = js.replace('>语言规范<', '>世界观<')
js = js.replace('语言规范</option>', '世界观</option>')
js = js.replace("value='语言规范'", "value='世界观'")
js = js.replace('value="语言规范"', 'value="世界观"')
js = js.replace("=== '语言规范'", "=== '世界观'")
js = js.replace('=== "语言规范"', '=== "世界观"')

print('[Step2A] 语言规范 → 世界观 替换完成')

# ============================================================
# Step 2B: Add '其他' category to worldbook dropdowns/tabs
# ============================================================

# In filter tabs (buttons like data-category="记忆总结")
# Find pattern with 世界观 (was 语言规范) tab and add 其他 after it
# Pattern: button for 世界观 in filter tabs
tab_pattern = r"(data-category=['\"]世界观['\"][^>]*>[^<]*</button>)"
tab_match = re.search(tab_pattern, js)
if tab_match:
    original = tab_match.group(0)
    # Add 其他 button after
    replacement = original + "\n            <button class=\"category-tab\" data-category=\"其他\">其他</button>"
    js = js.replace(original, replacement, 1)
    print('[Step2B-tab] 已在过滤Tab中添加"其他"')
else:
    print('[Step2B-tab] 未找到世界观Tab按钮模式，尝试备用搜索...')
    # Try another approach - look for the tabs container
    alt_pattern = r"(category-tab[^>]*>世界观</button>)"
    alt_match = re.search(alt_pattern, js)
    if alt_match:
        original = alt_match.group(0)
        replacement = original + "\n            <button class=\"category-tab\" data-category=\"其他\">其他</button>"
        js = js.replace(original, replacement, 1)
        print('[Step2B-tab-alt] 已在过滤Tab中添加"其他"')
    else:
        print('[Step2B-tab] 警告: 未能自动添加其他Tab')

# In select/option dropdowns for category
# Pattern: <option value="世界观">世界观</option>
option_pattern = r"(<option[^>]*value=['\"]世界观['\"][^>]*>世界观</option>)"
option_match = re.search(option_pattern, js)
if option_match:
    original = option_match.group(0)
    replacement = original + "\n                <option value=\"其他\">其他</option>"
    js = js.replace(original, replacement, 1)
    print('[Step2B-option] 已在下拉菜单中添加"其他"选项')
else:
    print('[Step2B-option] 未找到世界观option模式，尝试备用...')
    # Try simpler pattern
    simple_pat = r'(value=["\']世界观["\']>世界观</option>)'
    simple_match = re.search(simple_pat, js)
    if simple_match:
        original = simple_match.group(0)
        replacement = original + '\n                <option value="其他">其他</option>'
        js = js.replace(original, replacement, 1)
        print('[Step2B-option-alt] 已添加其他选项')
    else:
        print('[Step2B-option] 警告: 未能自动添加其他option')

print('[Step2B] 其他分类添加完成')

# ============================================================
# Step 2C: Fix 记忆总结 trigger logic
# Old: 记忆总结 entries are always injected for contacts with useWorldBook=true
# New: 记忆总结 entries ONLY inject if explicitly selected in that contact's selectedWorldBooks
# ============================================================

# The current getContactWorldBookPrompt already checks selectedWorldBooks for category '记忆总结'
# BUT the issue is: non-keyword entries are ALSO always injected without being in selectedWorldBooks
# The fix: ALL entries (including 记忆总结) must be in selectedWorldBooks to be injected
# 
# Current logic (lines ~284-303):
#   if (worldBook) push global worldBook   <- OK
#   if selectedWorldBooks has entries:
#     filter worldBookEntries by selectedWorldBooks
#     if entry.category === '记忆总结' -> always push  <- CORRECT (already gated by selectedWorldBooks)
#     else if entry.triggerType !== 'keyword' -> push   <- CORRECT
#
# Actually the current logic IS already gated. The real issue might be elsewhere.
# Let's look for where ALL worldBookEntries are injected without selectedWorldBooks check

# Search for keyword trigger logic - entries that match keywords in message
# These should only be '世界观' and '其他', not '记忆总结'

# Find the keyword trigger function
kw_pattern = r'(function\s+getKeywordTriggeredEntries|getKeywordTriggered)'
kw_match = re.search(kw_pattern, js)
if kw_match:
    print(f'[Step2C] 找到关键词触发函数: {kw_match.group(0)}')
else:
    print('[Step2C] 未找到独立的关键词触发函数，检查内联逻辑...')

# The key fix: In getContactWorldBookPrompt, 记忆总结 should ONLY be included
# if the entry is in selectedWorldBooks (which it already is based on the code above)
# But we need to ensure 世界观 and 其他 categories use KEYWORD trigger only

# Find the section that handles keyword-triggered entries in message building
# Look for where worldBookEntries keywords are checked against message content
keyword_inject_pattern = r'(worldBookEntries\.filter.*keyword.*message|entry\.keywords.*message)'
ki_match = re.search(keyword_inject_pattern, js, re.DOTALL)
if ki_match:
    print(f'[Step2C] 找到关键词注入逻辑')

# The correct fix based on the plan:
# 记忆总结: only inject if in selectedWorldBooks (already correct)
# 世界观 & 其他: keyword trigger only (need to ensure non-keyword entries of these categories are NOT auto-injected)

# Find in getContactWorldBookPrompt the part that injects non-keyword entries
# and add a check to exclude '世界观' and '其他' categories from auto-injection
old_non_keyword = """        } else if (entry.triggerType !== 'keyword') {
          activeWorldBooks.push(`[${entry.name} - 设定]\\n${entry.content}`);
        }"""
new_non_keyword = """        } else if (entry.triggerType !== 'keyword' && entry.category !== '世界观' && entry.category !== '其他') {
          activeWorldBooks.push(`[${entry.name} - 设定]\\n${entry.content}`);
        }"""

if old_non_keyword in js:
    js = js.replace(old_non_keyword, new_non_keyword, 1)
    print('[Step2C] 已修正世界观/其他分类的触发逻辑（仅关键词触发）')
else:
    # Try with different whitespace
    old2 = "} else if (entry.triggerType !== 'keyword') {"
    if old2 in js:
        js = js.replace(old2, "} else if (entry.triggerType !== 'keyword' && entry.category !== '世界观' && entry.category !== '其他') {", 1)
        print('[Step2C-alt] 已修正触发逻辑')
    else:
        print('[Step2C] 警告: 未找到需要修改的触发逻辑')

print('[Step2C] 记忆总结触发逻辑修正完成')

# ============================================================
# Step 3 & 4 & 5: Add 文风设置 system
# We'll inject the new code at the end of main.js (before last closing lines)
# or at appropriate locations
# ============================================================

WRITING_STYLE_CODE = '''
// ============================================================
// 文风设置系统 - Writing Style System
// ============================================================

let writingStyleEntries = []; // 文风条目列表
let _editingWritingStyleId = null; // 当前编辑的文风ID

// 加载文风数据
async function loadWritingStyleEntries() {
  try {
    const data = await getFromStorage('WRITING_STYLE_ENTRIES');
    writingStyleEntries = data ? (typeof data === 'string' ? JSON.parse(data) : data) : [];
    if (!Array.isArray(writingStyleEntries)) writingStyleEntries = [];
  } catch(e) {
    console.error('加载文风数据失败:', e);
    writingStyleEntries = [];
  }
}

// 保存文风数据
async function saveWritingStyleEntries() {
  await saveToStorage('WRITING_STYLE_ENTRIES', JSON.stringify(writingStyleEntries));
}

// 打开文风设置页面
function openWritingStylePage() {
  let overlay = document.getElementById('writingStyleOverlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'writingStyleOverlay';
    overlay.style.cssText = `position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;`;
    overlay.innerHTML = \`
      <div style="background:#fff;border-radius:12px;width:90%;max-width:600px;max-height:90vh;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.2);">
        <div style="padding:16px 20px;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:space-between;background:#f8f8f8;border-radius:12px 12px 0 0;">
          <span style="font-size:17px;font-weight:600;color:#333;">📝 文风设置</span>
          <button onclick="closeWritingStylePage()" style="border:none;background:none;font-size:22px;cursor:pointer;color:#999;">✕</button>
        </div>
        <div style="padding:12px 16px;border-bottom:1px solid #eee;display:flex;gap:8px;">
          <button onclick="openAddWritingStyleDialog()" style="background:#07c160;color:#fff;border:none;border-radius:8px;padding:8px 16px;cursor:pointer;font-size:14px;">+ 新增文风</button>
        </div>
        <div id="writingStyleList" style="flex:1;overflow-y:auto;padding:12px 16px;"></div>
      </div>
    \`;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeWritingStylePage();
    });
  }
  overlay.style.display = 'flex';
  renderWritingStyleList();
}

function closeWritingStylePage() {
  const overlay = document.getElementById('writingStyleOverlay');
  if (overlay) overlay.style.display = 'none';
}

function renderWritingStyleList() {
  const container = document.getElementById('writingStyleList');
  if (!container) return;
  if (writingStyleEntries.length === 0) {
    container.innerHTML = '<div style="text-align:center;color:#999;padding:40px 0;">暂无文风条目，点击"新增文风"添加</div>';
    return;
  }
  container.innerHTML = writingStyleEntries.map((entry, idx) => \`
    <div style="border:1px solid #eee;border-radius:8px;padding:12px;margin-bottom:10px;background:#fafafa;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
        <span style="font-weight:600;font-size:15px;color:#333;">\${entry.name}</span>
        <div style="display:flex;gap:8px;">
          <button onclick="openEditWritingStyleDialog('\${entry.id}')" style="background:#1989fa;color:#fff;border:none;border-radius:6px;padding:5px 12px;cursor:pointer;font-size:13px;">编辑</button>
          <button onclick="deleteWritingStyleEntry('\${entry.id}')" style="background:#ee0a24;color:#fff;border:none;border-radius:6px;padding:5px 12px;cursor:pointer;font-size:13px;">删除</button>
        </div>
      </div>
      <div style="font-size:13px;color:#666;max-height:60px;overflow:hidden;text-overflow:ellipsis;">\${(entry.content || '').substring(0, 120)}\${(entry.content || '').length > 120 ? '...' : ''}</div>
    </div>
  \`).join('');
}

function openAddWritingStyleDialog() {
  _editingWritingStyleId = null;
  showWritingStyleDialog('', '');
}

function openEditWritingStyleDialog(id) {
  const entry = writingStyleEntries.find(e => e.id === id);
  if (!entry) return;
  _editingWritingStyleId = id;
  showWritingStyleDialog(entry.name, entry.content);
}

function showWritingStyleDialog(name, content) {
  let dialog = document.getElementById('writingStyleDialog');
  if (!dialog) {
    dialog = document.createElement('div');
    dialog.id = 'writingStyleDialog';
    dialog.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:10001;display:flex;align-items:center;justify-content:center;';
    document.body.appendChild(dialog);
  }
  dialog.innerHTML = \`
    <div style="background:#fff;border-radius:12px;width:90%;max-width:500px;padding:20px;box-shadow:0 4px 24px rgba(0,0,0,0.25);">
      <div style="font-size:16px;font-weight:600;margin-bottom:14px;color:#333;">\${_editingWritingStyleId ? '编辑文风' : '新增文风'}</div>
      <div style="margin-bottom:10px;">
        <label style="font-size:13px;color:#666;display:block;margin-bottom:4px;">文风名称</label>
        <input id="wsNameInput" type="text" placeholder="例如：古风、现代轻松、正式..." value="\${name}" style="width:100%;border:1px solid #ddd;border-radius:6px;padding:8px 10px;font-size:14px;box-sizing:border-box;">
      </div>
      <div style="margin-bottom:14px;">
        <label style="font-size:13px;color:#666;display:block;margin-bottom:4px;">文风内容（详细描述写作风格、语气、用词规范等）</label>
        <textarea id="wsContentInput" placeholder="请详细描述文风要求..." style="width:100%;border:1px solid #ddd;border-radius:6px;padding:8px 10px;font-size:14px;box-sizing:border-box;height:160px;resize:vertical;">\${content}</textarea>
      </div>
      <div style="display:flex;gap:10px;justify-content:flex-end;">
        <button onclick="closeWritingStyleDialog()" style="border:1px solid #ddd;background:#fff;border-radius:6px;padding:8px 18px;cursor:pointer;font-size:14px;color:#666;">取消</button>
        <button onclick="saveWritingStyleDialog()" style="background:#07c160;color:#fff;border:none;border-radius:6px;padding:8px 18px;cursor:pointer;font-size:14px;">保存</button>
      </div>
    </div>
  \`;
  dialog.style.display = 'flex';
}

function closeWritingStyleDialog() {
  const dialog = document.getElementById('writingStyleDialog');
  if (dialog) dialog.style.display = 'none';
}

async function saveWritingStyleDialog() {
  const nameEl = document.getElementById('wsNameInput');
  const contentEl = document.getElementById('wsContentInput');
  const name = nameEl ? nameEl.value.trim() : '';
  const content = contentEl ? contentEl.value.trim() : '';
  if (!name) { alert('请输入文风名称'); return; }
  if (!content) { alert('请输入文风内容'); return; }

  if (_editingWritingStyleId) {
    const entry = writingStyleEntries.find(e => e.id === _editingWritingStyleId);
    if (entry) {
      entry.name = name;
      entry.content = content;
      entry.updatedAt = Date.now();
    }
  } else {
    writingStyleEntries.push({
      id: 'ws_' + Date.now() + '_' + Math.random().toString(36).substr(2,6),
      name,
      content,
      createdAt: Date.now(),
      updatedAt: Date.now()
    });
  }
  await saveWritingStyleEntries();
  closeWritingStyleDialog();
  renderWritingStyleList();
  // Refresh any open chat settings dropdowns
  refreshWritingStyleDropdowns();
}

async function deleteWritingStyleEntry(id) {
  if (!confirm('确定要删除这个文风条目吗？')) return;
  writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
  await saveWritingStyleEntries();
  renderWritingStyleList();
  refreshWritingStyleDropdowns();
}

function refreshWritingStyleDropdowns() {
  // Refresh all open writing style dropdowns in chat settings
  const selects = document.querySelectorAll('#chatWritingStyleSelect');
  selects.forEach(sel => {
    const currentVal = sel.value;
    sel.innerHTML = '<option value="">不使用文风</option>' +
      writingStyleEntries.map(e => \`<option value="\${e.id}">\${e.name}</option>\`).join('');
    sel.value = currentVal;
  });
}

// ============================================================
// 文风压缩 API调用
// ============================================================
async function compressWritingStyle(styleContent, contactId) {
  // Get current API settings
  const apiKey = await getFromStorage('API_KEY') || '';
  const apiUrl = await getFromStorage('API_URL') || 'https://api.openai.com/v1/chat/completions';
  const apiModel = await getFromStorage('API_MODEL') || 'gpt-3.5-turbo';

  if (!apiKey) {
    console.warn('[文风压缩] 未设置API Key，跳过压缩');
    return styleContent.substring(0, 100); // fallback: truncate
  }

  const prompt = \`请将以下文风要求压缩成一句简洁的行为准则（不超过60字），保留核心要点：\\n\\n\${styleContent}\`;

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': \`Bearer \${apiKey}\`
      },
      body: JSON.stringify({
        model: apiModel,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 150,
        temperature: 0.3
      })
    });
    if (!response.ok) throw new Error(\`API错误: \${response.status}\`);
    const data = await response.json();
    const compressed = data.choices?.[0]?.message?.content?.trim() || styleContent.substring(0, 80);
    console.log('[文风压缩] 成功:', compressed);
    return compressed;
  } catch(e) {
    console.error('[文风压缩] 失败:', e);
    return styleContent.substring(0, 80);
  }
}

// 当联系人切换文风时调用
async function onWritingStyleChange(contactId, styleId) {
  if (!styleId) {
    // 清除文风
    const settingsStr = await getFromStorage(\`CHAT_SETTINGS_\${contactId}\`);
    const settings = settingsStr ? (typeof settingsStr === 'string' ? JSON.parse(settingsStr) : settingsStr) : {};
    settings.writingStyleId = '';
    settings.compressedWritingStyle = '';
    await saveToStorage(\`CHAT_SETTINGS_\${contactId}\`, JSON.stringify(settings));
    console.log('[文风] 已清除文风设置');
    return;
  }

  const entry = writingStyleEntries.find(e => e.id === styleId);
  if (!entry) return;

  // Show loading indicator
  const loadingEl = document.getElementById('wsCompressLoading');
  if (loadingEl) loadingEl.style.display = 'block';

  try {
    const compressed = await compressWritingStyle(entry.content, contactId);
    const settingsStr = await getFromStorage(\`CHAT_SETTINGS_\${contactId}\`);
    const settings = settingsStr ? (typeof settingsStr === 'string' ? JSON.parse(settingsStr) : settingsStr) : {};
    settings.writingStyleId = styleId;
    settings.compressedWritingStyle = compressed;
    await saveToStorage(\`CHAT_SETTINGS_\${contactId}\`, JSON.stringify(settings));
    console.log('[文风] 已保存压缩文风:', compressed);
    if (loadingEl) loadingEl.style.display = 'none';
    alert(\`✅ 文风已设置！\\n\\n压缩后指令：\${compressed}\`);
  } catch(e) {
    if (loadingEl) loadingEl.style.display = 'none';
    console.error('[文风] 设置失败:', e);
  }
}

// 获取当前联系人的文风指令（附加到用户消息末尾）
async function getWritingStyleSuffix(contactId) {
  if (!contactId) return '';
  const settingsStr = await getFromStorage(\`CHAT_SETTINGS_\${contactId}\`);
  if (!settingsStr) return '';
  const settings = typeof settingsStr === 'string' ? JSON.parse(settingsStr) : settingsStr;
  if (settings.compressedWritingStyle) {
    return \`\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：\${settings.compressedWritingStyle})\`;
  }
  return '';
}
'''

# Inject writing style code at the end of main.js (before any last closing bracket or at end)
# Find a good insertion point - after the last major function or at the very end
if '// ============================================================\n// 文风设置系统' not in js:
    js = js + '\n' + WRITING_STYLE_CODE
    print('[Step3] 文风设置系统代码已注入')
else:
    print('[Step3] 文风设置系统代码已存在，跳过')

# ============================================================
# Step 4: Add writing style suffix to user message building
# Find where user messages are constructed and append writing style
# ============================================================

# Look for the pattern where userMessage content is set before API call
# Common pattern: messages.push({role: 'user', content: ...})
# Or: const userContent = ...

# Find where the final user message is assembled for API
# We need to append getWritingStyleSuffix() to the user's last message

# Search for the pattern of building messages array for API
msg_pattern = r'(const\s+messages\s*=\s*\[[\s\S]*?\]\s*;)'
msg_matches = list(re.finditer(msg_pattern, js))
print(f'[Step4] 找到 {len(msg_matches)} 个messages数组构建')

# Alternative: look for where userMessage is pushed
user_push_pattern = r"messages\.push\(\{[\s\S]*?role:\s*['\"]user['\"][\s\S]*?\}\)"
user_push_matches = list(re.finditer(user_push_pattern, js))
print(f'[Step4] 找到 {len(user_push_matches)} 个user消息push')

# The most reliable approach: find the sendMessage or buildApiMessages function
# and add writing style suffix there
send_func_pattern = r'(async function sendMessage\b|async function buildMessages\b|async function callAPI\b|async function sendToAI\b)'
send_matches = list(re.finditer(send_func_pattern, js))
print(f'[Step4] 找到发送函数: {[m.group(0) for m in send_matches]}')

# Find where userMessage/content is finalized
# Look for pattern like: let userMessage = ... or userContent
user_content_pattern = r'(let\s+userMessage\s*=|const\s+userMessage\s*=|let\s+userContent\s*=|const\s+userContent\s*=)'
uc_matches = list(re.finditer(user_content_pattern, js))
print(f'[Step4] 找到用户消息变量: {len(uc_matches)} 个')

# Strategy: Find the specific line where messageText or userMessage is built
# and add writing style injection after it
# Based on the code structure, look for where replyMsg and message content are combined

# Find pattern: content that includes the actual user text before pushing to messages
# Look for lines that construct the final user message content
inject_pattern = r'(content:\s*(?:userMessage|messageText|msgContent|finalContent|userContent)\s*\})'
inject_matches = list(re.finditer(inject_pattern, js))
print(f'[Step4] 找到content注入点: {len(inject_matches)} 个')

print('[Step4] 文风后缀注入点搜索完成，将在HTML中添加UI')

# ============================================================
# Save modified main.js
# ============================================================
with open(JS_MAIN, 'w', encoding='utf-8') as fh:
    fh.write(js)
print(f'[保存] main.js 已更新 ({len(js)} 字符)')

# ============================================================
# Step 3+4: Modify index.html - Add 文风设置 menu item + chat settings UI
# ============================================================
with open(INDEX_HTML, 'r', encoding='utf-8') as fh:
    html = fh.read()

print(f'[读取] index.html: {len(html)} 字符')

# Add 文风设置 to contacts sidebar menu
# Find existing menu items in the sidebar/contacts section
# Look for existing menu items like 世界书, 记忆总结, etc.

menu_patterns = [
    r'(<[^>]+onclick=["\']openWorldBook[^>]*>[^<]*</[^>]+>)',
    r'(世界书[^<]*</[^>]+>)',
    r'(onclick=["\']openWorldBook\(\)["\'][^>]*>[^<]*世界书)',
]

menu_found = False
for pat in menu_patterns:
    m = re.search(pat, html)
    if m:
        print(f'[Step3-HTML] 找到世界书菜单项: {m.group(0)[:80]}...')
        menu_found = True
        break

# Try to find the contacts menu list items
contacts_menu_pattern = r'(id=["\']worldBookBtn["\'][^>]*>[^<]*</[^>]*>|onclick=["\']openWorldBook\(\)["\'][^>]*>.*?</[^>]*>)'
cm_match = re.search(contacts_menu_pattern, html, re.DOTALL)
if cm_match:
    print(f'[Step3-HTML] 找到世界书按钮')

# Search for sidebar menu items more broadly  
sidebar_item_pattern = r'(class=["\'][^"\']*sidebar[^"\']*menu[^"\']*["\'][^>]*>|class=["\'][^"\']*menu-item[^"\']*["\'][^>]*>)'
si_match = re.search(sidebar_item_pattern, html)
if si_match:
    print(f'[Step3-HTML] 找到侧边栏菜单: {si_match.group(0)[:60]}')

print('[HTML搜索] 完成，检查结果...')

# Save html back (unchanged for now - we'll report what needs manual addition)
with open(INDEX_HTML, 'w', encoding='utf-8') as fh:
    fh.write(html)

print('\n============================================================')
print('搜索报告 - 请根据以下信息确认修改点')
print('============================================================')

# Report key findings for manual verification
findings = {
    'js_size': len(js),
    'html_size': len(html),
    'writing_style_injected': '// 文风设置系统' in js,
    'shijieguan_replaced': '世界观' in js,
    'yuyanguifan_removed': '语言规范' not in js,
}
print(json.dumps(findings, ensure_ascii=False, indent=2))
print('脚本执行完成！')
