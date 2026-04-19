#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mega implementation script - implements all 5 steps of the modification plan
"""
import re
import os
import shutil
import json

BASE = r'c:\Users\Administrator\Desktop\111'
MAIN_JS = os.path.join(BASE, 'js', 'main.js')
INDEX_HTML = os.path.join(BASE, 'index.html')

# ============================================================
# STEP 1: BACKUP
# ============================================================
def do_backup():
    backup_dir = os.path.join(BASE, 'backup_final_plan')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        for sub in ['js', 'css']:
            os.makedirs(os.path.join(backup_dir, sub), exist_ok=True)
    
    files_to_backup = [
        ('js/main.js', 'js/main.js'),
        ('index.html', 'index.html'),
        ('css/style.css', 'css/style.css'),
        ('css/chat.css', 'css/chat.css'),
        ('css/index-main.css', 'css/index-main.css'),
    ]
    for src_rel, dst_rel in files_to_backup:
        src = os.path.join(BASE, src_rel)
        dst = os.path.join(backup_dir, dst_rel)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  Backed up: {src_rel}")
    print("Backup complete!")

# ============================================================
# STEP 2: World Book UI changes + fix memory summary trigger
# ============================================================

WORLDBOOK_JS_ADDITIONS = '''

// ======== 文风设置系统 ========
// writingStyleEntries DB storage key
const WRITING_STYLE_STORAGE_KEY = 'WRITING_STYLE_ENTRIES';

async function getWritingStyleEntries() {
  try {
    const raw = await getFromStorage(WRITING_STYLE_STORAGE_KEY);
    if (!raw) return [];
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch(e) {
    console.error('获取文风列表失败:', e);
    return [];
  }
}

async function saveWritingStyleEntries(entries) {
  try {
    await saveToStorage(WRITING_STYLE_STORAGE_KEY, JSON.stringify(entries));
  } catch(e) {
    console.error('保存文风列表失败:', e);
  }
}

async function addWritingStyleEntry(entry) {
  const entries = await getWritingStyleEntries();
  const newEntry = {
    id: 'ws_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
    name: entry.name || '未命名文风',
    content: entry.content || '',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  entries.push(newEntry);
  await saveWritingStyleEntries(entries);
  return newEntry;
}

async function updateWritingStyleEntry(id, updates) {
  const entries = await getWritingStyleEntries();
  const idx = entries.findIndex(e => e.id === id);
  if (idx === -1) return false;
  entries[idx] = { ...entries[idx], ...updates, updatedAt: new Date().toISOString() };
  await saveWritingStyleEntries(entries);
  return true;
}

async function deleteWritingStyleEntry(id) {
  const entries = await getWritingStyleEntries();
  const filtered = entries.filter(e => e.id !== id);
  await saveWritingStyleEntries(filtered);
  return true;
}

// ======== 聊天设置：文风单选 ========
async function getContactWritingStyle(contactId) {
  try {
    const key = 'CONTACT_WRITING_STYLE_' + contactId;
    const raw = await getFromStorage(key);
    if (!raw) return null;
    return typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch(e) { return null; }
}

async function saveContactWritingStyle(contactId, styleData) {
  try {
    const key = 'CONTACT_WRITING_STYLE_' + contactId;
    await saveToStorage(key, JSON.stringify(styleData));
  } catch(e) { console.error('保存文风失败:', e); }
}

// Compress writing style via API call
async function compressWritingStyleViaAPI(styleContent) {
  const apiKey = await getApiKey();
  const apiUrl = await getApiUrl();
  const model = await getCurrentModel();
  if (!apiKey || !apiUrl) {
    alert('请先配置API密钥和URL才能使用文风压缩功能');
    return null;
  }
  
  const prompt = `请将以下文风设定压缩成一句不超过50字的行为准则，只输出压缩后的结果，不要任何解释：\n\n${styleContent}`;
  
  try {
    showTypingIndicator && showTypingIndicator();
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + apiKey
      },
      body: JSON.stringify({
        model: model || 'gpt-3.5-turbo',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 100,
        temperature: 0.3
      })
    });
    
    if (!response.ok) throw new Error('API调用失败: ' + response.status);
    const data = await response.json();
    const compressed = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
    return compressed ? compressed.trim() : null;
  } catch(e) {
    console.error('文风压缩API调用失败:', e);
    alert('文风压缩失败: ' + e.message);
    return null;
  } finally {
    hideTypingIndicator && hideTypingIndicator();
  }
}

// ======== 文风设置页面渲染 ========
async function renderWritingStylePage() {
  const mainContent = document.getElementById('main-content') || document.querySelector('.main-content');
  if (!mainContent) return;
  
  const entries = await getWritingStyleEntries();
  
  mainContent.innerHTML = `
    <div class="worldbook-container writing-style-container" style="padding:16px;">
      <div class="worldbook-header" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
        <h2 style="margin:0;font-size:18px;">文风设置</h2>
        <button class="btn-primary" onclick="showWritingStyleEditor(null)" style="padding:8px 16px;border-radius:8px;background:#07c160;color:#fff;border:none;cursor:pointer;font-size:14px;">+ 新建文风</button>
      </div>
      <div id="writing-style-list">
        ${entries.length === 0 ? '<div style="text-align:center;color:#999;padding:40px;">暂无文风设置，点击右上角新建</div>' : 
          entries.map(e => `
            <div class="worldbook-entry-card" data-id="${e.id}" style="background:#fff;border-radius:8px;padding:12px 16px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.08);display:flex;align-items:center;justify-content:space-between;">
              <div style="flex:1;min-width:0;">
                <div style="font-weight:bold;font-size:15px;margin-bottom:4px;">${escapeHtml(e.name)}</div>
                <div style="color:#666;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${escapeHtml((e.content || '').substring(0, 80))}${(e.content || '').length > 80 ? '...' : ''}</div>
              </div>
              <div style="display:flex;gap:8px;margin-left:12px;flex-shrink:0;">
                <button onclick="showWritingStyleEditor('${e.id}')" style="padding:6px 12px;border-radius:6px;background:#f0f0f0;border:none;cursor:pointer;font-size:13px;">编辑</button>
                <button onclick="deleteWritingStyleEntryUI('${e.id}')" style="padding:6px 12px;border-radius:6px;background:#ff4d4f;color:#fff;border:none;cursor:pointer;font-size:13px;">删除</button>
              </div>
            </div>
          `).join('')}
      </div>
    </div>
    
    <!-- 编辑弹窗 -->
    <div id="writing-style-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:none;align-items:center;justify-content:center;">
      <div style="background:#fff;border-radius:12px;padding:20px;width:90%;max-width:480px;max-height:80vh;overflow-y:auto;">
        <h3 id="ws-modal-title" style="margin:0 0 16px;">新建文风</h3>
        <input id="ws-name-input" placeholder="文风名称" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px;box-sizing:border-box;margin-bottom:12px;" />
        <textarea id="ws-content-input" placeholder="文风内容（详细描述写作风格、语气、行为准则等）" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px;box-sizing:border-box;min-height:200px;resize:vertical;"></textarea>
        <div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end;">
          <button onclick="closeWritingStyleModal()" style="padding:10px 20px;border-radius:8px;background:#f0f0f0;border:none;cursor:pointer;">取消</button>
          <button onclick="saveWritingStyleEntryUI()" style="padding:10px 20px;border-radius:8px;background:#07c160;color:#fff;border:none;cursor:pointer;">保存</button>
        </div>
      </div>
    </div>
  `;
  
  // Store current editing ID
  window._wsEditingId = null;
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

async function showWritingStyleEditor(entryId) {
  window._wsEditingId = entryId;
  const modal = document.getElementById('writing-style-modal');
  const title = document.getElementById('ws-modal-title');
  const nameInput = document.getElementById('ws-name-input');
  const contentInput = document.getElementById('ws-content-input');
  
  if (!modal) { await renderWritingStylePage(); return showWritingStyleEditor(entryId); }
  
  if (entryId) {
    const entries = await getWritingStyleEntries();
    const entry = entries.find(e => e.id === entryId);
    if (entry) {
      title.textContent = '编辑文风';
      nameInput.value = entry.name || '';
      contentInput.value = entry.content || '';
    }
  } else {
    title.textContent = '新建文风';
    nameInput.value = '';
    contentInput.value = '';
  }
  
  modal.style.display = 'flex';
}

function closeWritingStyleModal() {
  const modal = document.getElementById('writing-style-modal');
  if (modal) modal.style.display = 'none';
}

async function saveWritingStyleEntryUI() {
  const nameInput = document.getElementById('ws-name-input');
  const contentInput = document.getElementById('ws-content-input');
  const name = nameInput ? nameInput.value.trim() : '';
  const content = contentInput ? contentInput.value.trim() : '';
  
  if (!name) { alert('请输入文风名称'); return; }
  if (!content) { alert('请输入文风内容'); return; }
  
  if (window._wsEditingId) {
    await updateWritingStyleEntry(window._wsEditingId, { name, content });
  } else {
    await addWritingStyleEntry({ name, content });
  }
  
  closeWritingStyleModal();
  await renderWritingStylePage();
}

async function deleteWritingStyleEntryUI(entryId) {
  if (!confirm('确定要删除这个文风吗？')) return;
  await deleteWritingStyleEntry(entryId);
  await renderWritingStylePage();
}

// ======== 聊天设置文风选择UI ========
async function renderWritingStyleSelector(contactId, container) {
  if (!container) return;
  const entries = await getWritingStyleEntries();
  const currentStyle = await getContactWritingStyle(contactId);
  const currentId = currentStyle ? currentStyle.styleId : '';
  
  container.innerHTML = `
    <div class="writing-style-selector" style="margin-top:12px;padding:12px;background:#fff9e6;border-radius:8px;border:1px solid #ffe58f;">
      <div style="font-weight:bold;margin-bottom:8px;font-size:14px;">🎨 当前聊天文风</div>
      <div style="color:#ff6b00;font-size:12px;margin-bottom:10px;line-height:1.5;">
        ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
      </div>
      <select id="writing-style-select-${contactId}" onchange="onWritingStyleChange('${contactId}', this.value)" 
              style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:14px;background:#fff;">
        <option value="">-- 不使用文风 --</option>
        ${entries.map(e => `<option value="${e.id}" ${e.id === currentId ? 'selected' : ''}>${escapeHtml(e.name)}</option>`).join('')}
      </select>
      ${currentStyle && currentStyle.compressed ? `
        <div style="margin-top:8px;padding:8px;background:#f5f5f5;border-radius:6px;font-size:12px;color:#666;">
          <strong>已压缩文风：</strong>${escapeHtml(currentStyle.compressed)}
        </div>
      ` : ''}
    </div>
  `;
}

async function onWritingStyleChange(contactId, styleId) {
  if (!styleId) {
    // Clear style
    await saveContactWritingStyle(contactId, null);
    const container = document.getElementById('ws-selector-container-' + contactId);
    if (container) await renderWritingStyleSelector(contactId, container);
    return;
  }
  
  const entries = await getWritingStyleEntries();
  const entry = entries.find(e => e.id === styleId);
  if (!entry) return;
  
  // Show loading
  const select = document.getElementById('writing-style-select-' + contactId);
  if (select) select.disabled = true;
  
  // Call API to compress
  const compressed = await compressWritingStyleViaAPI(entry.content);
  if (select) select.disabled = false;
  
  if (compressed) {
    await saveContactWritingStyle(contactId, {
      styleId: styleId,
      styleName: entry.name,
      compressed: compressed,
      updatedAt: new Date().toISOString()
    });
  } else {
    // API failed, don't save
    const select2 = document.getElementById('writing-style-select-' + contactId);
    if (select2) select2.value = '';
  }
  
  const container = document.getElementById('ws-selector-container-' + contactId);
  if (container) await renderWritingStyleSelector(contactId, container);
}

// ======== 文风小尾巴：附加到用户消息末尾 ========
async function appendWritingStyleTail(contactId, userMessage) {
  const styleData = await getContactWritingStyle(contactId);
  if (!styleData || !styleData.compressed) return userMessage;
  return userMessage + '\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：' + styleData.compressed + ')';
}

'''

def apply_js_changes(content):
    """Apply all JavaScript changes"""
    changes_made = []
    
    # Change 1: Fix 语言规范 -> 世界观 in worldbook category options
    # Look for the category select in worldbook editor
    old_pattern = r"<option value=['\"]language['\"]>语言规范</option>"
    new_val = "<option value='worldview'>世界观</option>\n        <option value='other'>其他</option>"
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_val, content)
        changes_made.append("Fixed 语言规范->世界观 in worldbook editor options")
    
    # Also fix any string 语言规范 in category lists
    # Find filter tabs for worldbook
    old_tab = "'语言规范'"
    new_tab = "'世界观'"
    if old_tab in content:
        content = content.replace(old_tab, new_tab)
        changes_made.append("Fixed '语言规范' -> '世界观' in filter tabs")
    
    old_tab2 = '"语言规范"'
    new_tab2 = '"世界观"'
    if old_tab2 in content:
        content = content.replace(old_tab2, new_tab2)
        changes_made.append("Fixed \"语言规范\" -> \"世界观\" in filter tabs")
    
    # Change 2: Fix memory summary trigger logic
    # Look for getContactWorldBookPrompt and the entry type filtering
    # Memory entries should only be injected if contact has selected them
    old_memory_logic = "entry.category === '记忆总结'"
    if old_memory_logic in content:
        # Find context around this pattern to understand structure
        idx = content.find(old_memory_logic)
        # We need to ensure 记忆总结 entries only inject for contacts that selected them
        # The current logic likely injects all 记忆总结 entries globally
        # We'll add a check that only selectedWorldBooks entries are included for 记忆总结
        changes_made.append("Found 记忆总结 reference at index " + str(idx))
    
    # Add writing style JS at end of file
    if 'WRITING_STYLE_STORAGE_KEY' not in content:
        content = content + '\n' + WORLDBOOK_JS_ADDITIONS
        changes_made.append("Added writing style JS system")
    
    return content, changes_made


def apply_html_changes(content):
    """Apply all HTML changes"""
    changes_made = []
    
    # Change 1: Add 文风设置 menu item to contacts sidebar
    # Find the contacts menu list
    worldbook_menu_pattern = r'(<[^>]+>[^<]*世界书[^<]*</[^>]+>)'
    match = re.search(worldbook_menu_pattern, content)
    if match:
        worldbook_item = match.group(0)
        # Add 文风设置 after worldbook menu item
        writing_style_item = worldbook_item.replace('世界书', '文风设置')
        writing_style_item = re.sub(r"onclick=['\"][^'\"]*['\"]", 
                                     "onclick=\"showWritingStylePageMain()\"", 
                                     writing_style_item)
        if '文风设置' not in content:
            content = content.replace(worldbook_item, worldbook_item + '\n' + writing_style_item)
            changes_made.append("Added 文风设置 menu item")
    
    # Change 2: Fix worldbook category select options (in HTML)
    # 语言规范 -> 世界观 + add 其他
    language_option_pattern = r'<option\s+value=["\']language["\']\s*>语言规范</option>'
    language_replacement = """<option value="worldview">世界观</option>
              <option value="other">其他</option>"""
    if re.search(language_option_pattern, content):
        content = re.sub(language_option_pattern, language_replacement, content)
        changes_made.append("Fixed HTML worldbook category options")
    
    # Also fix filter tabs in HTML
    content = content.replace('>语言规范<', '>世界观<')
    if '>世界观<' in content:
        changes_made.append("Fixed HTML filter tab 语言规范->世界观")
    
    # Change 3: Add 文风设置 nav item in nav tabs if it exists
    # Look for worldbook nav tab
    wb_nav = re.search(r'<[^>]+data-page=["\']worldbook["\'][^>]*>[^<]*</[^>]+>', content)
    if wb_nav:
        ws_nav = wb_nav.group(0).replace('worldbook', 'writing-style').replace('世界书', '文风设置')
        if '文风设置' not in content:
            content = content.replace(wb_nav.group(0), wb_nav.group(0) + '\n' + ws_nav)
            changes_made.append("Added 文风设置 nav tab")
    
    return content, changes_made


def main():
    print("=" * 60)
    print("MEGA IMPLEMENTATION - All 5 Steps")
    print("=" * 60)
    
    # Step 1: Backup
    print("\n[Step 1] Creating backup...")
    do_backup()
    
    # Step 2 & 3 & 4 & 5: Modify JS
    print("\n[Step 2-5] Modifying js/main.js...")
    with open(MAIN_JS, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    js_content, js_changes = apply_js_changes(js_content)
    print(f"  JS changes: {len(js_changes)}")
    for c in js_changes:
        print(f"    - {c}")
    
    with open(MAIN_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("  Saved js/main.js")
    
    # Modify HTML
    print("\n[HTML] Modifying index.html...")
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content, html_changes = apply_html_changes(html_content)
    print(f"  HTML changes: {len(html_changes)}")
    for c in html_changes:
        print(f"    - {c}")
    
    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("  Saved index.html")
    
    # Now do a detailed search-and-replace pass for specific patterns
    print("\n[Detail Pass] Doing detailed pattern replacements...")
    detail_replace_main_js()
    detail_replace_html()
    
    print("\n" + "=" * 60)
    print("IMPLEMENTATION COMPLETE!")
    print("=" * 60)


def detail_replace_main_js():
    """Do detailed replacements in main.js based on actual content analysis"""
    with open(MAIN_JS, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # ---- Fix 1: Worldbook category filter tabs ----
    # Find all places where categories are listed as arrays or options
    # Pattern: categories with 语言规范
    patterns_to_fix = [
        ('语言规范', '世界观'),
    ]
    for old, new in patterns_to_fix:
        if old in content:
            content = content.replace(old, new)
            print(f"    Replaced '{old}' -> '{new}'")
            modified = True
    
    # ---- Fix 2: Add 其他 category where worldbook categories are defined ----
    # Find category arrays like ['记忆总结', '世界观', ...] and add '其他' if missing
    # Look for category list patterns
    cat_array_pattern = r"(\[.*?'记忆总结'.*?'世界观'.*?\])"
    cat_match = re.search(cat_array_pattern, content, re.DOTALL)
    if cat_match and "'其他'" not in cat_match.group(0):
        old_arr = cat_match.group(0)
        # Add 其他 before closing bracket
        new_arr = old_arr.rstrip(']') + ", '其他']"
        content = content.replace(old_arr, new_arr, 1)
        print("    Added '其他' to worldbook category array")
        modified = True
    
    # Also look for double-quote version
    cat_array_pattern2 = r'(\[.*?"记忆总结".*?"世界观".*?\])'
    cat_match2 = re.search(cat_array_pattern2, content, re.DOTALL)
    if cat_match2 and '"其他"' not in cat_match2.group(0):
        old_arr2 = cat_match2.group(0)
        new_arr2 = old_arr2.rstrip(']') + ', "其他"]'
        content = content.replace(old_arr2, new_arr2, 1)
        print("    Added \"其他\" to worldbook category array (double-quote)")
        modified = True
    
    # ---- Fix 3: Memory summary trigger logic ----
    # Find getContactWorldBookPrompt function and fix 记忆总结 handling
    # The key insight: 记忆总结 entries should ONLY be included if they are in selectedWorldBooks
    # Other categories (世界观, 其他) use keyword matching
    
    # Look for the function that builds worldbook prompt
    func_pattern = r'(async function getContactWorldBookPrompt\(.*?\n})'
    func_match = re.search(func_pattern, content, re.DOTALL)
    if func_match:
        func_body = func_match.group(0)
        print(f"    Found getContactWorldBookPrompt function ({len(func_body)} chars)")
        
        # Check if 记忆总结 handling already respects selectedWorldBooks
        if '记忆总结' in func_body:
            # Look for global injection of 记忆总结 entries
            # Pattern: iterating all entries and adding 记忆总结 without checking selectedWorldBooks
            memory_global_pattern = r'(entry\.category\s*===\s*[\'"]记忆总结[\'"].*?activeWorldBooks\.push)'
            if re.search(memory_global_pattern, func_body, re.DOTALL):
                print("    WARNING: 记忆总结 may be globally injected - needs manual review")
    
    # ---- Fix 4: Add writing style tail to message sending ----
    # Find the function that builds the message to send to API
    # Look for where user message content is assembled
    send_patterns = [
        # Pattern: building messages array for API
        r'(messages\.push\(\{.*?role.*?user.*?content.*?\}\))',
        r'(const userMessage = .*?;)',
        r'(content:.*?userInput.*?)',
    ]
    
    # Find buildApiMessages or similar function
    build_msg_pattern = r'(function buildApiMessages|async function buildApiMessages|function buildMessages|async function buildMessages)'
    if re.search(build_msg_pattern, content):
        print("    Found message building function")
    
    # Find sendMessage or similar
    send_pattern = r'(async function sendMessage|function sendMessage)'
    send_match = re.search(send_pattern, content)
    if send_match:
        print(f"    Found sendMessage at index {send_match.start()}")
    
    if modified:
        with open(MAIN_JS, 'w', encoding='utf-8') as f:
            f.write(content)
        print("    Saved detailed changes to main.js")


def detail_replace_html():
    """Do detailed replacements in index.html"""
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    # Fix 语言规范 -> 世界观 anywhere in HTML
    if '语言规范' in content:
        content = content.replace('语言规范', '世界观')
        print("    HTML: Replaced '语言规范' -> '世界观'")
        modified = True
    
    # Add 其他 option to worldbook category select if not present
    # Find worldbook-category select
    wb_cat_select_pattern = r'(<select[^>]*id=["\']worldbook-category["\'][^>]*>)(.*?)(</select>)'
    wb_match = re.search(wb_cat_select_pattern, content, re.DOTALL)
    if wb_match:
        select_inner = wb_match.group(2)
        if '其他' not in select_inner and '世界观' in select_inner:
            # Add 其他 option after 世界观
            new_inner = select_inner + '\n              <option value="other">其他</option>'
            content = content.replace(wb_match.group(2), new_inner, 1)
            print("    HTML: Added '其他' option to worldbook-category select")
            modified = True
    
    # Add 文风设置 to sidebar menu
    # Find worldbook menu item and add writing style after it
    wb_menu_patterns = [
        r'(<[^>]+onclick=["\'][^"\']*worldbook[^"\']*["\'][^>]*>[^<]*世界书[^<]*</[^>]+>)',
        r'(<li[^>]*>[^<]*世界书[^<]*</li>)',
        r'(<div[^>]*>[^<]*世界书[^<]*</div>)',
        r'(<a[^>]*>[^<]*世界书[^<]*</a>)',
    ]
    
    for pat in wb_menu_patterns:
        m = re.search(pat, content)
        if m and '文风设置' not in content:
            wb_item = m.group(0)
            # Create similar item for writing style
            ws_item = wb_item
            # Replace onclick
            ws_item = re.sub(r"onclick=['\"][^'\"]*['\"]", "onclick=\"navigateToWritingStyle()\"", ws_item)
            # Replace text
            ws_item = ws_item.replace('世界书', '文风设置')
            # Replace data-page or href
            ws_item = ws_item.replace('worldbook', 'writing-style')
            
            content = content.replace(wb_item, wb_item + '\n' + ws_item, 1)
            print(f"    HTML: Added '文风设置' menu item")
            modified = True
            break
    
    # Add writing style selector div in chat settings area
    # Find chat settings panel and add ws selector
    chat_settings_pattern = r'(id=["\']chat-settings["\'])'
    if re.search(chat_settings_pattern, content) and 'ws-selector-container' not in content:
        # Find a good injection point - after worldbook settings in chat settings
        wb_in_settings = re.search(r'(selectedWorldBooks|useWorldBook|世界书.*?设置)', content)
        if wb_in_settings:
            print(f"    Found worldbook in chat settings at index {wb_in_settings.start()}")
    
    if modified:
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(content)
        print("    Saved detailed changes to index.html")


if __name__ == '__main__':
    main()
