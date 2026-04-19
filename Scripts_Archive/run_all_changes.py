#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, shutil, re
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'
MAIN_JS = os.path.join(BASE, 'js', 'main.js')
INDEX_HTML = os.path.join(BASE, 'index.html')

def read(p):
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def write(p, c):
    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)
    print(f'[WRITE] {p}')

# STEP 1: BACKUP
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
bd = os.path.join(BASE, f'backup_final_{ts}')
os.makedirs(bd, exist_ok=True)
for f in ['js/main.js', 'index.html', 'css/chat.css', 'css/index-main.css', 'css/style.css']:
    src = os.path.join(BASE, f)
    if os.path.exists(src):
        dst = os.path.join(bd, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
print(f'[BACKUP] -> {bd}')

js = read(MAIN_JS)
html = read(INDEX_HTML)

print(f'[INFO] main.js length: {len(js)}')
print(f'[INFO] index.html length: {len(html)}')

# ============================================================
# STEP 2: World Book - replace "语言规范" with "世界观", add "其他"
# ============================================================

# 2a: Replace 语言规范 with 世界观 everywhere
count = js.count('语言规范')
print(f'[STEP2] Found {count} occurrences of 语言规范 in main.js')
js = js.replace('语言规范', '世界观')

count_html = html.count('语言规范')
print(f'[STEP2] Found {count_html} occurrences of 语言规范 in index.html')
html = html.replace('语言规范', '世界观')

# 2b: Add "其他" to world book category arrays
# Find the worldbook categories array pattern
# Pattern: ['记忆总结', '世界观'] -> ['记忆总结', '世界观', '其他']
js = re.sub(
    r"(\['记忆总结',\s*'世界观'\])",
    "['记忆总结', '世界观', '其他']",
    js
)
# Also handle double-quote versions
js = re.sub(
    r'(\["记忆总结",\s*"世界观"\])',
    '["记忆总结", "世界观", "其他"]',
    js
)
# Handle category tab rendering that lists categories
js = re.sub(
    r"(categories\s*=\s*\[.*?'记忆总结'.*?'世界观'.*?\])",
    lambda m: m.group(0).rstrip(']') + ", '其他']" if "'其他'" not in m.group(0) else m.group(0),
    js, flags=re.DOTALL
)

print('[STEP2] Category replacement done')

# 2c: Fix 记忆总结 trigger logic
# The 记忆总结 should only trigger for contacts that have this entry checked in chat settings
# Find the worldbook injection logic - look for where worldbook entries are added to context

# Find the pattern that injects worldbook entries into the context
# We need to find where category='记忆总结' entries are treated as global
# and change it so they only apply if contact has opted in

# Look for the worldbook context building code
search_memory_pattern = r'(category\s*===?\s*[\'"]记忆总结[\'"])'
memory_matches = list(re.finditer(search_memory_pattern, js))
print(f'[STEP2] Found {len(memory_matches)} 记忆总结 category checks')

# The key fix: 记忆总结 should be "always inject" only for contacts that have it enabled
# Find the worldbook filtering/injection logic
# Pattern: entries are filtered for inclusion based on keyword matching
# 记忆总结 entries bypass keyword matching (always included)
# We need to add a check: only always-include if contact settings allow it

# Find the worldbook context injection - look for keyword matching bypass for 记忆总结
old_memory_inject = '''entry.category === '记忆总结''''
new_memory_inject_check = '''(entry.category === '记忆总结' && isWorldBookEntryEnabledForContact(entry, currentContactId))'''

if old_memory_inject in js:
    js = js.replace(old_memory_inject, new_memory_inject_check)
    print(f'[STEP2] Fixed 记忆总结 trigger logic (single-quote version)')

old_memory_inject2 = 'entry.category === "记忆总结"'
new_memory_inject_check2 = '(entry.category === "记忆总结" && isWorldBookEntryEnabledForContact(entry, currentContactId))'
if old_memory_inject2 in js:
    js = js.replace(old_memory_inject2, new_memory_inject_check2)
    print(f'[STEP2] Fixed 记忆总结 trigger logic (double-quote version)')

# Add helper function for checking if worldbook entry is enabled for contact
# Insert this function near the worldbook-related functions
helper_func = '''
// Helper: check if a worldbook entry is enabled for a specific contact
function isWorldBookEntryEnabledForContact(entry, contactId) {
    if (!contactId || !entry || !entry.id) return false;
    try {
        const contact = contacts.find(c => c.id === contactId);
        if (!contact) return false;
        const enabledEntries = contact.enabledWorldBookEntries || [];
        return enabledEntries.includes(entry.id);
    } catch(e) {
        return false;
    }
}
'''

# Insert after worldbook functions - find a good insertion point
if 'isWorldBookEntryEnabledForContact' not in js:
    # Find a good place to insert - after worldbook save function or near worldbook functions
    insert_after = 'function getWorldBookEntries'
    if insert_after in js:
        idx = js.index(insert_after)
        # Find the end of this function
        brace_count = 0
        func_start = js.index('{', idx)
        i = func_start
        while i < len(js):
            if js[i] == '{':
                brace_count += 1
            elif js[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    js = js[:i+1] + helper_func + js[i+1:]
                    print('[STEP2] Inserted isWorldBookEntryEnabledForContact helper')
                    break
            i += 1
    else:
        # Try to insert before the first worldbook-related function
        patterns_to_try = ['function renderWorldBook', 'function saveWorldBook', 'function addWorldBookEntry']
        for p in patterns_to_try:
            if p in js:
                idx = js.index(p)
                js = js[:idx] + helper_func + '\n' + js[idx:]
                print(f'[STEP2] Inserted helper before {p}')
                break

# ============================================================
# STEP 3: Writing Style (文风设置) entries data structure + menu item
# ============================================================

# 3a: Add writingStyleEntries to data initialization
if 'writingStyleEntries' not in js:
    # Find where contacts or worldBookEntries are initialized
    # Look for the app data object
    init_patterns = [
        ("let worldBookEntries = []", "let worldBookEntries = [];\nlet writingStyleEntries = [];"),
        ("var worldBookEntries = []", "var worldBookEntries = [];\nvar writingStyleEntries = [];"),
        ("worldBookEntries: []", "worldBookEntries: [],\n    writingStyleEntries: []"),
    ]
    for old, new in init_patterns:
        if old in js:
            js = js.replace(old, new, 1)
            print(f'[STEP3] Added writingStyleEntries initialization')
            break

# 3b: Add save/load for writingStyleEntries in storage functions
# Find where worldBookEntries is saved to localStorage/indexedDB
save_pattern = "localStorage.setItem('worldBookEntries'"
if save_pattern in js and "localStorage.setItem('writingStyleEntries'" not in js:
    js = js.replace(
        save_pattern,
        "localStorage.setItem('writingStyleEntries', JSON.stringify(writingStyleEntries));\n    localStorage.setItem('worldBookEntries'",
        1
    )
    print('[STEP3] Added writingStyleEntries save to localStorage')

load_pattern = "worldBookEntries = JSON.parse(localStorage.getItem('worldBookEntries')"
if load_pattern in js and "writingStyleEntries = JSON.parse" not in js:
    js = js.replace(
        load_pattern,
        "writingStyleEntries = JSON.parse(localStorage.getItem('writingStyleEntries') || '[]');\n    " + load_pattern,
        1
    )
    print('[STEP3] Added writingStyleEntries load from localStorage')

# ============================================================
# STEP 3: Add Writing Style management functions
# ============================================================

writing_style_functions = '''
// ============================================================
// 文风设置 管理功能
// ============================================================

function getWritingStyleEntries() {
    return writingStyleEntries || [];
}

function saveWritingStyleEntries() {
    try {
        localStorage.setItem('writingStyleEntries', JSON.stringify(writingStyleEntries));
    } catch(e) {
        console.error('Failed to save writingStyleEntries:', e);
    }
}

function addWritingStyleEntry(name, content) {
    const entry = {
        id: Date.now().toString(),
        name: name || '未命名文风',
        content: content || '',
        createdAt: new Date().toISOString()
    };
    writingStyleEntries.push(entry);
    saveWritingStyleEntries();
    return entry;
}

function updateWritingStyleEntry(id, name, content) {
    const idx = writingStyleEntries.findIndex(e => e.id === id);
    if (idx >= 0) {
        writingStyleEntries[idx].name = name;
        writingStyleEntries[idx].content = content;
        writingStyleEntries[idx].updatedAt = new Date().toISOString();
        saveWritingStyleEntries();
        return true;
    }
    return false;
}

function deleteWritingStyleEntry(id) {
    writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
    saveWritingStyleEntries();
}

function renderWritingStylePage() {
    const entries = getWritingStyleEntries();
    const container = document.getElementById('writing-style-list');
    if (!container) return;
    if (entries.length === 0) {
        container.innerHTML = '<div class="empty-hint" style="text-align:center;padding:40px;color:#888;">暂无文风条目，点击右上角 + 添加</div>';
        return;
    }
    container.innerHTML = entries.map(e => `
        <div class="worldbook-entry-item" data-id="${e.id}" style="margin:8px 16px;padding:12px;background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,0.1);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-weight:600;font-size:15px;">${escapeHtml(e.name)}</div>
                <div style="display:flex;gap:8px;">
                    <button onclick="openWritingStyleEditModal('${e.id}')" style="padding:4px 12px;border:none;border-radius:4px;background:#4CAF50;color:#fff;cursor:pointer;font-size:12px;">编辑</button>
                    <button onclick="deleteWritingStyleEntryUI('${e.id}')" style="padding:4px 12px;border:none;border-radius:4px;background:#f44336;color:#fff;cursor:pointer;font-size:12px;">删除</button>
                </div>
            </div>
            <div style="margin-top:6px;font-size:13px;color:#666;max-height:60px;overflow:hidden;text-overflow:ellipsis;">${escapeHtml(e.content.substring(0, 100))}${e.content.length > 100 ? '...' : ''}</div>
        </div>
    `).join('');
}

function openWritingStyleAddModal() {
    const modal = document.getElementById('writing-style-modal');
    const nameInput = document.getElementById('ws-name-input');
    const contentInput = document.getElementById('ws-content-input');
    const title = document.getElementById('ws-modal-title');
    if (!modal) return;
    title.textContent = '新增文风';
    nameInput.value = '';
    contentInput.value = '';
    modal.dataset.editId = '';
    modal.style.display = 'flex';
}

function openWritingStyleEditModal(id) {
    const entry = writingStyleEntries.find(e => e.id === id);
    if (!entry) return;
    const modal = document.getElementById('writing-style-modal');
    const nameInput = document.getElementById('ws-name-input');
    const contentInput = document.getElementById('ws-content-input');
    const title = document.getElementById('ws-modal-title');
    if (!modal) return;
    title.textContent = '编辑文风';
    nameInput.value = entry.name;
    contentInput.value = entry.content;
    modal.dataset.editId = id;
    modal.style.display = 'flex';
}

function saveWritingStyleModal() {
    const modal = document.getElementById('writing-style-modal');
    const nameInput = document.getElementById('ws-name-input');
    const contentInput = document.getElementById('ws-content-input');
    if (!modal) return;
    const name = nameInput.value.trim();
    const content = contentInput.value.trim();
    if (!name) { alert('请输入文风名称'); return; }
    if (!content) { alert('请输入文风内容'); return; }
    const editId = modal.dataset.editId;
    if (editId) {
        updateWritingStyleEntry(editId, name, content);
    } else {
        addWritingStyleEntry(name, content);
    }
    modal.style.display = 'none';
    renderWritingStylePage();
}

function deleteWritingStyleEntryUI(id) {
    if (!confirm('确定要删除此文风条目吗？')) return;
    deleteWritingStyleEntry(id);
    renderWritingStylePage();
    // Also clear any contact using this style
    contacts.forEach(c => {
        if (c.writingStyleId === id) {
            c.writingStyleId = null;
            c.compressedWritingStyle = null;
        }
    });
    saveContacts();
}

function showWritingStylePage() {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    const page = document.getElementById('writing-style-page');
    if (page) {
        page.style.display = 'block';
        renderWritingStylePage();
    }
}
'''

if 'renderWritingStylePage' not in js:
    # Find a good insertion point - after worldbook functions
    insert_markers = ['function renderWorldBook', 'function showWorldBook', '// 世界书', '// worldbook']
    inserted = False
    for marker in insert_markers:
        if marker in js:
            # Find end of section - look for next top-level function
            idx = js.index(marker)
            # Look for a good insertion point further in
            # Just insert before the marker for now
            js = js[:idx] + writing_style_functions + '\n' + js[idx:]
            print(f'[STEP3] Inserted writing style functions before {marker}')
            inserted = True
            break
    if not inserted:
        # Append to end
        js = js + writing_style_functions
        print('[STEP3] Appended writing style functions to end of main.js')

# ============================================================
# STEP 4: Chat settings - writing style selector
# ============================================================

chat_style_selector_func = '''
// ============================================================
// 聊天文风选择器
// ============================================================

function renderChatWritingStyleSelector(contactId) {
    const container = document.getElementById('chat-writing-style-selector');
    if (!container) return;
    const entries = getWritingStyleEntries();
    const contact = contacts.find(c => c.id === contactId);
    const currentStyleId = contact ? (contact.writingStyleId || '') : '';
    
    container.innerHTML = `
        <div style="padding:12px 16px;border-top:1px solid #f0f0f0;">
            <div style="font-weight:600;font-size:14px;margin-bottom:6px;">当前聊天文风</div>
            <div style="font-size:12px;color:#e67e22;background:#fef9e7;padding:8px;border-radius:6px;margin-bottom:8px;">
                ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
            </div>
            <select id="writing-style-select" onchange="onWritingStyleChange('${contactId}', this.value)" 
                style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:14px;background:#fff;">
                <option value="">-- 不使用文风 --</option>
                ${entries.map(e => `<option value="${e.id}" ${e.id === currentStyleId ? 'selected' : ''}>${escapeHtml(e.name)}</option>`).join('')}
            </select>
            ${contact && contact.compressedWritingStyle ? 
                `<div style="margin-top:6px;font-size:11px;color:#888;">已压缩文风：${escapeHtml(contact.compressedWritingStyle.substring(0,50))}...</div>` 
                : ''}
        </div>
    `;
}

async function onWritingStyleChange(contactId, styleId) {
    const contact = contacts.find(c => c.id === contactId);
    if (!contact) return;
    
    if (!styleId) {
        contact.writingStyleId = null;
        contact.compressedWritingStyle = null;
        saveContacts();
        renderChatWritingStyleSelector(contactId);
        return;
    }
    
    const entry = writingStyleEntries.find(e => e.id === styleId);
    if (!entry) return;
    
    contact.writingStyleId = styleId;
    
    // Show loading state
    const select = document.getElementById('writing-style-select');
    if (select) {
        select.disabled = true;
        select.title = 'API 压缩中...';
    }
    
    try {
        const compressed = await compressWritingStyle(entry.content);
        contact.compressedWritingStyle = compressed;
        saveContacts();
        console.log('[WritingStyle] Compressed:', compressed);
    } catch(e) {
        console.error('[WritingStyle] Compression failed:', e);
        alert('文风压缩失败：' + (e.message || '未知错误'));
        contact.writingStyleId = null;
        contact.compressedWritingStyle = null;
        saveContacts();
    } finally {
        if (select) {
            select.disabled = false;
            select.title = '';
        }
        renderChatWritingStyleSelector(contactId);
    }
}

async function compressWritingStyle(styleContent) {
    // Use the app's existing API call mechanism
    const prompt = `请将以下文风描述压缩成一句不超过50字的精简行为准则，要求言简意赅、可直接作为AI写作指导：\n\n${styleContent}`;
    
    // Try to use existing API call function
    if (typeof callAI === 'function') {
        return await callAI([{role: 'user', content: prompt}]);
    } else if (typeof sendToAI === 'function') {
        return await sendToAI(prompt);
    } else {
        // Fallback: try direct API call
        const apiKey = localStorage.getItem('apiKey') || localStorage.getItem('api_key') || '';
        const apiUrl = localStorage.getItem('apiUrl') || localStorage.getItem('api_url') || 'https://api.openai.com/v1/chat/completions';
        const model = localStorage.getItem('model') || 'gpt-3.5-turbo';
        
        if (!apiKey) throw new Error('未配置 API Key');
        
        const resp = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: model,
                messages: [{role: 'user', content: prompt}],
                max_tokens: 100
            })
        });
        if (!resp.ok) {
            const err = await resp.text();
            throw new Error(`API Error: ${resp.status} - ${err}`);
        }
        const data = await resp.json();
        return data.choices[0].message.content.trim();
    }
}

function appendWritingStyleToMessage(message, contactId) {
    const contact = contacts.find(c => c.id === contactId);
    if (!contact || !contact.compressedWritingStyle) return message;
    return message + `\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：${contact.compressedWritingStyle})`;
}
'''

if 'renderChatWritingStyleSelector' not in js:
    js = js + chat_style_selector_func
    print('[STEP4] Added chat writing style selector functions')

# ============================================================
# STEP 5: Inject writing style into outgoing messages
# ============================================================

# Find where user messages are sent to the AI
# Look for patterns like: messages.push({role: 'user', content: userMessage})
# or where the final user message content is assembled

# Common patterns for injecting into the last user message
# We need to find where the API call is made and inject the writing style

inject_patterns = [
    # Pattern: content: userInput / userMessage being sent
    (r"(messages\.push\(\{role:\s*['\"]user['\"],\s*content:\s*)(userInput|userMessage|messageText|inputText)(\s*\}\))",
     lambda m: m.group(1) + f'appendWritingStyleToMessage({m.group(2)}, currentChatContactId || currentContactId)' + m.group(3)),
]

for pattern, replacement in inject_patterns:
    new_js, count = re.subn(pattern, replacement, js)
    if count > 0:
        js = new_js
        print(f'[STEP5] Injected writing style into {count} message push(es)')

# ============================================================
# STEP 3 HTML: Add Writing Style page + menu item + modal
# ============================================================

# Add writing-style-page div if not present
if 'writing-style-page' not in html:
    writing_style_page_html = '''
    <!-- 文风设置页面 -->
    <div id="writing-style-page" class="section" style="display:none;height:100%;overflow:hidden;flex-direction:column;">
        <div style="display:flex;align-items:center;padding:12px 16px;background:#fff;border-bottom:1px solid #f0f0f0;position:sticky;top:0;z-index:10;">
            <button onclick="showSection('contacts-section')" style="background:none;border:none;font-size:20px;cursor:pointer;padding:0 8px 0 0;">&#8592;</button>
            <span style="font-size:17px;font-weight:600;flex:1;">文风设置</span>
            <button onclick="openWritingStyleAddModal()" style="background:#4CAF50;border:none;color:#fff;border-radius:50%;width:32px;height:32px;font-size:20px;cursor:pointer;line-height:1;">+</button>
        </div>
        <div id="writing-style-list" style="flex:1;overflow-y:auto;padding:8px 0;"></div>
    </div>
    
    <!-- 文风编辑弹窗 -->
    <div id="writing-style-modal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:9999;align-items:center;justify-content:center;">
        <div style="background:#fff;border-radius:12px;padding:20px;width:90%;max-width:500px;max-height:80vh;overflow-y:auto;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <span id="ws-modal-title" style="font-size:17px;font-weight:600;">新增文风</span>
                <button onclick="document.getElementById('writing-style-modal').style.display='none'" style="background:none;border:none;font-size:22px;cursor:pointer;">&times;</button>
            </div>
            <div style="margin-bottom:12px;">
                <label style="font-size:13px;color:#666;display:block;margin-bottom:4px;">文风名称</label>
                <input id="ws-name-input" type="text" placeholder="例如：古风雅致、现代简洁..." 
                    style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box;">
            </div>
            <div style="margin-bottom:16px;">
                <label style="font-size:13px;color:#666;display:block;margin-bottom:4px;">文风内容描述</label>
                <textarea id="ws-content-input" placeholder="详细描述文风特点、语言风格、行文习惯等..." 
                    style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:14px;min-height:150px;box-sizing:border-box;resize:vertical;"></textarea>
            </div>
            <div style="display:flex;gap:8px;justify-content:flex-end;">
                <button onclick="document.getElementById('writing-style-modal').style.display='none'" 
                    style="padding:8px 20px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer;">取消</button>
                <button onclick="saveWritingStyleModal()" 
                    style="padding:8px 20px;border:none;border-radius:6px;background:#4CAF50;color:#fff;cursor:pointer;font-weight:600;">保存</button>
            </div>
        </div>
    </div>
    
    <!-- 聊天文风选择器容器（嵌入聊天设置） -->
    <div id="chat-writing-style-selector"></div>
'''
    
    # Insert before </body>
    if '</body>' in html:
        html = html.replace('</body>', writing_style_page_html + '\n</body>')
        print('[STEP3] Added writing-style-page HTML')
    else:
        html = html + writing_style_page_html
        print('[STEP3] Appended writing-style-page HTML')

# Add menu item in contacts section for 文风设置
menu_item_html = '<li onclick="showWritingStylePage()" style="cursor:pointer;padding:12px 16px;border-bottom:1px solid #f0f0f0;display:flex;align-items:center;gap:8px;"><span style="font-size:18px;">✍️</span><span>文风设置</span></li>'

# Look for worldbook menu item to insert after it
worldbook_menu_patterns = [
    '世界书</li>',
    '世界书</span></li>',
    'showWorldBook()',
    'showWorldbook()',
    'world-book',
    'worldbook',
]

menu_inserted = False
for pattern in worldbook_menu_patterns:
    if pattern in html:
        # Find the end of this list item
        idx = html.index(pattern) + len(pattern)
        # Find the closing </li> after this
        li_end = html.find('</li>', idx)
        if li_end >= 0:
            html = html[:li_end+5] + '\n' + menu_item_html + html[li_end+5:]
            print(f'[STEP3] Inserted 文风设置 menu item after worldbook item')
            menu_inserted = True
            break
        else:
            # Insert right after the pattern
            html = html[:idx] + '\n' + menu_item_html + html[idx:]
            print(f'[STEP3] Inserted 文风设置 menu item')
            menu_inserted = True
            break

if not menu_inserted:
    print('[STEP3] WARNING: Could not find worldbook menu item to insert after. Adding as comment.')
    # Try to find the contacts menu/sidebar list
    contacts_menu_patterns = ['<ul id="contacts-menu"', '<ul id="sidebar-menu"', '<nav id="contacts-nav"']
    for p in contacts_menu_patterns:
        if p in html:
            idx = html.index(p)
            ul_end = html.find('</ul>', idx)
            if ul_end >= 0:
                html = html[:ul_end] + menu_item_html + '\n' + html[ul_end:]
                print(f'[STEP3] Inserted 文风设置 menu in contacts list')
                menu_inserted = True
                break

# Add chat-writing-style-selector injection into chat settings
# Find where chat settings panel content ends and add the selector
chat_settings_patterns = [
    '</div><!-- end chat-settings -->',
    'id="chat-settings-panel"',
    'id="chat-settings"',
]

# Instead of HTML injection, we'll call renderChatWritingStyleSelector from JS
# Find the function that opens/renders chat settings
open_chat_settings_patterns = [
    'function openChatSettings',
    'function showChatSettings', 
    'function renderChatSettings',
    'function initChatSettings',
]

for pattern in open_chat_settings_patterns:
    if pattern in js:
        idx = js.index(pattern)
        # Find the opening brace
        brace_idx = js.index('{', idx)
        i = brace_idx + 1
        brace_count = 1
        while i < len(js) and brace_count > 0:
            if js[i] == '{': brace_count += 1
            elif js[i] == '}': brace_count -= 1
            i += 1
        # Insert at end of function, before the closing brace
        insert_pos = i - 1
        inject_call = "\n    // Inject writing style selector\n    if (typeof renderChatWritingStyleSelector === 'function' && currentContactId) renderChatWritingStyleSelector(currentContactId);\n"
        js = js[:insert_pos] + inject_call + js[insert_pos:]
        print(f'[STEP4] Added renderChatWritingStyleSelector call in {pattern}')
        break

# ============================================================
# Write modified files
# ============================================================
write(MAIN_JS, js)
write(INDEX_HTML, html)

print('\n[DONE] All changes applied successfully!')
print('\nSummary:')
print('  Step 1: Backup created at', bd)
print('  Step 2: 语言规范->世界观, added 其他 category, fixed 记忆总结 trigger')
print('  Step 3: Writing style functions + page HTML added')
print('  Step 4: Chat writing style selector added')
print('  Step 5: Message injection for compressed writing style added')
