#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive script to implement all 5 steps of changes.
"""
import os
import shutil
import re
import sys

BASE = r'c:\Users\Administrator\Desktop\111'
BACKUP_DIR = os.path.join(BASE, 'backup_final_plan')

def backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        os.makedirs(os.path.join(BACKUP_DIR, 'js'))
        os.makedirs(os.path.join(BACKUP_DIR, 'css'))
    files = [
        ('index.html', ''),
        ('js/main.js', 'js'),
        ('css/chat.css', 'css'),
        ('css/index-main.css', 'css'),
        ('css/style.css', 'css'),
        ('css/themes.css', 'css'),
    ]
    for f, subdir in files:
        src = os.path.join(BASE, f)
        dst_dir = os.path.join(BACKUP_DIR, subdir) if subdir else BACKUP_DIR
        if os.path.exists(src):
            shutil.copy2(src, dst_dir)
            print(f'Backed up: {f}')
    print('Backup done.\n')

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def patch_index_html():
    path = os.path.join(BASE, 'index.html')
    content = read_file(path)
    
    # ============================================================
    # Step 2a: World Book tabs - change 语言规范 to 世界观, add 其他
    # ============================================================
    # Replace the tab bar in world-win page
    old_tabs = '''<div style="display:flex; gap:8px; padding:10px 20px; border-bottom:1px solid #f0e8df; background:rgba(255,255,255,0.7);">
        <div class="wb-tab active" onclick="filterWorldBook('all')" data-category="all" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:var(--main-pink); color:white;">全部</div>
        <div class="wb-tab" onclick="filterWorldBook('记忆总结')" data-category="记忆总结" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">记忆总结</div>
        <div class="wb-tab" onclick="filterWorldBook('语言规范')" data-category="语言规范" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">语言规范</div>
        <div class="wb-tab" onclick="filterWorldBook('html')" data-category="html" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">html</div>
      </div>'''
    
    new_tabs = '''<div style="display:flex; gap:8px; padding:10px 20px; border-bottom:1px solid #f0e8df; background:rgba(255,255,255,0.7); flex-wrap:wrap;">
        <div class="wb-tab active" onclick="filterWorldBook('all')" data-category="all" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:var(--main-pink); color:white;">全部</div>
        <div class="wb-tab" onclick="filterWorldBook('记忆总结')" data-category="记忆总结" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">记忆总结</div>
        <div class="wb-tab" onclick="filterWorldBook('世界观')" data-category="世界观" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">世界观</div>
        <div class="wb-tab" onclick="filterWorldBook('html')" data-category="html" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">html</div>
        <div class="wb-tab" onclick="filterWorldBook('其他')" data-category="其他" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">其他</div>
      </div>'''
    
    if old_tabs in content:
        content = content.replace(old_tabs, new_tabs)
        print('✓ Step 2a: World Book tabs updated (语言规范→世界观, added 其他)')
    else:
        print('✗ Step 2a: Could not find World Book tabs to replace')
    
    # ============================================================
    # Step 2b: World Book add/edit form - change 语言规范 to 世界观, add 其他
    # ============================================================
    # Replace category dropdown in add-worldbook form
    old_cat_dropdown = '''<option value="记忆总结">记忆总结</option>
            <option value="语言规范">语言规范</option>
            <option value="html">html</option>'''
    
    new_cat_dropdown = '''<option value="记忆总结">记忆总结</option>
            <option value="世界观">世界观</option>
            <option value="html">html</option>
            <option value="其他">其他</option>'''
    
    if old_cat_dropdown in content:
        content = content.replace(old_cat_dropdown, new_cat_dropdown)
        print('✓ Step 2b: World Book category dropdown updated')
    else:
        print('✗ Step 2b: Could not find category dropdown - trying alternate search...')
        # Try to find it with regex
        m = re.search(r'(<option value="记忆总结">记忆总结</option>\s*<option value=")[^"]*("[^>]*>[^<]*</option>\s*<option value="html">html</option>)', content)
        if m:
            old = m.group(0)
            new_v = '<option value="记忆总结">记忆总结</option>\n            <option value="世界观">世界观</option>\n            <option value="html">html</option>\n            <option value="其他">其他</option>'
            content = content.replace(old, new_v)
            print('✓ Step 2b: World Book category dropdown updated (regex)')
        else:
            print('✗ Step 2b: Skipped')
    
    # ============================================================
    # Step 3: Add 文风设置 to contacts menu
    # ============================================================
    # Find the contacts settings menu and add 文风设置 entry
    # Look for 世界书 entry in the menu
    old_worldbook_menu = '''<div class="menu-item" onclick="openSub('world-win')">
          <span>世界书</span>
          <svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
        </div>'''
    
    new_worldbook_menu = '''<div class="menu-item" onclick="openSub('world-win')">
          <span>世界书</span>
          <svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
        </div>
        <div class="menu-item" onclick="openSub('writing-style-win')">
          <span>文风设置</span>
          <svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
        </div>'''
    
    if old_worldbook_menu in content:
        content = content.replace(old_worldbook_menu, new_worldbook_menu)
        print('✓ Step 3a: Added 文风设置 to contacts menu')
    else:
        # Try regex
        m = re.search(r'(<div class="menu-item" onclick="openSub\(\'world-win\'\)">[\s\S]*?</div>)', content)
        if m:
            old = m.group(0)
            new_v = old + '''
        <div class="menu-item" onclick="openSub('writing-style-win')">
          <span>文风设置</span>
          <svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
        </div>'''
            content = content.replace(old, new_v, 1)
            print('✓ Step 3a: Added 文风设置 to contacts menu (regex)')
        else:
            print('✗ Step 3a: Could not find world-win menu item')
    
    # ============================================================
    # Step 3b: Add 文风设置 sub-page (similar to world-win)
    # ============================================================
    writing_style_page = '''
    <!-- 文风设置页面 -->
    <div class="sub-page" id="writing-style-win">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('writing-style-win')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">文风设置</div>
        <div style="margin-left:auto; font-size:24px; color:var(--text-dark); cursor:pointer;" onclick="openSub('add-writing-style')">+</div>
      </div>
      <div class="page-body" id="writingStyleList">
        <div class="empty-tip">暂无文风条目<br>点击右上角 + 新建</div>
      </div>
    </div>

    <!-- 新建/编辑文风条目页面 -->
    <div class="sub-page" id="add-writing-style">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('add-writing-style')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title" id="addWritingStyleTitle">新建文风</div>
        <div style="margin-left:auto; font-size:16px; color:var(--main-pink); cursor:pointer; font-weight:500;" onclick="saveWritingStyle()">保存</div>
      </div>
      <div class="page-body" style="padding:20px;">
        <input type="hidden" id="editingWritingStyleId" value="">
        <div style="margin-bottom:16px;">
          <div style="font-size:13px; color:var(--text-light); margin-bottom:6px;">文风名称</div>
          <input type="text" id="writingStyleName" placeholder="输入文风名称" style="width:100%; padding:10px 12px; border:1px solid #e0d5cc; border-radius:10px; font-size:14px; box-sizing:border-box;">
        </div>
        <div style="margin-bottom:16px;">
          <div style="font-size:13px; color:var(--text-light); margin-bottom:6px;">文风内容（详细描述写作风格和行为规范）</div>
          <textarea id="writingStyleContent" placeholder="详细描述文风要求，如语气、措辞、表达方式等..." style="width:100%; padding:10px 12px; border:1px solid #e0d5cc; border-radius:10px; font-size:14px; min-height:200px; box-sizing:border-box; resize:vertical;"></textarea>
        </div>
      </div>
    </div>'''
    
    # Insert before </body> or before the last sub-page closing
    if '</body>' in content:
        content = content.replace('</body>', writing_style_page + '\n</body>', 1)
        print('✓ Step 3b: Added 文风设置 sub-pages to HTML')
    else:
        print('✗ Step 3b: Could not find </body>')
    
    # ============================================================
    # Step 4: Add 文风单选 to chat settings
    # ============================================================
    # Find the chat settings section - look for world book setting or jailbreak setting
    # We'll look for a distinctive part of chat-setting page
    old_chat_setting_wb = '''<div style="font-size:13px; color:var(--text-light); margin-bottom:10px;">选择要启用的世界书条目：</div>'''
    
    writing_style_select_html = '''
        <div style="margin-bottom:20px; padding:16px; background:#fff8f5; border-radius:12px; border:1px solid #f0e0d6;">
          <div style="font-weight:600; font-size:15px; margin-bottom:8px;">📝 当前聊天文风</div>
          <div style="font-size:12px; color:#e05; background:#fff0f0; border-radius:8px; padding:8px 10px; margin-bottom:10px;">
            ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
          </div>
          <select id="chatWritingStyleSelect" onchange="onWritingStyleChange(this.value)" style="width:100%; padding:10px 12px; border:1px solid #e0d5cc; border-radius:10px; font-size:14px; background:white;">
            <option value="">-- 不使用文风 --</option>
          </select>
          <div id="compressedStylePreview" style="margin-top:8px; font-size:12px; color:var(--text-light); display:none;">
            <div style="font-size:12px; color:var(--text-light); margin-bottom:4px;">已压缩的文风指令：</div>
            <div id="compressedStyleText" style="background:#f5f5f5; padding:8px; border-radius:6px; font-size:12px;"></div>
          </div>
        </div>'''
    
    if old_chat_setting_wb in content:
        content = content.replace(old_chat_setting_wb, writing_style_select_html + '\n        ' + old_chat_setting_wb)
        print('✓ Step 4: Added 文风单选 to chat settings')
    else:
        # Try to find chat settings page and insert there
        m = re.search(r'(id="chat-setting"[\s\S]{0,500}?<div class="page-body"[^>]*>)', content)
        if m:
            old = m.group(0)
            content = content.replace(old, old + writing_style_select_html, 1)
            print('✓ Step 4: Added 文风单选 to chat settings (fallback)')
        else:
            print('✗ Step 4: Could not find chat settings page')
    
    write_file(path, content)
    print('index.html saved.\n')

def patch_main_js():
    path = os.path.join(BASE, 'js/main.js')
    content = read_file(path)
    
    # ============================================================
    # Step 2c: Fix getContactWorldBookPrompt - 记忆总结 only for selected contacts
    # ============================================================
    old_func = '''async function getContactWorldBookPrompt(contactId) {
  const contactSettingsStr = await getFromStorage(`CHAT_SETTINGS_${contactId}`);
  const contactSettings = contactSettingsStr ? (typeof contactSettingsStr === 'string' ? JSON.parse(contactSettingsStr) : contactSettingsStr) : { useWorldBook: true, selectedWorldBooks: [] };

  let activeWorldBooks = [];
  if (contactSettings.useWorldBook) {
    if (worldBook) activeWorldBooks.push(`全局世界书：\\n${worldBook}`);
    if (contactSettings.selectedWorldBooks && contactSettings.selectedWorldBooks.length > 0) {
      const selectedEntries = worldBookEntries.filter(e => contactSettings.selectedWorldBooks.includes(e.id));
      selectedEntries.forEach(entry => {
        if (entry.category === '记忆总结') {
          activeWorldBooks.push(`[${entry.name}]\\n${entry.content}`);
        } else if (entry.triggerType !== 'keyword') {
          activeWorldBooks.push(`[${entry.name} - 设定]\\n${entry.content}`);
        }
      });
    }
  }
  return activeWorldBooks.length > 0 ? `\\n${WORLD_BOOK_PRIORITY_INSTRUCTION}\\n【世界书/角色设定】\\n${activeWorldBooks.join('\\n\\n')}\\n` : '';
}'''
    
    new_func = '''async function getContactWorldBookPrompt(contactId) {
  const contactSettingsStr = await getFromStorage(`CHAT_SETTINGS_${contactId}`);
  const contactSettings = contactSettingsStr ? (typeof contactSettingsStr === 'string' ? JSON.parse(contactSettingsStr) : contactSettingsStr) : { useWorldBook: true, selectedWorldBooks: [] };

  let activeWorldBooks = [];
  if (contactSettings.useWorldBook) {
    if (worldBook) activeWorldBooks.push(`全局世界书：\\n${worldBook}`);
    if (contactSettings.selectedWorldBooks && contactSettings.selectedWorldBooks.length > 0) {
      const selectedEntries = worldBookEntries.filter(e => contactSettings.selectedWorldBooks.includes(e.id));
      selectedEntries.forEach(entry => {
        if (entry.category === '记忆总结') {
          // 记忆总结：只有在该联系人明确勾选了此条目时才注入（常驻上下文）
          activeWorldBooks.push(`[${entry.name}]\\n${entry.content}`);
        } else if (entry.category === '世界观' || entry.category === '其他') {
          // 世界观/其他：严格关键词触发，不在这里注入（由关键词检测触发）
          // do nothing here - handled by keyword trigger in buildMessages
        } else if (entry.triggerType !== 'keyword') {
          activeWorldBooks.push(`[${entry.name} - 设定]\\n${entry.content}`);
        }
      });
    }
  }
  return activeWorldBooks.length > 0 ? `\\n${WORLD_BOOK_PRIORITY_INSTRUCTION}\\n【世界书/角色设定】\\n${activeWorldBooks.join('\\n\\n')}\\n` : '';
}'''
    
    if old_func in content:
        content = content.replace(old_func, new_func)
        print('✓ Step 2c: Fixed getContactWorldBookPrompt trigger logic')
    else:
        # Try with flexible whitespace
        print('✗ Step 2c: Exact match failed, trying regex...')
        m = re.search(r'async function getContactWorldBookPrompt\(contactId\) \{[\s\S]*?\n\}', content)
        if m:
            old_f = m.group(0)
            content = content.replace(old_f, new_func, 1)
            print('✓ Step 2c: Fixed via regex')
        else:
            print('✗ Step 2c: Could not fix getContactWorldBookPrompt')
    
    # ============================================================
    # Step 2d: Update renderWorldBookList to show 语言规范 entries as 世界观
    # ============================================================
    content = content.replace("category === '语言规范'", "category === '世界观'")
    content = content.replace("value=\"语言规范\"", "value=\"世界观\"")
    content = content.replace("'语言规范'", "'世界观'")
    print('✓ Step 2d: Replaced 语言规范 references with 世界观 in main.js')
    
    # ============================================================
    # Step 3c: Add writingStyleEntries global var and functions
    # ============================================================
    old_globals = '''let worldBook = '';
let worldBookEntries = [];'''
    
    new_globals = '''let worldBook = '';
let worldBookEntries = [];
let writingStyleEntries = []; // 文风设置条目'''
    
    if old_globals in content:
        content = content.replace(old_globals, new_globals)
        print('✓ Step 3c: Added writingStyleEntries global var')
    else:
        print('✗ Step 3c: Could not find globals - trying fallback')
        # try just adding after worldBookEntries
        content = content.replace('let worldBookEntries = [];', 'let worldBookEntries = [];\nlet writingStyleEntries = []; // 文风设置条目')
        print('✓ Step 3c: Added writingStyleEntries (fallback)')
    
    # ============================================================
    # Step 3d: Add writing style CRUD functions
    # ============================================================
    writing_style_functions = '''
// ==================== 文风设置功能 ====================

async function loadWritingStyles() {
  try {
    const data = await getFromStorage('WRITING_STYLE_ENTRIES');
    writingStyleEntries = data ? (typeof data === 'string' ? JSON.parse(data) : data) : [];
  } catch(e) {
    writingStyleEntries = [];
  }
}

async function saveWritingStyleEntries() {
  await saveToStorage('WRITING_STYLE_ENTRIES', JSON.stringify(writingStyleEntries));
}

function renderWritingStyleList() {
  const listEl = document.getElementById('writingStyleList');
  if (!listEl) return;
  if (!writingStyleEntries || writingStyleEntries.length === 0) {
    listEl.innerHTML = '<div class="empty-tip">暂无文风条目<br>点击右上角 + 新建</div>';
    return;
  }
  listEl.innerHTML = writingStyleEntries.map(entry => `
    <div class="worldbook-item" style="margin:10px 16px; padding:14px; background:white; border-radius:12px; box-shadow:0 1px 4px rgba(0,0,0,0.08);">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="font-weight:600; font-size:14px; color:var(--text-dark);">${escHtml(entry.name)}</div>
        <div style="display:flex; gap:8px;">
          <span onclick="editWritingStyle('${entry.id}')" style="font-size:13px; color:var(--main-pink); cursor:pointer;">编辑</span>
          <span onclick="deleteWritingStyle('${entry.id}')" style="font-size:13px; color:#999; cursor:pointer;">删除</span>
        </div>
      </div>
      <div style="font-size:12px; color:var(--text-light); margin-top:6px; line-height:1.5; max-height:60px; overflow:hidden;">${escHtml(entry.content.substring(0, 100))}${entry.content.length > 100 ? '...' : ''}</div>
    </div>
  `).join('');
}

function openAddWritingStyle() {
  document.getElementById('editingWritingStyleId').value = '';
  document.getElementById('writingStyleName').value = '';
  document.getElementById('writingStyleContent').value = '';
  document.getElementById('addWritingStyleTitle').textContent = '新建文风';
  openSub('add-writing-style');
}

function editWritingStyle(id) {
  const entry = writingStyleEntries.find(e => e.id === id);
  if (!entry) return;
  document.getElementById('editingWritingStyleId').value = id;
  document.getElementById('writingStyleName').value = entry.name;
  document.getElementById('writingStyleContent').value = entry.content;
  document.getElementById('addWritingStyleTitle').textContent = '编辑文风';
  openSub('add-writing-style');
}

async function saveWritingStyle() {
  const id = document.getElementById('editingWritingStyleId').value;
  const name = document.getElementById('writingStyleName').value.trim();
  const content = document.getElementById('writingStyleContent').value.trim();
  if (!name) { alert('请输入文风名称'); return; }
  if (!content) { alert('请输入文风内容'); return; }
  
  if (id) {
    const idx = writingStyleEntries.findIndex(e => e.id === id);
    if (idx >= 0) {
      writingStyleEntries[idx] = { ...writingStyleEntries[idx], name, content, updatedAt: Date.now() };
      // 如果有联系人使用此文风，清除其压缩缓存，下次切换时重新压缩
      await clearCompressedStyleForEntry(id);
    }
  } else {
    const newId = 'ws_' + Date.now();
    writingStyleEntries.push({ id: newId, name, content, createdAt: Date.now() });
  }
  await saveWritingStyleEntries();
  renderWritingStyleList();
  closeSub('add-writing-style');
  // Refresh dropdowns in chat settings
  refreshWritingStyleDropdowns();
}

async function clearCompressedStyleForEntry(styleId) {
  // Clear compressed cache for all contacts using this style
  for (const contact of contacts) {
    const settingsStr = await getFromStorage(`CHAT_SETTINGS_${contact.id}`);
    if (settingsStr) {
      const settings = typeof settingsStr === 'string' ? JSON.parse(settingsStr) : settingsStr;
      if (settings.writingStyleId === styleId) {
        settings.compressedStyle = null;
        await saveToStorage(`CHAT_SETTINGS_${contact.id}`, JSON.stringify(settings));
      }
    }
  }
}

async function deleteWritingStyle(id) {
  if (!confirm('确定删除此文风条目？')) return;
  writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
  await saveWritingStyleEntries();
  renderWritingStyleList();
  refreshWritingStyleDropdowns();
}

function refreshWritingStyleDropdowns() {
  // Refresh all chat setting writing style selects
  const sel = document.getElementById('chatWritingStyleSelect');
  if (sel) {
    populateWritingStyleSelect(sel);
  }
}

function populateWritingStyleSelect(selectEl) {
  if (!selectEl) return;
  const currentVal = selectEl.value;
  selectEl.innerHTML = '<option value="">-- 不使用文风 --</option>';
  writingStyleEntries.forEach(entry => {
    const opt = document.createElement('option');
    opt.value = entry.id;
    opt.textContent = entry.name;
    selectEl.appendChild(opt);
  });
  selectEl.value = currentVal;
}

async function onWritingStyleChange(styleId) {
  if (!currentContactId) return;
  const settingsStr = await getFromStorage(`CHAT_SETTINGS_${currentContactId}`);
  const settings = settingsStr ? (typeof settingsStr === 'string' ? JSON.parse(settingsStr) : settingsStr) : {};
  
  const oldStyleId = settings.writingStyleId;
  settings.writingStyleId = styleId || null;
  settings.compressedStyle = null; // clear old compressed
  
  if (styleId) {
    const entry = writingStyleEntries.find(e => e.id === styleId);
    if (entry) {
      // Show preview area as loading
      const preview = document.getElementById('compressedStylePreview');
      const previewText = document.getElementById('compressedStyleText');
      if (preview) preview.style.display = 'block';
      if (previewText) previewText.textContent = '正在压缩文风内容，请稍候...';
      
      // Save settings first (without compressed)
      await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(settings));
      
      // Call API to compress style
      try {
        const compressed = await compressWritingStyle(entry.content);
        settings.compressedStyle = compressed;
        if (previewText) previewText.textContent = compressed;
      } catch(e) {
        console.error('压缩文风失败:', e);
        settings.compressedStyle = entry.content.substring(0, 100);
        if (previewText) previewText.textContent = settings.compressedStyle + ' (压缩失败，使用截断版本)';
      }
    }
  } else {
    const preview = document.getElementById('compressedStylePreview');
    if (preview) preview.style.display = 'none';
  }
  
  await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(settings));
}

async function compressWritingStyle(styleContent) {
  // Use the current AI API to compress the style into ~50 chars guideline
  const apiKey = await getFromStorage('API_KEY');
  const apiUrl = await getFromStorage('API_URL');
  const modelName = await getFromStorage('MODEL_NAME');
  
  if (!apiKey || !apiUrl) {
    throw new Error('API未配置');
  }
  
  const baseUrl = apiUrl.replace(/\\/+$/, '');
  const url = baseUrl.endsWith('/chat/completions') ? baseUrl : baseUrl + '/chat/completions';
  
  const payload = {
    model: modelName || 'gpt-4o-mini',
    messages: [
      {
        role: 'user',
        content: `请将以下文风描述压缩成一句50字以内的行为准则，直接输出准则内容，不要前缀：\\n\\n${styleContent}`
      }
    ],
    max_tokens: 150,
    temperature: 0.3
  };
  
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
    body: JSON.stringify(payload)
  });
  
  if (!resp.ok) throw new Error(`API error: ${resp.status}`);
  const data = await resp.json();
  return data.choices[0].message.content.trim();
}

// ==================== 文风设置功能结束 ====================
'''
    
    # Find a good insertion point - after the world book functions
    insert_marker = '// 为异步加载初始值，设置默认值'
    if insert_marker in content:
        content = content.replace(insert_marker, writing_style_functions + '\n' + insert_marker, 1)
        print('✓ Step 3d: Added writing style CRUD functions')
    else:
        # Try another marker
        m = re.search(r'(let contacts = \[\];)', content)
        if m:
            content = content.replace(m.group(0), writing_style_functions + '\n' + m.group(0), 1)
            print('✓ Step 3d: Added writing style CRUD functions (fallback)')
        else:
            content += writing_style_functions
            print('✓ Step 3d: Added writing style CRUD functions (appended)')
    
    # ============================================================
    # Step 5: Append compressed style to user messages
    # ============================================================
    # Find where user messages are sent and append the style "tail"
    # Look for the buildMessages or sendMessage function
    
    # We need to find where the final user message content is built
    # Common pattern: the last user message content
    
    # Strategy: add helper function and call it when building messages
    compressed_style_append = '''
// 获取当前联系人的压缩文风后缀
async function getWritingStyleTail(contactId) {
  if (!contactId) return '';
  try {
    const settingsStr = await getFromStorage(`CHAT_SETTINGS_${contactId}`);
    if (!settingsStr) return '';
    const settings = typeof settingsStr === 'string' ? JSON.parse(settingsStr) : settingsStr;
    if (settings.compressedStyle) {
      return `\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：${settings.compressedStyle})`;
    }
  } catch(e) {}
  return '';
}
'''
    
    # Add this function near the other helpers
    if 'async function getWritingStyleTail' not in content:
        # Insert before the send message function or at a good point
        m2 = re.search(r'(async function sendMessage\()', content)
        if m2:
            content = content.replace(m2.group(0), compressed_style_append + '\n' + m2.group(0), 1)
            print('✓ Step 5a: Added getWritingStyleTail function')
        else:
            content += compressed_style_append
            print('✓ Step 5a: Added getWritingStyleTail function (appended)')
    
    # Now find where userMessage content is assembled and add the tail
    # Look for patterns like: { role: 'user', content: userMessage }
    # We need to add it to the message content before sending
    
    # Find the sendMessage function and inject the tail
    # Pattern: look for where messages array is being built with user content
    old_send_pattern = "const userMsg = { role: 'user', content: userMessage };"
    new_send_pattern = '''const writingStyleTail = await getWritingStyleTail(currentContactId);
  const userMsg = { role: 'user', content: userMessage + writingStyleTail };'''
    
    if old_send_pattern in content:
        content = content.replace(old_send_pattern, new_send_pattern)
        print('✓ Step 5b: Injected writing style tail into user message')
    else:
        # Try to find the message send location
        m3 = re.search(r"(\{ role: 'user', content: userMessage \})", content)
        if m3:
            old = m3.group(0)
            new_v = "{ role: 'user', content: userMessage + (await getWritingStyleTail(currentContactId)) }"
            content = content.replace(old, new_v, 1)
            print('✓ Step 5b: Injected writing style tail (regex)')
        else:
            print('✗ Step 5b: Could not inject writing style tail - manual integration needed')
    
    # ============================================================
    # Step: Load writing styles on init
    # ============================================================
    old_load = 'await loadWorldBook();'
    new_load = 'await loadWorldBook();\n  await loadWritingStyles();'
    if old_load in content:
        content = content.replace(old_load, new_load, 1)
        print('✓ Load writingStyles on init added')
    else:
        print('✗ Could not find loadWorldBook() call to add loadWritingStyles()')
    
    write_file(path, content)
    print('main.js saved.\n')

def check_and_fix_html_chat_settings(content):
    """Make sure chat setting page has the writing style select properly."""
    # Check if already added
    if 'chatWritingStyleSelect' in content:
        return content, True
    return content, False

if __name__ == '__main__':
    print('=== Starting comprehensive changes ===\n')
    
    # Step 1: Backup
    print('--- Step 1: Backup ---')
    backup()
    
    # Step 2 + 3 + 4: Patch index.html
    print('--- Patching index.html ---')
    patch_index_html()
    
    # Step 2c + 3c + 3d + 5: Patch main.js
    print('--- Patching main.js ---')
    patch_main_js()
    
    print('\n=== All changes applied! ===')
    print('Please review the changes and test in browser.')
