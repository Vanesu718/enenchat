#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master implementation script for all 5 steps:
1. Backup
2. World Book UI changes + fix 记忆总结 trigger logic
3. Add 文风设置 page
4. Add 文风单选 in chat settings
5. API compression + append to messages
"""

import os
import shutil
import re
import json
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'

def backup():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bdir = os.path.join(BASE, f'backup_final_{ts}')
    os.makedirs(bdir, exist_ok=True)
    os.makedirs(os.path.join(bdir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(bdir, 'css'), exist_ok=True)
    for f in ['js/main.js', 'index.html']:
        src = os.path.join(BASE, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(bdir, f))
    for f in os.listdir(os.path.join(BASE, 'css')):
        src = os.path.join(BASE, 'css', f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(bdir, 'css', f))
    print(f'Backup done: {bdir}')
    return bdir

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Written: {path}')

def patch_main_js():
    path = os.path.join(BASE, 'js', 'main.js')
    content = read_file(path)
    
    # =========================================================
    # STEP 2a: Replace '语言规范' with '世界观' in worldbook categories
    # =========================================================
    content = content.replace("'语言规范'", "'世界观'")
    content = content.replace('"语言规范"', '"世界观"')
    content = content.replace('语言规范', '世界观')
    
    # =========================================================
    # STEP 2b: Add '其他' category to worldbook category arrays
    # =========================================================
    # Find category arrays like ['记忆总结', '世界观'] and add '其他'
    # Pattern: arrays with worldbook categories
    def add_qita_to_array(m):
        arr = m.group(0)
        if '其他' not in arr:
            # Insert '其他' before the closing bracket
            arr = arr.rstrip(']').rstrip() + ", '其他']"
        return arr
    
    # Replace category arrays in worldbook sections
    content = re.sub(
        r"\['记忆总结',\s*'世界观'\]",
        "['记忆总结', '世界观', '其他']",
        content
    )
    content = re.sub(
        r"\[\"记忆总结\",\s*\"世界观\"\]",
        '["记忆总结", "世界观", "其他"]',
        content
    )
    
    # =========================================================
    # STEP 2c: Fix 记忆总结 trigger logic
    # =========================================================
    # Find where worldbook entries are processed for injection
    # 记忆总结 should only trigger if explicitly enabled for current contact
    
    # Look for the worldbook injection logic pattern
    # We need to find where worldbook entries are gathered and fix 记忆总结 behavior
    
    # Pattern: typically entries with category '记忆总结' are always injected
    # We change this so they only inject if contact's worldBookEnabled includes the entry id
    
    # Find the getWorldBookContext or similar function
    # Replace the filter logic for 记忆总结 entries
    
    # Search for common patterns of worldbook context building
    patterns_to_fix = [
        # Pattern 1: entry.category === '记忆总结' always included
        (
            r"entry\.category\s*===\s*['\"]记忆总结['\"]",
            "entry.category === '记忆总结' && isWorldBookEnabledForContact(entry, currentContactId)"
        ),
    ]
    
    for old_pat, new_str in patterns_to_fix:
        content = re.sub(old_pat, new_str, content)
    
    # =========================================================
    # STEP 3: Add writingStyleEntries storage + functions
    # =========================================================
    
    # Add after the worldbook data initialization or near contacts init
    writing_style_init = '''
// ============================================================
// 文风设置 - Writing Style System
// ============================================================
function getWritingStyleEntries() {
    try {
        const data = localStorage.getItem('writingStyleEntries');
        return data ? JSON.parse(data) : [];
    } catch(e) {
        return [];
    }
}

function saveWritingStyleEntries(entries) {
    localStorage.setItem('writingStyleEntries', JSON.stringify(entries));
}

function addWritingStyleEntry(entry) {
    const entries = getWritingStyleEntries();
    entry.id = 'ws_' + Date.now() + '_' + Math.random().toString(36).substr(2,6);
    entry.createdAt = new Date().toISOString();
    entries.push(entry);
    saveWritingStyleEntries(entries);
    return entry;
}

function updateWritingStyleEntry(id, updates) {
    const entries = getWritingStyleEntries();
    const idx = entries.findIndex(e => e.id === id);
    if (idx >= 0) {
        entries[idx] = Object.assign(entries[idx], updates, {updatedAt: new Date().toISOString()});
        saveWritingStyleEntries(entries);
        return entries[idx];
    }
    return null;
}

function deleteWritingStyleEntry(id) {
    const entries = getWritingStyleEntries().filter(e => e.id !== id);
    saveWritingStyleEntries(entries);
}

function getContactWritingStyle(contactId) {
    try {
        const data = localStorage.getItem('contactWritingStyle_' + contactId);
        return data ? JSON.parse(data) : null;
    } catch(e) {
        return null;
    }
}

function saveContactWritingStyle(contactId, styleData) {
    localStorage.setItem('contactWritingStyle_' + contactId, JSON.stringify(styleData));
}

function isWorldBookEnabledForContact(entry, contactId) {
    if (!contactId) return false;
    try {
        const key = 'worldbook_enabled_' + contactId;
        const data = localStorage.getItem(key);
        if (!data) return false;
        const enabled = JSON.parse(data);
        return Array.isArray(enabled) && enabled.includes(entry.id);
    } catch(e) {
        return false;
    }
}

function toggleWorldBookForContact(entryId, contactId, enabled) {
    const key = 'worldbook_enabled_' + contactId;
    let list = [];
    try {
        const data = localStorage.getItem(key);
        if (data) list = JSON.parse(data);
    } catch(e) {}
    if (enabled) {
        if (!list.includes(entryId)) list.push(entryId);
    } else {
        list = list.filter(id => id !== entryId);
    }
    localStorage.setItem(key, JSON.stringify(list));
}

async function compressWritingStyle(apiKey, apiUrl, model, styleContent) {
    const prompt = `请将以下文风描述压缩成一句不超过50字的精简行为准则，只输出结果，不要解释：\\n\\n${styleContent}`;
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + apiKey
            },
            body: JSON.stringify({
                model: model,
                messages: [{role: 'user', content: prompt}],
                max_tokens: 100,
                temperature: 0.3
            })
        });
        const data = await response.json();
        if (data.choices && data.choices[0]) {
            return data.choices[0].message.content.trim();
        }
    } catch(e) {
        console.error('压缩文风失败:', e);
    }
    return styleContent.substring(0, 50);
}
'''
    
    # Find a good insertion point - after 'use strict' or at the start of the file after comments
    # Insert after the first function definition or near the top utility functions
    insert_marker = '// ============================================================\n// 文风设置 - Writing Style System'
    if insert_marker not in content:
        # Find insertion point - after localStorage or worldbook functions
        # Try to find after getWorldBookEntries or similar
        match = re.search(r'(function\s+getWorldBook[^}]+\})', content, re.DOTALL)
        if match:
            pos = match.end()
            content = content[:pos] + '\n' + writing_style_init + '\n' + content[pos:]
        else:
            # Insert near the top after any 'use strict'
            match = re.search(r"'use strict';?\s*\n", content)
            if match:
                pos = match.end()
                content = content[:pos] + writing_style_init + '\n' + content[pos:]
            else:
                content = writing_style_init + '\n' + content
    
    # =========================================================
    # STEP 5: Append compressed style to user messages
    # =========================================================
    # Find where user messages are sent to API and append style
    # Look for the message construction before API call
    
    # Pattern: where messages array is built for API, add style injection
    style_injection_code = '''
    // 文风附着 - append compressed writing style
    if (typeof currentContactId !== 'undefined' && currentContactId) {
        const wsData = getContactWritingStyle(currentContactId);
        if (wsData && wsData.compressed) {
            // Find last user message and append style
            for (let i = messages.length - 1; i >= 0; i--) {
                if (messages[i].role === 'user') {
                    messages[i] = Object.assign({}, messages[i], {
                        content: messages[i].content + '\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：' + wsData.compressed + ')'
                    });
                    break;
                }
            }
        }
    }'''
    
    # Find where API is called with messages array
    # Look for fetch call to API or similar
    api_call_patterns = [
        r'(const\s+messages\s*=\s*\[[\s\S]*?\];)\s*\n(\s*(?:const|let|var)\s+response\s*=\s*await\s+fetch)',
        r'(messages\.push\([^)]+\);)\s*\n(\s*(?:const|let)\s+response\s*=\s*await)',
    ]
    
    injected = False
    for pat in api_call_patterns:
        match = re.search(pat, content)
        if match:
            insert_pos = match.start(2)
            content = content[:insert_pos] + style_injection_code + '\n    ' + content[insert_pos:]
            injected = True
            print('Style injection inserted at API call point')
            break
    
    if not injected:
        print('WARNING: Could not find API call pattern for style injection - will need manual check')
    
    write_file(path, content)
    print('main.js patched successfully')

def patch_index_html():
    path = os.path.join(BASE, 'index.html')
    content = read_file(path)
    
    # =========================================================
    # STEP 2: Update worldbook category tabs in HTML
    # =========================================================
    content = content.replace('语言规范', '世界观')
    
    # Add '其他' tab to worldbook filter tabs if not present
    # Find the worldbook tabs section
    if '其他' not in content:
        # Add after 世界观 tab
        content = re.sub(
            r'(<button[^>]*data-category=["\']世界观["\'][^>]*>世界观</button>)',
            r'\1\n                        <button class="wb-tab-btn" data-category="其他">其他</button>',
            content
        )
    
    # =========================================================
    # STEP 3: Add 文风设置 menu item in contacts
    # =========================================================
    writing_style_menu_item = '''
            <!-- 文风设置 -->
            <li class="menu-item" id="menu-writing-style" onclick="showWritingStylePage()">
                <span class="menu-icon">✍️</span>
                <span class="menu-text">文风设置</span>
            </li>'''
    
    # Find worldbook menu item and insert after it
    wb_pattern = r'(</li>\s*\n)(\s*<!-- (?:联系人|通讯录|contacts))'
    match = re.search(wb_pattern, content)
    
    # Try to find the contacts/menu list area
    if 'menu-writing-style' not in content:
        # Find worldbook or settings menu item
        patterns = [
            r'(id=["\']menu-worldbook["\'][^>]*>[\s\S]*?</li>)',
            r'(id=["\']menu-settings["\'][^>]*>[\s\S]*?</li>)',
            r'(<li[^>]*>\s*<span[^>]*>🌍[^<]*</span>[\s\S]*?</li>)',
            r'(<li[^>]*>\s*<span[^>]*>📖[^<]*</span>[\s\S]*?</li>)',
        ]
        inserted = False
        for pat in patterns:
            m = re.search(pat, content)
            if m:
                pos = m.end()
                content = content[:pos] + writing_style_menu_item + content[pos:]
                inserted = True
                print('Writing style menu item inserted')
                break
        if not inserted:
            print('WARNING: Could not find worldbook menu item - writing style menu not inserted in nav')
    
    # =========================================================
    # STEP 3: Add 文风设置 page HTML
    # =========================================================
    writing_style_page_html = '''
    <!-- 文风设置页面 -->
    <div id="writing-style-page" class="page" style="display:none;">
        <div class="page-header">
            <button class="back-btn" onclick="hidePage('writing-style-page')">←</button>
            <h2>文风设置</h2>
            <button class="add-btn" onclick="showAddWritingStyleModal()">+ 新建</button>
        </div>
        <div class="writing-style-list" id="writing-style-list">
            <!-- entries rendered here -->
        </div>
    </div>
    
    <!-- 文风新增/编辑弹窗 -->
    <div id="writing-style-modal" class="modal" style="display:none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="ws-modal-title">新建文风</h3>
                <button class="close-btn" onclick="closeWritingStyleModal()">✕</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>文风名称</label>
                    <input type="text" id="ws-name-input" placeholder="例如：温柔甜宠风" />
                </div>
                <div class="form-group">
                    <label>文风内容</label>
                    <textarea id="ws-content-input" rows="10" placeholder="详细描述文风特征、行为规范、语气要求等..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-cancel" onclick="closeWritingStyleModal()">取消</button>
                <button class="btn-save" onclick="saveWritingStyleModal()">保存</button>
            </div>
        </div>
    </div>'''
    
    if 'writing-style-page' not in content:
        # Insert before </body>
        content = content.replace('</body>', writing_style_page_html + '\n</body>')
        print('Writing style page HTML inserted')
    
    # =========================================================
    # STEP 4: Add 文风单选 in chat settings HTML
    # =========================================================
    writing_style_selector_html = '''
                <!-- 文风选择 -->
                <div class="setting-group" id="writing-style-selector-group">
                    <label class="setting-label">当前聊天文风</label>
                    <div class="setting-warning" style="color:#e74c3c;font-size:12px;margin-bottom:8px;">
                        ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，每切换一次都会调用一次 API。
                    </div>
                    <select id="chat-writing-style-select" class="setting-select" onchange="onWritingStyleChanged(this.value)">
                        <option value="">-- 不使用文风 --</option>
                    </select>
                    <div id="writing-style-status" style="font-size:12px;color:#888;margin-top:4px;"></div>
                </div>'''
    
    if 'writing-style-selector-group' not in content:
        # Find chat settings area - look for existing setting groups
        patterns = [
            r'(id=["\']chat-settings["\'][\s\S]*?<div[^>]*class=["\']setting-group["\'])',
            r'(<div[^>]*id=["\']chat-settings-panel["\'][\s\S]*?<div[^>]*class=["\']setting)',
            r'(<!-- 聊天设置[\s\S]*?<div[^>]*class=["\']setting-group)',
        ]
        inserted = False
        for pat in patterns:
            m = re.search(pat, content)
            if m:
                pos = m.end()
                content = content[:pos] + '\n' + writing_style_selector_html + content[pos:]
                inserted = True
                print('Writing style selector inserted in chat settings')
                break
        
        if not inserted:
            # Try to find the chat settings section by common patterns
            m = re.search(r'(记忆总结|memory-summary|jailbreak|越狱|setting-group)', content)
            if m:
                # Find the containing setting group
                start = content.rfind('<div', 0, m.start())
                if start >= 0:
                    end = content.find('</div>', m.end()) + 6
                    content = content[:end] + '\n' + writing_style_selector_html + content[end:]
                    inserted = True
                    print('Writing style selector inserted near memory settings')
            
            if not inserted:
                print('WARNING: Could not find chat settings area for writing style selector')
    
    # =========================================================
    # STEP 2: Add worldbook enable checkboxes in chat settings
    # =========================================================
    worldbook_contact_settings_html = '''
                <!-- 世界书-联系人启用设置 (记忆总结条目) -->
                <div class="setting-group" id="worldbook-contact-settings-group">
                    <label class="setting-label">世界书-记忆总结</label>
                    <div style="font-size:12px;color:#888;margin-bottom:8px;">
                        勾选后，该世界书条目将对此联系人常驻注入上下文
                    </div>
                    <div id="worldbook-contact-checkboxes">
                        <!-- rendered by renderWorldBookContactSettings() -->
                    </div>
                </div>'''
    
    if 'worldbook-contact-settings-group' not in content:
        # Insert in chat settings
        if 'writing-style-selector-group' in content:
            content = content.replace(
                '<!-- 文风选择 -->',
                worldbook_contact_settings_html + '\n                <!-- 文风选择 -->'
            )
            print('Worldbook contact settings inserted')
    
    write_file(path, content)
    print('index.html patched successfully')

def add_js_functions():
    """Add UI functions for writing style to main.js"""
    path = os.path.join(BASE, 'js', 'main.js')
    content = read_file(path)
    
    new_functions = '''
// ============================================================
// 文风设置 UI Functions
// ============================================================

function showWritingStylePage() {
    // Hide all pages first
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    const page = document.getElementById('writing-style-page');
    if (page) {
        page.style.display = 'flex';
        renderWritingStyleList();
    }
}

function renderWritingStyleList() {
    const container = document.getElementById('writing-style-list');
    if (!container) return;
    const entries = getWritingStyleEntries();
    if (entries.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:#888;padding:40px;">暂无文风条目，点击右上角新建</div>';
        return;
    }
    container.innerHTML = entries.map(entry => `
        <div class="ws-entry-card" data-id="${entry.id}">
            <div class="ws-entry-header">
                <span class="ws-entry-name">${escapeHtml(entry.name || '未命名')}</span>
                <div class="ws-entry-actions">
                    <button onclick="editWritingStyleEntry('${entry.id}')">编辑</button>
                    <button onclick="deleteWritingStyleEntryUI('${entry.id}')">删除</button>
                </div>
            </div>
            <div class="ws-entry-preview">${escapeHtml((entry.content || '').substring(0, 100))}${(entry.content || '').length > 100 ? '...' : ''}</div>
        </div>
    `).join('');
}

function showAddWritingStyleModal() {
    document.getElementById('ws-modal-title').textContent = '新建文风';
    document.getElementById('ws-name-input').value = '';
    document.getElementById('ws-content-input').value = '';
    document.getElementById('writing-style-modal').setAttribute('data-edit-id', '');
    document.getElementById('writing-style-modal').style.display = 'flex';
}

function editWritingStyleEntry(id) {
    const entries = getWritingStyleEntries();
    const entry = entries.find(e => e.id === id);
    if (!entry) return;
    document.getElementById('ws-modal-title').textContent = '编辑文风';
    document.getElementById('ws-name-input').value = entry.name || '';
    document.getElementById('ws-content-input').value = entry.content || '';
    document.getElementById('writing-style-modal').setAttribute('data-edit-id', id);
    document.getElementById('writing-style-modal').style.display = 'flex';
}

function closeWritingStyleModal() {
    document.getElementById('writing-style-modal').style.display = 'none';
}

function saveWritingStyleModal() {
    const name = document.getElementById('ws-name-input').value.trim();
    const content = document.getElementById('ws-content-input').value.trim();
    if (!name) { alert('请输入文风名称'); return; }
    if (!content) { alert('请输入文风内容'); return; }
    
    const editId = document.getElementById('writing-style-modal').getAttribute('data-edit-id');
    if (editId) {
        updateWritingStyleEntry(editId, {name, content});
    } else {
        addWritingStyleEntry({name, content});
    }
    closeWritingStyleModal();
    renderWritingStyleList();
}

function deleteWritingStyleEntryUI(id) {
    if (!confirm('确定删除该文风条目？')) return;
    deleteWritingStyleEntry(id);
    renderWritingStyleList();
}

function escapeHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ============================================================
// 文风单选 - Chat Settings Writing Style Selector
// ============================================================

function renderWritingStyleSelector(contactId) {
    const sel = document.getElementById('chat-writing-style-select');
    if (!sel) return;
    const entries = getWritingStyleEntries();
    sel.innerHTML = '<option value="">-- 不使用文风 --</option>' +
        entries.map(e => `<option value="${e.id}">${escapeHtml(e.name)}</option>`).join('');
    
    // Set current selection
    const current = getContactWritingStyle(contactId);
    if (current && current.styleId) {
        sel.value = current.styleId;
    }
    
    // Show compressed status
    const status = document.getElementById('writing-style-status');
    if (status && current && current.compressed) {
        status.textContent = '已压缩：' + current.compressed;
    }
}

async function onWritingStyleChanged(styleId) {
    const contactId = getCurrentContactId();
    if (!contactId) return;
    
    if (!styleId) {
        saveContactWritingStyle(contactId, null);
        const status = document.getElementById('writing-style-status');
        if (status) status.textContent = '';
        return;
    }
    
    const entries = getWritingStyleEntries();
    const entry = entries.find(e => e.id === styleId);
    if (!entry) return;
    
    const status = document.getElementById('writing-style-status');
    if (status) status.textContent = '正在调用 API 压缩文风...';
    
    try {
        // Get API settings
        const apiKey = localStorage.getItem('apiKey') || '';
        const apiUrl = localStorage.getItem('apiUrl') || 'https://api.openai.com/v1/chat/completions';
        const model = localStorage.getItem('model') || 'gpt-3.5-turbo';
        
        const compressed = await compressWritingStyle(apiKey, apiUrl, model, entry.content);
        saveContactWritingStyle(contactId, {
            styleId: styleId,
            styleName: entry.name,
            compressed: compressed,
            updatedAt: new Date().toISOString()
        });
        
        if (status) status.textContent = '✅ 已压缩：' + compressed;
    } catch(e) {
        if (status) status.textContent = '❌ 压缩失败：' + e.message;
        console.error('Writing style compression failed:', e);
    }
}

function getCurrentContactId() {
    // Try common patterns to get current contact id
    if (typeof currentContactId !== 'undefined') return currentContactId;
    if (typeof currentChatId !== 'undefined') return currentChatId;
    const el = document.querySelector('[data-contact-id]');
    return el ? el.getAttribute('data-contact-id') : null;
}

// ============================================================
// 世界书-联系人设置 UI
// ============================================================

function renderWorldBookContactSettings(contactId) {
    const container = document.getElementById('worldbook-contact-checkboxes');
    if (!container) return;
    
    const entries = typeof getWorldBookEntries === 'function' ? getWorldBookEntries() : [];
    const memoryEntries = entries.filter(e => e.category === '记忆总结');
    
    if (memoryEntries.length === 0) {
        container.innerHTML = '<div style="color:#888;font-size:12px;">暂无记忆总结条目</div>';
        return;
    }
    
    container.innerHTML = memoryEntries.map(entry => {
        const enabled = isWorldBookEnabledForContact(entry, contactId);
        return `<div style="margin:4px 0;">
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                <input type="checkbox" ${enabled ? 'checked' : ''} 
                    onchange="toggleWorldBookForContact('${entry.id}', '${contactId}', this.checked)">
                <span>${escapeHtml(entry.keyword || entry.title || entry.id)}</span>
            </label>
        </div>`;
    }).join('');
}
'''
    
    if 'showWritingStylePage' not in content:
        content = content + '\n' + new_functions
        write_file(path, content)
        print('JS functions added to main.js')
    else:
        print('JS functions already exist in main.js')

def add_css_styles():
    """Add CSS for writing style UI"""
    path = os.path.join(BASE, 'css', 'index-main.css')
    content = read_file(path)
    
    new_css = '''
/* ============================================================
   文风设置 Styles
   ============================================================ */

#writing-style-page {
    flex-direction: column;
    background: var(--bg-primary, #fff);
}

#writing-style-page .page-header {
    display: flex;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--border-color, #eee);
    gap: 12px;
}

#writing-style-page .page-header h2 {
    flex: 1;
    margin: 0;
    font-size: 18px;
}

#writing-style-page .add-btn {
    padding: 6px 14px;
    background: var(--accent-color, #07c160);
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}

.writing-style-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
}

.ws-entry-card {
    background: var(--bg-secondary, #f9f9f9);
    border: 1px solid var(--border-color, #eee);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
}

.ws-entry-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}

.ws-entry-name {
    font-weight: bold;
    font-size: 15px;
}

.ws-entry-actions {
    display: flex;
    gap: 6px;
}

.ws-entry-actions button {
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid var(--border-color, #ddd);
    background: var(--bg-primary, #fff);
    cursor: pointer;
    font-size: 13px;
}

.ws-entry-preview {
    font-size: 13px;
    color: var(--text-secondary, #888);
    line-height: 1.4;
}

/* Modal styles for writing style */
#writing-style-modal {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

#writing-style-modal .modal-content {
    background: var(--bg-primary, #fff);
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

#writing-style-modal .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border-bottom: 1px solid var(--border-color, #eee);
}

#writing-style-modal .modal-header h3 {
    margin: 0;
    font-size: 16px;
}

#writing-style-modal .modal-body {
    padding: 16px;
    overflow-y: auto;
    flex: 1;
}

#writing-style-modal .form-group {
    margin-bottom: 16px;
}

#writing-style-modal .form-group label {
    display: block;
    margin-bottom: 6px;
    font-size: 14px;
    color: var(--text-primary, #333);
}

#writing-style-modal .form-group input,
#writing-style-modal .form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid var(--border-color, #ddd);
    border-radius: 6px;
    font-size: 14px;
    box-sizing: border-box;
    font-family: inherit;
    resize: vertical;
}

#writing-style-modal .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 12px 16px;
    border-top: 1px solid var(--border-color, #eee);
}

#writing-style-modal .btn-cancel {
    padding: 8px 20px;
    border-radius: 6px;
    border: 1px solid var(--border-color, #ddd);
    background: var(--bg-primary, #fff);
    cursor: pointer;
}

#writing-style-modal .btn-save {
    padding: 8px 20px;
    border-radius: 6px;
    border: none;
    background: var(--accent-color, #07c160);
    color: #fff;
    cursor: pointer;
}

.setting-warning {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
    padding: 6px 10px;
}
'''
    
    if 'writing-style-list' not in content:
        content = content + '\n' + new_css
        write_file(path, content)
        print('CSS added to index-main.css')
    else:
        print('CSS already exists')

def main():
    print('='*60)
    print('Starting master implementation...')
    print('='*60)
    
    # Step 1: Backup
    backup()
    
    # Step 2 & 3 & 4 & 5: Patch main.js
    patch_main_js()
    
    # Steps 2-4: Patch index.html
    patch_index_html()
    
    # Step 3: Add JS UI functions
    add_js_functions()
    
    # Add CSS
    add_css_styles()
    
    print('='*60)
    print('Implementation complete!')
    print('='*60)

if __name__ == '__main__':
    main()
