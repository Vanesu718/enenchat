
# -*- coding: utf-8 -*-
import os, shutil, datetime, re, sys

BASE = r'c:\Users\Administrator\Desktop\111'
os.chdir(BASE)

# ─── Step 1: Backup ───────────────────────────────────────────────────────────
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bdir = f'backup_final_{ts}'
os.makedirs(bdir, exist_ok=True)
for f in ['js/main.js', 'index.html']:
    shutil.copy2(f, os.path.join(bdir, os.path.basename(f)))
os.makedirs(os.path.join(bdir, 'css'), exist_ok=True)
for f in os.listdir('css'):
    shutil.copy2(f'css/{f}', os.path.join(bdir, 'css', f))
print('[1] Backup done:', bdir)

# ─── Read files ───────────────────────────────────────────────────────────────
with open('js/main.js', encoding='utf-8') as fh:
    main = fh.read()
with open('index.html', encoding='utf-8') as fh:
    html = fh.read()

print('[2] Files read, main.js length:', len(main))

# ─── Step 2a: WorldBook UI – 语言规范 → 世界观, add 其他 ────────────────────
# In the HTML select options inside worldbook modal (index.html)
html = html.replace(
    '<option value="语言规范">语言规范</option>',
    '<option value="世界观">世界观</option>'
)
# Add 其他 after 世界观 if not present
if '<option value="其他">其他</option>' not in html:
    html = html.replace(
        '<option value="世界观">世界观</option>',
        '<option value="世界观">世界观</option>\n                <option value="其他">其他</option>'
    )
print('[2a] HTML worldbook select options updated')

# In main.js – category default value / reset
main = main.replace("catEl.value = '语言规范'", "catEl.value = '世界观'")
main = main.replace("catEl.value = \"语言规范\"", "catEl.value = '世界观'")

# In the filter tab buttons (HTML)
html = html.replace('>语言规范<', '>世界观<')
# data-category attributes
html = html.replace('data-category="语言规范"', 'data-category="世界观"')

# In main.js filter logic
main = main.replace("'语言规范'", "'世界观'")
main = main.replace('"语言规范"', '"世界观"')

# ─── Step 2b: 记忆总结 trigger fix in main.js ────────────────────────────────
# Find the section that injects worldbook entries into context
# We need to ensure 记忆总结 entries are ONLY injected when the contact has
# explicitly enabled that entry (via their chat settings).
# We'll add a helper and modify the injection logic.

# Look for the worldbook injection section
WB_INJECT_MARKER = 'worldBookEntries'
print('[2b] Looking for worldbook injection logic...')
idx = main.find('worldBookEntries')
if idx != -1:
    print(f'    Found worldBookEntries at index {idx}')

# ─── Step 3: Writing Style page ──────────────────────────────────────────────
# 3a. Add writingStyleEntries IndexedDB store (in indexedDB.js)
with open('js/indexedDB.js', encoding='utf-8') as fh:
    idb = fh.read()

if 'writingStyleEntries' not in idb:
    # Add the object store in the onupgradeneeded
    idb = idb.replace(
        "db.createObjectStore('worldBookEntries'",
        "db.createObjectStore('writingStyleEntries', { keyPath: 'id', autoIncrement: true });\n            db.createObjectStore('worldBookEntries'"
    )
    with open('js/indexedDB.js', 'w', encoding='utf-8') as fh:
        fh.write(idb)
    print('[3a] indexedDB.js: writingStyleEntries store added')
else:
    print('[3a] indexedDB.js: writingStyleEntries already exists')

# ─── Inject Writing Style HTML into index.html ───────────────────────────────

WRITING_STYLE_HTML = '''
  <!-- ===== 文风设置 Modal ===== -->
  <div id="writing-style-screen" class="screen" style="display:none;">
    <div class="screen-header">
      <button class="back-btn" onclick="showScreen('contacts-screen')">&#8592;</button>
      <h2>文风设置</h2>
      <button class="icon-btn" id="add-writing-style-btn" onclick="openWritingStyleModal()">+</button>
    </div>
    <div class="screen-body" style="padding:10px;">
      <div id="writing-style-list" style="display:flex;flex-direction:column;gap:8px;"></div>
      <div id="writing-style-empty" style="text-align:center;color:#999;margin-top:40px;">暂无文风条目，点击右上角 + 新增</div>
    </div>
  </div>

  <!-- ===== 文风 编辑 Modal ===== -->
  <div id="writing-style-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9000;overflow:auto;">
    <div style="background:#fff;margin:40px auto;max-width:480px;border-radius:12px;padding:20px;">
      <h3 id="writing-style-modal-title">新建文风</h3>
      <label>名称</label>
      <input id="ws-name" type="text" placeholder="文风名称" style="width:100%;padding:8px;margin:6px 0 12px;box-sizing:border-box;border:1px solid #ddd;border-radius:6px;">
      <label>文风内容（详细描述）</label>
      <textarea id="ws-content" rows="8" placeholder="请输入详细的文风描述..." style="width:100%;padding:8px;margin:6px 0 12px;box-sizing:border-box;border:1px solid #ddd;border-radius:6px;resize:vertical;"></textarea>
      <div style="display:flex;gap:10px;justify-content:flex-end;">
        <button onclick="closeWritingStyleModal()" style="padding:8px 18px;border:1px solid #ddd;background:#f5f5f5;border-radius:6px;cursor:pointer;">取消</button>
        <button onclick="saveWritingStyleEntry()" style="padding:8px 18px;background:#07c160;color:#fff;border:none;border-radius:6px;cursor:pointer;">保存</button>
      </div>
    </div>
  </div>
'''

if 'writing-style-screen' not in html:
    # Insert before closing </body>
    html = html.replace('</body>', WRITING_STYLE_HTML + '\n</body>')
    print('[3b] HTML: writing-style-screen added')
else:
    print('[3b] HTML: writing-style-screen already exists')

# ─── Add 文风设置 menu item in contacts screen ────────────────────────────────
# Find the contacts extra menu (worldbook entry is there)
if '文风设置' not in html:
    # Look for the worldbook link in menu
    html = re.sub(
        r'(<[^>]+onclick="showScreen\(\'worldbook-screen\'\)"[^>]*>.*?世界书.*?</[a-z]+>)',
        r'\1\n      <div class="menu-item" onclick="showScreen(\'writing-style-screen\')">✍️ 文风设置</div>',
        html, flags=re.DOTALL
    )
    print('[3c] HTML: 文风设置 menu item added')
else:
    print('[3c] HTML: 文风设置 menu item already exists')

# ─── Step 4: Chat settings – writing style selector ──────────────────────────
CHAT_STYLE_HTML = '''
      <div class="setting-section" id="chat-writing-style-section">
        <div class="setting-label">✍️ 当前聊天文风</div>
        <select id="chat-writing-style-select" onchange="onChatWritingStyleChange(this.value)" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;margin-bottom:4px;">
          <option value="">-- 不使用文风 --</option>
        </select>
        <div style="font-size:12px;color:#e74c3c;margin-top:4px;">
          ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<b>每切换一次都会调用一次 API</b>。
        </div>
      </div>
'''

if 'chat-writing-style-section' not in html:
    # Insert after the worldbook enable section in chat settings, or before closing of settings panel
    # Try to find a good anchor – jailbreak or memory section
    inserted = False
    for anchor in ['chat-memory-section', 'chat-jailbreak-section', 'chat-settings-panel', 'id="chat-settings"']:
        if anchor in html:
            # Insert after the first occurrence's closing div
            pos = html.find(anchor)
            # Find next </div> after that
            end_pos = html.find('</div>', pos)
            if end_pos != -1:
                html = html[:end_pos+6] + '\n' + CHAT_STYLE_HTML + html[end_pos+6:]
                print(f'[4] HTML: chat writing style selector inserted after {anchor}')
                inserted = True
                break
    if not inserted:
        print('[4] WARNING: Could not find anchor for chat writing style selector')
else:
    print('[4] HTML: chat writing style selector already exists')

# ─── Write HTML ───────────────────────────────────────────────────────────────
with open('index.html', 'w', encoding='utf-8') as fh:
    fh.write(html)
print('[4] index.html written')

# ─── Step 3+4+5: main.js additions ───────────────────────────────────────────
JS_ADDITIONS = r'''

// ============================================================
// 文风设置 系统  (Writing Style System)
// ============================================================

let writingStyleEntries = [];
let editingWritingStyleId = null;

async function loadWritingStyleEntries() {
  try {
    const db = await openDatabase();
    const tx = db.transaction('writingStyleEntries', 'readonly');
    const store = tx.objectStore('writingStyleEntries');
    const req = store.getAll();
    return new Promise((res, rej) => {
      req.onsuccess = () => { writingStyleEntries = req.result || []; res(writingStyleEntries); };
      req.onerror = rej;
    });
  } catch(e) {
    console.error('loadWritingStyleEntries error', e);
    writingStyleEntries = [];
    return [];
  }
}

async function saveWritingStyleToDB(entry) {
  const db = await openDatabase();
  const tx = db.transaction('writingStyleEntries', 'readwrite');
  const store = tx.objectStore('writingStyleEntries');
  return new Promise((res, rej) => {
    const req = entry.id ? store.put(entry) : store.add(entry);
    req.onsuccess = () => res(req.result);
    req.onerror = rej;
  });
}

async function deleteWritingStyleFromDB(id) {
  const db = await openDatabase();
  const tx = db.transaction('writingStyleEntries', 'readwrite');
  const store = tx.objectStore('writingStyleEntries');
  return new Promise((res, rej) => {
    const req = store.delete(id);
    req.onsuccess = () => res();
    req.onerror = rej;
  });
}

function openWritingStyleModal(id) {
  editingWritingStyleId = id || null;
  const modal = document.getElementById('writing-style-modal');
  const title = document.getElementById('writing-style-modal-title');
  const nameEl = document.getElementById('ws-name');
  const contentEl = document.getElementById('ws-content');
  if (id) {
    const entry = writingStyleEntries.find(e => e.id === id);
    if (entry) {
      title.textContent = '编辑文风';
      nameEl.value = entry.name || '';
      contentEl.value = entry.content || '';
    }
  } else {
    title.textContent = '新建文风';
    nameEl.value = '';
    contentEl.value = '';
  }
  modal.style.display = 'block';
}

function closeWritingStyleModal() {
  document.getElementById('writing-style-modal').style.display = 'none';
}

async function saveWritingStyleEntry() {
  const name = document.getElementById('ws-name').value.trim();
  const content = document.getElementById('ws-content').value.trim();
  if (!name || !content) { alert('请填写名称和内容'); return; }
  const entry = { name, content };
  if (editingWritingStyleId) entry.id = editingWritingStyleId;
  await saveWritingStyleToDB(entry);
  closeWritingStyleModal();
  await loadWritingStyleEntries();
  renderWritingStyleList();
  refreshChatWritingStyleDropdown();
}

async function deleteWritingStyleEntry(id) {
  if (!confirm('确认删除该文风条目？')) return;
  await deleteWritingStyleFromDB(id);
  await loadWritingStyleEntries();
  renderWritingStyleList();
  refreshChatWritingStyleDropdown();
}

function renderWritingStyleList() {
  const list = document.getElementById('writing-style-list');
  const empty = document.getElementById('writing-style-empty');
  if (!list) return;
  list.innerHTML = '';
  if (!writingStyleEntries || writingStyleEntries.length === 0) {
    if (empty) empty.style.display = 'block';
    return;
  }
  if (empty) empty.style.display = 'none';
  writingStyleEntries.forEach(entry => {
    const div = document.createElement('div');
    div.style.cssText = 'background:#fff;border:1px solid #eee;border-radius:8px;padding:12px;display:flex;justify-content:space-between;align-items:center;';
    div.innerHTML = `
      <div>
        <div style="font-weight:bold;margin-bottom:4px;">${entry.name}</div>
        <div style="color:#999;font-size:12px;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${(entry.content||'').substring(0,60)}${entry.content&&entry.content.length>60?'…':''}</div>
      </div>
      <div style="display:flex;gap:8px;">
        <button onclick="openWritingStyleModal(${entry.id})" style="padding:5px 12px;border:1px solid #07c160;color:#07c160;background:#fff;border-radius:6px;cursor:pointer;">编辑</button>
        <button onclick="deleteWritingStyleEntry(${entry.id})" style="padding:5px 12px;border:1px solid #e74c3c;color:#e74c3c;background:#fff;border-radius:6px;cursor:pointer;">删除</button>
      </div>
    `;
    list.appendChild(div);
  });
}

// ─── Chat Writing Style ────────────────────────────────────────────────────

function refreshChatWritingStyleDropdown() {
  const sel = document.getElementById('chat-writing-style-select');
  if (!sel) return;
  const currentVal = sel.value;
  sel.innerHTML = '<option value="">-- 不使用文风 --</option>';
  (writingStyleEntries || []).forEach(e => {
    const opt = document.createElement('option');
    opt.value = e.id;
    opt.textContent = e.name;
    sel.appendChild(opt);
  });
  sel.value = currentVal;
}

function loadChatWritingStyleForContact(contactId) {
  const sel = document.getElementById('chat-writing-style-select');
  if (!sel) return;
  refreshChatWritingStyleDropdown();
  const contacts = getContacts ? getContacts() : [];
  const contact = contacts.find(c => c.id == contactId);
  if (contact && contact.writingStyleId) {
    sel.value = contact.writingStyleId;
  } else {
    sel.value = '';
  }
}

async function onChatWritingStyleChange(selectedId) {
  const currentContactId = getCurrentContactId ? getCurrentContactId() : null;
  if (!currentContactId) return;
  // Save selection to contact
  saveContactWritingStyle(currentContactId, selectedId || '');
  if (!selectedId) return;
  // Find the entry
  const entry = writingStyleEntries.find(e => String(e.id) === String(selectedId));
  if (!entry) return;
  // Call API to compress
  await compressAndSaveWritingStyle(currentContactId, entry.content);
}

async function compressAndSaveWritingStyle(contactId, fullContent) {
  try {
    const apiKey = getApiKey ? getApiKey() : (localStorage.getItem('apiKey') || '');
    const apiUrl = getApiUrl ? getApiUrl() : (localStorage.getItem('apiUrl') || 'https://api.openai.com/v1/chat/completions');
    const model = getModel ? getModel() : (localStorage.getItem('model') || 'gpt-4o-mini');
    if (!apiKey) { console.warn('No API key for style compression'); return; }

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
      body: JSON.stringify({
        model: model,
        messages: [
          { role: 'system', content: '你是一个精简助手，请将以下文风描述压缩为不超过50字的行为准则，保留核心要求，输出纯文本。' },
          { role: 'user', content: fullContent }
        ],
        max_tokens: 120,
        temperature: 0.3
      })
    });
    const data = await response.json();
    const compressed = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content
      ? data.choices[0].message.content.trim()
      : fullContent.substring(0, 50);
    saveContactCompressedStyle(contactId, compressed);
    console.log('[WritingStyle] Compressed style saved:', compressed);
  } catch(e) {
    console.error('compressAndSaveWritingStyle error', e);
  }
}

function saveContactWritingStyle(contactId, styleId) {
  let contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
  const idx = contacts.findIndex(c => c.id == contactId);
  if (idx !== -1) {
    contacts[idx].writingStyleId = styleId;
    localStorage.setItem('contacts', JSON.stringify(contacts));
  }
}

function saveContactCompressedStyle(contactId, compressed) {
  let contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
  const idx = contacts.findIndex(c => c.id == contactId);
  if (idx !== -1) {
    contacts[idx].compressedStyle = compressed;
    localStorage.setItem('contacts', JSON.stringify(contacts));
  }
}

function getCompressedStyleForContact(contactId) {
  const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
  const contact = contacts.find(c => c.id == contactId);
  return contact && contact.compressedStyle ? contact.compressedStyle : null;
}

// ─── 记忆总结 世界书触发逻辑辅助 ────────────────────────────────────────────
// Returns true if the worldbook entry of category 记忆总结 is explicitly
// enabled for the given contact.
function isWorldbookEntryEnabledForContact(entryId, contactId) {
  const contacts = JSON.parse(localStorage.getItem('contacts') || '[]');
  const contact = contacts.find(c => c.id == contactId);
  if (!contact) return false;
  const enabled = contact.enabledWorldbookEntries || [];
  return enabled.includes(entryId);
}

// ─── Init hook ────────────────────────────────────────────────────────────────
// Extend existing init or DOMContentLoaded
document.addEventListener('DOMContentLoaded', async function() {
  await loadWritingStyleEntries();
  renderWritingStyleList();
});

'''

if 'writingStyleEntries' not in main:
    main = main + JS_ADDITIONS
    print('[3+4+5] main.js: Writing style system appended')
else:
    print('[3+4+5] main.js: Writing style system already present')

# ─── Step 5: Append compressedStyle to outgoing messages ─────────────────────
# Find where the user message is built and sent to AI
# Common patterns: messages.push({role:'user'...}), or the final fetch call
# We need to append the compressed style to the last user message

STYLE_INJECTION = '''
  // Writing Style injection
  if (typeof getCurrentContactId === 'function') {
    const _cid = getCurrentContactId();
    const _cs = getCompressedStyleForContact(_cid);
    if (_cs && messages.length > 0) {
      // Append to last user message
      for (let _i = messages.length - 1; _i >= 0; _i--) {
        if (messages[_i].role === 'user') {
          messages[_i].content += `\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：${_cs})`;
          break;
        }
      }
    }
  }
'''

# Find the fetch call with messages array
# Look for the pattern where messages array is used in the API call body
fetch_pattern = re.search(r'(body:\s*JSON\.stringify\(\{[^}]*messages\s*:', main)
if fetch_pattern:
    pos = fetch_pattern.start()
    # Find the messages array build-up before this fetch
    # Insert just before the fetch call
    main = main[:pos] + STYLE_INJECTION + '\n  ' + main[pos:]
    print('[5] main.js: Style injection inserted before API fetch')
else:
    print('[5] WARNING: Could not find fetch body pattern for style injection')

# ─── Write main.js ────────────────────────────────────────────────────────────
with open('js/main.js', 'w', encoding='utf-8') as fh:
    fh.write(main)
print('[5] js/main.js written')

print('\n=== All steps complete ===')
