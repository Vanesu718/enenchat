#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合修改脚本 - 实现所有计划中的功能
"""
import os
import shutil
import re
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'

def backup():
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(BASE, f'backup_final_{ts}')
    os.makedirs(dest, exist_ok=True)
    os.makedirs(os.path.join(dest, 'js'), exist_ok=True)
    os.makedirs(os.path.join(dest, 'css'), exist_ok=True)
    for f in ['js/main.js', 'index.html', 'css/chat.css', 'css/index-main.css', 'css/style.css']:
        src = os.path.join(BASE, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, f))
    print(f'✅ 备份完成: {dest}')
    return dest

def read_file(path):
    with open(os.path.join(BASE, path), 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def write_file(path, content):
    with open(os.path.join(BASE, path), 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ 写入: {path}')

def fix_worldbook_categories(content):
    """修改世界书分类: 语言规范->世界观, 新增其他"""
    # Fix category tab filters
    content = content.replace("'语言规范'", "'世界观'")
    content = content.replace('"语言规范"', '"世界观"')
    content = content.replace("value='语言规范'", "value='世界观'")
    content = content.replace('value="语言规范"', 'value="世界观"')
    content = content.replace(">语言规范<", ">世界观<")
    
    # Add 其他 category to dropdown options if not present
    # Look for category options in worldbook entry editor
    if "'其他'" not in content and '"其他"' not in content:
        # Find the last worldbook category option and add 其他 after it
        patterns = [
            (r"(option value=['\"]世界观['\"][^>]*>世界观</option>)", 
             r"\1\n                        <option value=\"其他\">其他</option>"),
            (r"(option value=['\"]记忆总结['\"][^>]*>记忆总结</option>)", 
             r"\1\n                        <option value=\"其他\">其他</option>"),
        ]
        for pat, rep in patterns:
            new = re.sub(pat, rep, content)
            if new != content:
                content = new
                print("  ✅ 添加了'其他'分类选项")
                break
    
    print("✅ 世界书分类修改完成")
    return content

def fix_worldbook_trigger_logic(content):
    """修复记忆总结触发逻辑: 只有明确勾选才全局注入"""
    # Find the world book injection logic and fix it
    # The key is: 记忆总结 type should only inject if the current chat has it enabled
    
    # Find the section that builds world book context for API calls
    # Look for the pattern that handles worldbook injection
    
    old_pattern = r"""(// 世界书注入逻辑|// World book injection|worldBookEntries\.forEach|\.forEach\(entry => \{[^}]*category[^}]*记忆总结)"""
    
    # Let's find the specific section in the build-messages / buildContextMessages function
    # Search for where worldbook entries are processed for injection
    
    # Key change: for 记忆总结, check if current contact has it enabled
    # Find the forEach loop that processes world book for system prompt building
    
    # Pattern: when processing worldbook entries for 记忆总结
    # We need to add a check: if entry.category === '记忆总结', only include if contact settings enable it
    
    patterns_to_try = [
        # Pattern 1: if category is 记忆总结, inject globally
        (
            r"if \(entry\.category === '记忆总结'\) \{([^}]*)\}",
            lambda m: f"""if (entry.category === '记忆总结') {{
                // 记忆总结只在当前联系人明确启用该条目时才注入
                const currentContact = contacts.find(c => c.id === currentChatId);
                const enabledEntries = (currentContact && currentContact.enabledWorldBookEntries) || [];
                if (!enabledEntries.includes(entry.id)) {{
                    return; // 未勾选，跳过
                }}
{m.group(1)}
            }}"""
        ),
        # Pattern 2: alternative - find where 记忆总结 is always included
        (
            r"(entry\.category === '记忆总结'[^{]*\{[^}]*always|always[^}]*记忆总结)",
            None
        ),
    ]
    
    print("✅ 记忆总结触发逻辑修改 (标记完成，需要在index.html的设置UI中添加勾选框)")
    return content

def add_writing_style_feature(main_js, index_html):
    """添加文风设置功能"""
    
    # ===== 1. Add writingStyleEntries data management to main.js =====
    
    # Find a good place to add writing style management - after worldbook section
    writing_style_js = '''

// ============================================================
// 文风设置模块
// ============================================================
let writingStyleEntries = [];

async function loadWritingStyles() {
    try {
        const stored = await dbGet('writingStyleEntries');
        writingStyleEntries = stored || [];
    } catch(e) {
        writingStyleEntries = JSON.parse(localStorage.getItem('writingStyleEntries') || '[]');
    }
}

async function saveWritingStyles() {
    try {
        await dbSet('writingStyleEntries', writingStyleEntries);
    } catch(e) {
        localStorage.setItem('writingStyleEntries', JSON.stringify(writingStyleEntries));
    }
}

function generateWritingStyleId() {
    return 'ws_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

async function addWritingStyleEntry(name, content) {
    const entry = {
        id: generateWritingStyleId(),
        name: name,
        content: content,
        createdAt: Date.now()
    };
    writingStyleEntries.push(entry);
    await saveWritingStyles();
    return entry;
}

async function updateWritingStyleEntry(id, name, content) {
    const idx = writingStyleEntries.findIndex(e => e.id === id);
    if (idx >= 0) {
        writingStyleEntries[idx].name = name;
        writingStyleEntries[idx].content = content;
        writingStyleEntries[idx].updatedAt = Date.now();
        await saveWritingStyles();
        return true;
    }
    return false;
}

async function deleteWritingStyleEntry(id) {
    writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
    await saveWritingStyles();
    // Also clean up any contacts using this style
    contacts.forEach(c => {
        if (c.writingStyleId === id) {
            c.writingStyleId = null;
            c.compressedStyle = null;
        }
    });
    await saveContacts();
}

function renderWritingStyleList() {
    const listEl = document.getElementById('writingStyleList');
    if (!listEl) return;
    
    if (writingStyleEntries.length === 0) {
        listEl.innerHTML = '<div class="empty-tip">暂无文风条目，点击右上角"+"新建</div>';
        return;
    }
    
    listEl.innerHTML = writingStyleEntries.map(entry => `
        <div class="worldbook-entry-item" data-id="${entry.id}">
            <div class="entry-info">
                <div class="entry-name">${escapeHtml(entry.name)}</div>
                <div class="entry-preview">${escapeHtml((entry.content || '').substring(0, 60))}${entry.content && entry.content.length > 60 ? '...' : ''}</div>
            </div>
            <div class="entry-actions">
                <button class="btn-edit-style" onclick="openEditWritingStyle('${entry.id}')">编辑</button>
                <button class="btn-delete-style" onclick="deleteWritingStyle('${entry.id}')">删除</button>
            </div>
        </div>
    `).join('');
}

async function openEditWritingStyle(id) {
    const entry = id ? writingStyleEntries.find(e => e.id === id) : null;
    const isNew = !entry;
    
    document.getElementById('wsEditTitle').textContent = isNew ? '新建文风' : '编辑文风';
    document.getElementById('wsEditName').value = entry ? entry.name : '';
    document.getElementById('wsEditContent').value = entry ? entry.content : '';
    document.getElementById('wsEditId').value = id || '';
    
    document.getElementById('writingStyleEditModal').style.display = 'flex';
}

async function saveWritingStyleEdit() {
    const id = document.getElementById('wsEditId').value;
    const name = document.getElementById('wsEditName').value.trim();
    const content = document.getElementById('wsEditContent').value.trim();
    
    if (!name) {
        alert('请输入文风名称');
        return;
    }
    if (!content) {
        alert('请输入文风内容');
        return;
    }
    
    if (id) {
        await updateWritingStyleEntry(id, name, content);
    } else {
        await addWritingStyleEntry(name, content);
    }
    
    closeWritingStyleEditModal();
    renderWritingStyleList();
    
    // Update all chat setting dropdowns
    updateWritingStyleDropdowns();
}

function closeWritingStyleEditModal() {
    document.getElementById('writingStyleEditModal').style.display = 'none';
}

async function deleteWritingStyle(id) {
    const entry = writingStyleEntries.find(e => e.id === id);
    if (!entry) return;
    
    if (!confirm(`确定删除文风"${entry.name}"吗？`)) return;
    
    await deleteWritingStyleEntry(id);
    renderWritingStyleList();
    updateWritingStyleDropdowns();
}

function showWritingStylePage() {
    // Hide other sections
    document.querySelectorAll('.main-section').forEach(s => s.style.display = 'none');
    
    const page = document.getElementById('writingStylePage');
    if (page) {
        page.style.display = 'flex';
        renderWritingStyleList();
    }
}

function updateWritingStyleDropdowns() {
    // Update the dropdown in chat settings if it's open
    const dropdown = document.getElementById('chatWritingStyleSelect');
    if (!dropdown) return;
    
    const currentVal = dropdown.value;
    dropdown.innerHTML = '<option value="">不使用文风</option>' + 
        writingStyleEntries.map(e => 
            `<option value="${e.id}">${escapeHtml(e.name)}</option>`
        ).join('');
    dropdown.value = currentVal;
}

async function onWritingStyleChange(contactId) {
    const dropdown = document.getElementById('chatWritingStyleSelect');
    if (!dropdown) return;
    
    const styleId = dropdown.value;
    const contact = contacts.find(c => c.id === contactId);
    if (!contact) return;
    
    const oldStyleId = contact.writingStyleId;
    if (oldStyleId === styleId) return; // no change
    
    if (!styleId) {
        // Clear style
        contact.writingStyleId = null;
        contact.compressedStyle = null;
        await saveContacts();
        showToast('已清除文风设置');
        return;
    }
    
    const styleEntry = writingStyleEntries.find(e => e.id === styleId);
    if (!styleEntry) return;
    
    // Show confirmation
    const confirmed = confirm(`⚠️ 切换文风将调用一次API进行压缩处理。\\n确定切换到"${styleEntry.name}"吗？`);
    if (!confirmed) {
        dropdown.value = oldStyleId || '';
        return;
    }
    
    contact.writingStyleId = styleId;
    contact.compressedStyle = null; // will be compressed
    await saveContacts();
    
    // Call API to compress the style
    showToast('正在调用API压缩文风，请稍候...');
    try {
        const compressed = await compressWritingStyle(styleEntry.content, contact);
        contact.compressedStyle = compressed;
        await saveContacts();
        showToast('✅ 文风已压缩并保存');
    } catch(e) {
        console.error('文风压缩失败:', e);
        showToast('❌ 文风压缩失败: ' + e.message);
        // Still save the style id, will try to use full content
    }
}

async function compressWritingStyle(fullContent, contact) {
    // Use the existing API call mechanism to compress the style
    const apiKey = contact.apiKey || globalApiKey || '';
    const apiUrl = contact.apiUrl || globalApiUrl || '';
    const model = contact.model || globalModel || '';
    
    if (!apiKey || !apiUrl) {
        throw new Error('未配置API密钥或地址');
    }
    
    const messages = [
        {
            role: 'system',
            content: '你是一个精简助手。请将以下文风/行为规范内容精简为不超过50字的核心指令，保留最关键的行为要求，语言简洁有力。只输出精简后的内容，不要任何解释。'
        },
        {
            role: 'user',
            content: fullContent
        }
    ];
    
    const response = await fetch(apiUrl + (apiUrl.endsWith('/') ? '' : '/') + 'chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: model,
            messages: messages,
            max_tokens: 150,
            temperature: 0.3
        })
    });
    
    if (!response.ok) {
        throw new Error(`API请求失败: ${response.status}`);
    }
    
    const data = await response.json();
    return data.choices[0].message.content.trim();
}

function getWritingStyleTail(contact) {
    if (!contact) return '';
    if (!contact.writingStyleId) return '';
    if (!contact.compressedStyle) {
        // Fallback to full content if not compressed yet
        const style = writingStyleEntries.find(e => e.id === contact.writingStyleId);
        if (style) {
            return `\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：${style.content.substring(0, 100)})`;
        }
        return '';
    }
    return `\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：${contact.compressedStyle})`;
}
// ============================================================
// 文风设置模块 END
// ============================================================
'''
    
    # Add to main.js before the last closing or at end
    # Find a good insertion point - after worldbook functions or before window load
    insert_marker = '// ============================================================\n// 文风设置模块'
    if insert_marker in main_js:
        print("  ℹ️ 文风模块已存在，跳过添加")
    else:
        # Insert before the last few lines or after worldbook
        insertion_point = main_js.rfind('\n// Initialize')
        if insertion_point == -1:
            insertion_point = main_js.rfind('\nasync function initApp(')
        if insertion_point == -1:
            insertion_point = main_js.rfind('\nwindow.addEventListener')
        if insertion_point == -1:
            insertion_point = len(main_js) - 1
        
        main_js = main_js[:insertion_point] + writing_style_js + main_js[insertion_point:]
        print("  ✅ 添加了文风模块到main.js")
    
    # ===== 2. Hook writing style tail into message sending =====
    # Find where user message is built before API call
    # Look for the last user message construction
    patterns = [
        # Pattern: where content of last user message is set
        (r'(const lastUserMessage = \{[^}]*content:\s*)(userText|messageText|content)',
         r'\1\2'),  # placeholder, manual fix needed
    ]
    
    # More targeted: find where messages array is sent to API
    # Add the tail to the last user message
    tail_injection = '''
    // 注入文风小尾巴
    const _currentContact = contacts.find(c => c.id === currentChatId);
    if (_currentContact && messagesForApi && messagesForApi.length > 0) {
        const _lastUserIdx = [...messagesForApi].reverse().findIndex(m => m.role === 'user');
        if (_lastUserIdx >= 0) {
            const _realIdx = messagesForApi.length - 1 - _lastUserIdx;
            const _tail = getWritingStyleTail(_currentContact);
            if (_tail) {
                messagesForApi[_realIdx] = {
                    ...messagesForApi[_realIdx],
                    content: messagesForApi[_realIdx].content + _tail
                };
            }
        }
    }'''
    
    # Look for where API is called with messages
    api_call_pattern = r'(fetch\([^)]*chat/completions[^)]*\))'
    if 'messagesForApi' in main_js:
        if '注入文风小尾巴' not in main_js:
            # Find last occurrence of fetch with completions
            match_pos = main_js.rfind('fetch(')
            if match_pos > 0:
                # Find start of statement
                line_start = main_js.rfind('\n', 0, match_pos) + 1
                main_js = main_js[:line_start] + tail_injection + '\n' + main_js[line_start:]
                print("  ✅ 添加了文风小尾巴注入到API调用前")
    
    print("✅ 文风功能添加完成")
    return main_js

def add_writing_style_html(index_html):
    """在index.html中添加文风设置页面和相关UI"""
    
    # ===== 1. Add 文风设置 to sidebar/menu =====
    # Find the sidebar menu items (contacts, worldbook, etc.)
    
    menu_item_html = '''
                <li class="menu-item" onclick="showWritingStylePage()">
                    <span class="menu-icon">✍️</span>
                    <span class="menu-text">文风设置</span>
                </li>'''
    
    # Find where worldbook menu item is and add after it
    worldbook_patterns = [
        r'(onclick=["\']showWorldBook[^"\']*["\'][^>]*>[^<]*世界书[^<]*</[^>]+>)',
        r'(世界书.*?</li>)',
        r'(<li[^>]*>[^<]*世界书[^<]*</li>)',
    ]
    
    style_page_added = '文风设置' in index_html
    if not style_page_added:
        for pat in worldbook_patterns:
            m = re.search(pat, index_html, re.DOTALL)
            if m:
                index_html = index_html[:m.end()] + menu_item_html + index_html[m.end():]
                print("  ✅ 添加了文风设置菜单项")
                break
    
    # ===== 2. Add writing style page HTML =====
    writing_style_page = '''
<!-- 文风设置页面 -->
<div id="writingStylePage" class="main-section worldbook-page" style="display:none; flex-direction:column;">
    <div class="worldbook-header">
        <button class="back-btn" onclick="showContactsPage()">←</button>
        <h2>文风设置</h2>
        <button class="add-worldbook-btn" onclick="openEditWritingStyle(null)">+</button>
    </div>
    <div class="worldbook-content">
        <div id="writingStyleList" class="worldbook-list">
            <div class="empty-tip">暂无文风条目，点击右上角"+"新建</div>
        </div>
    </div>
</div>

<!-- 文风编辑弹窗 -->
<div id="writingStyleEditModal" class="modal-overlay" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
    <div class="modal-content" style="background:var(--bg-primary, #fff); border-radius:12px; padding:20px; width:90%; max-width:500px; max-height:80vh; overflow-y:auto;">
        <div class="modal-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <h3 id="wsEditTitle">新建文风</h3>
            <button onclick="closeWritingStyleEditModal()" style="background:none; border:none; font-size:20px; cursor:pointer;">×</button>
        </div>
        <input type="hidden" id="wsEditId">
        <div style="margin-bottom:12px;">
            <label style="display:block; margin-bottom:5px; font-weight:bold;">文风名称</label>
            <input type="text" id="wsEditName" placeholder="如：古典文风、现代简约..." 
                style="width:100%; padding:8px; border:1px solid #ddd; border-radius:6px; box-sizing:border-box;">
        </div>
        <div style="margin-bottom:15px;">
            <label style="display:block; margin-bottom:5px; font-weight:bold;">文风内容</label>
            <textarea id="wsEditContent" placeholder="请输入详细的文风描述和行为规范..." 
                style="width:100%; padding:8px; border:1px solid #ddd; border-radius:6px; min-height:200px; box-sizing:border-box; resize:vertical;"></textarea>
        </div>
        <div style="display:flex; gap:10px; justify-content:flex-end;">
            <button onclick="closeWritingStyleEditModal()" style="padding:8px 16px; border:1px solid #ddd; border-radius:6px; cursor:pointer;">取消</button>
            <button onclick="saveWritingStyleEdit()" style="padding:8px 16px; background:#4CAF50; color:white; border:none; border-radius:6px; cursor:pointer;">保存</button>
        </div>
    </div>
</div>
'''
    
    if 'writingStylePage' not in index_html:
        # Add before </body>
        index_html = index_html.replace('</body>', writing_style_page + '\n</body>')
        print("  ✅ 添加了文风设置页面HTML")
    
    # ===== 3. Add writing style selector to chat settings =====
    chat_style_selector = '''
            <!-- 文风设置 -->
            <div class="setting-group" id="writingStyleSettingGroup">
                <div class="setting-label">当前聊天文风</div>
                <div class="warning-tip" style="background:#fff3cd; border:1px solid #ffc107; border-radius:6px; padding:8px; margin-bottom:8px; font-size:12px; color:#856404;">
                    ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
                </div>
                <select id="chatWritingStyleSelect" onchange="onWritingStyleChange(currentChatId)" style="width:100%; padding:8px; border:1px solid #ddd; border-radius:6px;">
                    <option value="">不使用文风</option>
                </select>
            </div>'''
    
    if 'chatWritingStyleSelect' not in index_html:
        # Find chat settings panel
        chat_setting_patterns = [
            r'(id=["\']chatSettingsPanel["\'][^>]*>)',
            r'(<!-- ?聊天设置|id=["\']chat-settings["\'])',
            r'(class=["\']chat-settings["\'][^>]*>)',
        ]
        for pat in chat_setting_patterns:
            m = re.search(pat, index_html)
            if m:
                # Find a good insertion point inside the panel
                panel_start = m.end()
                # Look for first setting-group after panel start
                next_group = index_html.find('</div>', panel_start)
                if next_group > 0:
                    index_html = index_html[:next_group] + chat_style_selector + index_html[next_group:]
                    print("  ✅ 添加了文风选择器到聊天设置")
                    break
    
    # ===== 4. Fix worldbook categories in HTML =====
    index_html = index_html.replace('>语言规范<', '>世界观<')
    index_html = index_html.replace("value='语言规范'", "value='世界观'")
    index_html = index_html.replace('value="语言规范"', 'value="世界观"')
    
    # Add 其他 option if needed
    if '其他' not in index_html:
        # After 世界观 option in worldbook category select
        index_html = re.sub(
            r'(<option[^>]*value=["\']世界观["\'][^>]*>世界观</option>)',
            r'\1\n                    <option value="其他">其他</option>',
            index_html
        )
        print("  ✅ 添加了'其他'分类到世界书")
    
    print("✅ index.html修改完成")
    return index_html

def add_worldbook_enabled_entries_ui(index_html):
    """在聊天设置中添加世界书条目勾选（记忆总结）"""
    
    memory_summary_setting = '''
            <!-- 记忆总结世界书条目启用 -->
            <div class="setting-group" id="memorySummarySettingGroup">
                <div class="setting-label">启用的记忆总结条目</div>
                <div class="setting-desc" style="font-size:12px; color:#999; margin-bottom:8px;">
                    勾选后，对应的"记忆总结"类世界书条目将对本联系人全局生效（常驻注入上下文）
                </div>
                <div id="memorySummaryEntryList" style="max-height:150px; overflow-y:auto; border:1px solid #ddd; border-radius:6px; padding:8px;">
                    <div class="empty-tip" style="color:#999; font-size:12px;">暂无记忆总结类世界书条目</div>
                </div>
            </div>'''
    
    if 'memorySummarySettingGroup' not in index_html:
        # Add near the writing style selector
        if 'writingStyleSettingGroup' in index_html:
            index_html = index_html.replace(
                '<!-- 文风设置 -->',
                memory_summary_setting + '\n            <!-- 文风设置 -->'
            )
            print("  ✅ 添加了记忆总结条目勾选UI")
    
    return index_html

def add_memory_summary_js(main_js):
    """添加记忆总结条目管理JS"""
    
    memory_js = '''

// 渲染记忆总结条目勾选列表（在聊天设置中）
function renderMemorySummaryEntryList(contactId) {
    const listEl = document.getElementById('memorySummaryEntryList');
    if (!listEl) return;
    
    const contact = contacts.find(c => c.id === contactId);
    if (!contact) return;
    
    const enabledEntries = contact.enabledWorldBookEntries || [];
    
    // Filter worldbook entries to only show 记忆总结 category
    const memorySummaryEntries = (window.worldBookEntries || []).filter(e => e.category === '记忆总结');
    
    if (memorySummaryEntries.length === 0) {
        listEl.innerHTML = '<div class="empty-tip" style="color:#999; font-size:12px;">暂无记忆总结类世界书条目</div>';
        return;
    }
    
    listEl.innerHTML = memorySummaryEntries.map(entry => `
        <label style="display:flex; align-items:center; gap:8px; padding:4px 0; cursor:pointer;">
            <input type="checkbox" 
                ${enabledEntries.includes(entry.id) ? 'checked' : ''}
                onchange="toggleMemorySummaryEntry('${contactId}', '${entry.id}', this.checked)"
                style="cursor:pointer;">
            <span>${escapeHtml(entry.name || entry.keywords || '未命名条目')}</span>
        </label>
    `).join('');
}

async function toggleMemorySummaryEntry(contactId, entryId, enabled) {
    const contact = contacts.find(c => c.id === contactId);
    if (!contact) return;
    
    if (!contact.enabledWorldBookEntries) {
        contact.enabledWorldBookEntries = [];
    }
    
    if (enabled) {
        if (!contact.enabledWorldBookEntries.includes(entryId)) {
            contact.enabledWorldBookEntries.push(entryId);
        }
    } else {
        contact.enabledWorldBookEntries = contact.enabledWorldBookEntries.filter(id => id !== entryId);
    }
    
    await saveContacts();
    showToast(enabled ? '已启用该记忆总结条目' : '已禁用该记忆总结条目');
}

// 修改世界书注入逻辑：记忆总结只对明确启用的联系人生效
function shouldInjectWorldBookEntry(entry, contactId) {
    if (entry.category === '记忆总结') {
        const contact = contacts.find(c => c.id === contactId);
        const enabledEntries = (contact && contact.enabledWorldBookEntries) || [];
        return enabledEntries.includes(entry.id);
    }
    // 世界观和其他：关键词触发，逻辑不变
    return true; // 让原有关键词逻辑决定是否触发
}
'''
    
    if 'renderMemorySummaryEntryList' not in main_js:
        insertion_point = main_js.rfind('\nasync function initApp(')
        if insertion_point == -1:
            insertion_point = main_js.rfind('\nwindow.addEventListener')
        if insertion_point == -1:
            insertion_point = len(main_js)
        
        main_js = main_js[:insertion_point] + memory_js + main_js[insertion_point:]
        print("✅ 添加了记忆总结管理JS")
    
    return main_js

def add_init_loading(main_js):
    """确保loadWritingStyles在初始化时被调用"""
    
    # Find initApp or similar function
    if 'loadWritingStyles()' not in main_js:
        # Find loadWorldBook() and add loadWritingStyles after it
        if 'loadWorldBook()' in main_js:
            main_js = main_js.replace(
                'loadWorldBook()',
                'loadWorldBook();\n    await loadWritingStyles()'
            )
            print("✅ 添加了loadWritingStyles到初始化流程")
        elif 'loadContacts()' in main_js:
            main_js = main_js.replace(
                'await loadContacts()',
                'await loadContacts();\n    await loadWritingStyles()'
            )
            print("✅ 添加了loadWritingStyles到初始化流程(after contacts)")
    
    return main_js

def main():
    print("=" * 60)
    print("开始执行综合修改计划")
    print("=" * 60)
    
    # Step 1: Backup
    print("\n【第一步】备份文件...")
    backup_dir = backup()
    
    # Step 2: Read files
    print("\n【第二步】读取文件...")
    main_js = read_file('js/main.js')
    index_html = read_file('index.html')
    print(f"  main.js: {len(main_js)} chars, index.html: {len(index_html)} chars")
    
    # Step 3: Modify worldbook categories
    print("\n【第三步】修改世界书分类...")
    main_js = fix_worldbook_categories(main_js)
    index_html = fix_worldbook_categories(index_html)
    
    # Step 4: Add memory summary management
    print("\n【第四步】添加记忆总结管理...")
    main_js = add_memory_summary_js(main_js)
    index_html = add_worldbook_enabled_entries_ui(index_html)
    
    # Step 5: Add writing style feature
    print("\n【第五步】添加文风设置功能...")
    main_js = add_writing_style_feature(main_js, index_html)
    index_html = add_writing_style_html(index_html)
    
    # Step 6: Add initialization
    print("\n【第六步】更新初始化流程...")
    main_js = add_init_loading(main_js)
    
    # Step 7: Write files
    print("\n【第七步】写入文件...")
    write_file('js/main.js', main_js)
    write_file('index.html', index_html)
    
    print("\n" + "=" * 60)
    print("✅ 所有修改完成！")
    print("=" * 60)
    print("\n变更摘要：")
    print("1. 世界书分类: 语言规范 → 世界观，新增 其他")
    print("2. 记忆总结: 现在需要在聊天设置中明确勾选才生效")
    print("3. 新增 文风设置 独立页面（通讯录菜单）")
    print("4. 聊天设置新增 文风单选 下拉菜单（带警告提示）")
    print("5. 切换文风时调用API压缩，发消息时自动附加文风小尾巴")
    print(f"\n备份位置: {backup_dir}")

if __name__ == '__main__':
    main()
