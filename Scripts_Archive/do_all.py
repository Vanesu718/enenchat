
# -*- coding: utf-8 -*-
import shutil, os, re, sys

BASE = r'c:\Users\Administrator\Desktop\111'
MAIN_JS = os.path.join(BASE, 'js', 'main.js')
INDEX_HTML = os.path.join(BASE, 'index.html')

# ── 1. 备份 ──────────────────────────────────────────────────────────────────
bk = os.path.join(BASE, 'backup_final_plan')
os.makedirs(bk, exist_ok=True)
for f in [MAIN_JS, INDEX_HTML]:
    shutil.copy2(f, os.path.join(bk, os.path.basename(f)))
print('Backup done')

# ── 2. 读取 main.js ──────────────────────────────────────────────────────────
with open(MAIN_JS, 'r', encoding='utf-8-sig') as fh:
    src = fh.read()

orig_len = len(src)
print(f'Original length: {orig_len}')

# ── 3. 世界书分类：语言规范 → 世界观，添加"其他" ──────────────────────────
# 3a. 把所有字符串 '语言规范' 替换成 '世界观'（但只替换分类名相关的地方）
src = src.replace("'语言规范'", "'世界观'")
src = src.replace('"语言规范"', '"世界观"')
# 3b. 分类数组 ['记忆总结','语言规范'] → ['记忆总结','世界观','其他']
src = re.sub(
    r"\['记忆总结',\s*'世界观'\]",
    "['记忆总结', '世界观', '其他']",
    src
)
src = re.sub(
    r'\["记忆总结",\s*"世界观"\]',
    '["记忆总结", "世界观", "其他"]',
    src
)
print('Step 3 done: categories updated')

# ── 4. 世界书触发逻辑修正 ───────────────────────────────────────────────────
# 寻找世界书注入逻辑：记忆总结 category 已经是"勾选启用"逻辑（selectedWorldBooks contains id）
# 世界观 & 其他：关键词触发
# 目前代码里的模式（来自之前输出）：
#   selectedEntries.forEach(entry => {
#     if (entry.category === '记忆总结') {
#       activeWorldBooks.push(...)
#     } else ...  ← 这里是关键词触发

# 我们要确认这部分代码已经正确（记忆总结 = 全局注入，其他 = 关键词）
# 如果存在旧的"全部注入"逻辑需要修正：
# 搜索关键词触发部分，确保 '世界观' 和 '其他' 走关键词路径

# 修正：确保 else 分支（关键词触发）也覆盖 '其他'
# 典型旧代码：
old_trigger = """        if (entry.category === '记忆总结') {
          activeWorldBooks.push(`[${entry.name}]\\n${entry.content}`);

        } else"""
new_trigger = """        if (entry.category === '记忆总结') {
          // 记忆总结：已勾选即常驻注入（无需关键词）
          activeWorldBooks.push(`[${entry.name}]\\n${entry.content}`);
        } else"""
if old_trigger in src:
    src = src.replace(old_trigger, new_trigger, 1)
    print('Step 4 done: trigger logic comment added')
else:
    print('Step 4: trigger pattern not found (may already be OK)')

# ── 5. 添加 writingStyleEntries 数据库初始化 ─────────────────────────────────
# 在 worldBookEntries 数组初始化附近添加 writingStyleEntries
ws_init_old = "let worldBookEntries = [];"
ws_init_new = "let worldBookEntries = [];\nlet writingStyleEntries = []; // 文风条目列表"
if ws_init_old in src and "writingStyleEntries" not in src:
    src = src.replace(ws_init_old, ws_init_new, 1)
    print('Step 5a done: writingStyleEntries var added')
elif "writingStyleEntries" in src:
    print('Step 5a: writingStyleEntries already exists')
else:
    # fallback: 在 DOMContentLoaded 前插入
    src = "let writingStyleEntries = [];\n" + src
    print('Step 5a: writingStyleEntries prepended')

# ── 6. 添加文风设置的核心 JS 功能 ─────────────────────────────────────────────
# 把完整的文风功能注入到文件末尾（在最后一个 } 前）
writing_style_js = '''

// ═══════════════════════════════════════════════════════════════
// 文风设置模块
// ═══════════════════════════════════════════════════════════════

// 保存文风条目到 localStorage
function saveWritingStyleEntries() {
  try {
    localStorage.setItem('writingStyleEntries', JSON.stringify(writingStyleEntries));
  } catch(e) {
    console.error('保存文风条目失败', e);
  }
}

// 加载文风条目
function loadWritingStyleEntries() {
  try {
    const data = localStorage.getItem('writingStyleEntries');
    writingStyleEntries = data ? JSON.parse(data) : [];
  } catch(e) {
    writingStyleEntries = [];
  }
}

// 渲染文风设置页面
function renderWritingStylePage() {
  loadWritingStyleEntries();
  const container = document.getElementById('writing-style-list');
  if (!container) return;
  if (writingStyleEntries.length === 0) {
    container.innerHTML = '<div class="empty-hint" style="text-align:center;color:#999;padding:40px;">暂无文风条目，点击右上角 ＋ 新建</div>';
    return;
  }
  container.innerHTML = writingStyleEntries.map((entry, idx) => `
    <div class="worldbook-item" data-id="${entry.id}">
      <div class="worldbook-item-header">
        <span class="worldbook-item-name">${entry.name}</span>
        <div class="worldbook-item-actions">
          <button class="wb-edit-btn" onclick="openWritingStyleEditor(${idx})">编辑</button>
          <button class="wb-delete-btn" onclick="deleteWritingStyleEntry('${entry.id}')">删除</button>
        </div>
      </div>
      <div class="worldbook-item-preview">${(entry.content||'').substring(0,80)}${(entry.content||'').length>80?'…':''}</div>
    </div>
  `).join('');
}

// 打开文风编辑器
function openWritingStyleEditor(idx) {
  const entry = idx !== undefined ? writingStyleEntries[idx] : null;
  const modal = document.getElementById('writing-style-modal');
  if (!modal) return;
  document.getElementById('ws-modal-title').textContent = entry ? '编辑文风' : '新建文风';
  document.getElementById('ws-entry-name').value = entry ? entry.name : '';
  document.getElementById('ws-entry-content').value = entry ? entry.content : '';
  document.getElementById('ws-entry-id').value = entry ? entry.id : '';
  modal.style.display = 'flex';
}

// 关闭文风编辑器
function closeWritingStyleModal() {
  const modal = document.getElementById('writing-style-modal');
  if (modal) modal.style.display = 'none';
}

// 保存文风条目（新建或编辑）
function saveWritingStyleEntry() {
  const name = document.getElementById('ws-entry-name').value.trim();
  const content = document.getElementById('ws-entry-content').value.trim();
  const id = document.getElementById('ws-entry-id').value;
  if (!name) { alert('请填写文风名称'); return; }
  if (!content) { alert('请填写文风内容'); return; }
  if (id) {
    const idx = writingStyleEntries.findIndex(e => e.id === id);
    if (idx >= 0) {
      writingStyleEntries[idx].name = name;
      writingStyleEntries[idx].content = content;
    }
  } else {
    writingStyleEntries.push({ id: 'ws_' + Date.now(), name, content });
  }
  saveWritingStyleEntries();
  closeWritingStyleModal();
  renderWritingStylePage();
  // 刷新所有联系人的文风下拉
  refreshWritingStyleSelects();
}

// 删除文风条目
function deleteWritingStyleEntry(id) {
  if (!confirm('确认删除此文风条目？')) return;
  writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
  saveWritingStyleEntries();
  renderWritingStylePage();
  refreshWritingStyleSelects();
}

// 刷新聊天设置中的文风下拉
function refreshWritingStyleSelects() {
  const sel = document.getElementById('chat-writing-style-select');
  if (!sel) return;
  const currentVal = sel.value;
  sel.innerHTML = '<option value="">（不使用文风）</option>' +
    writingStyleEntries.map(e => `<option value="${e.id}">${e.name}</option>`).join('');
  sel.value = currentVal;
}

// 显示文风设置页面
function showWritingStylePage() {
  // 隐藏其他页面
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const page = document.getElementById('writing-style-page');
  if (page) {
    page.classList.add('active');
    renderWritingStylePage();
  }
}

// 聊天设置：切换文风时压缩并保存
async function onWritingStyleChange(contactId, styleId) {
  if (!styleId) {
    // 清除文风
    const settings = getContactSettings(contactId);
    settings.writingStyleId = '';
    settings.compressedStyle = '';
    saveContactSettings(contactId, settings);
    return;
  }
  const entry = writingStyleEntries.find(e => e.id === styleId);
  if (!entry) return;

  // 调用 API 压缩文风
  showToast('正在压缩文风内容，请稍候…');
  try {
    const compressed = await compressWritingStyle(entry.content);
    const settings = getContactSettings(contactId);
    settings.writingStyleId = styleId;
    settings.compressedStyle = compressed;
    saveContactSettings(contactId, settings);
    showToast('文风已设置：' + compressed.substring(0, 30) + '…');
  } catch(e) {
    alert('压缩文风时 API 调用失败：' + e.message);
  }
}

// 调用 API 压缩文风（返回约50字的行为准则）
async function compressWritingStyle(styleContent) {
  // 获取当前 API 配置
  const apiUrl = localStorage.getItem('apiUrl') || '';
  const apiKey = localStorage.getItem('apiKey') || '';
  const model = localStorage.getItem('currentModel') || 'gpt-3.5-turbo';
  if (!apiUrl || !apiKey) throw new Error('请先配置 API URL 和 API Key');

  const prompt = `请将以下文风描述压缩为一句话（约50字以内）的行为准则，直接输出结果，不要解释：\\n\\n${styleContent}`;
  const resp = await fetch(apiUrl.replace(/\\/+$/, '') + '/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + apiKey
    },
    body: JSON.stringify({
      model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 150,
      temperature: 0.3
    })
  });
  if (!resp.ok) throw new Error('API 响应错误：' + resp.status);
  const data = await resp.json();
  return data.choices[0].message.content.trim();
}

// 获取联系人设置（如果主程序没有此函数则提供 fallback）
function getContactSettings(contactId) {
  try {
    const key = 'contactSettings_' + contactId;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : {};
  } catch(e) { return {}; }
}

function saveContactSettings(contactId, settings) {
  try {
    const key = 'contactSettings_' + contactId;
    localStorage.setItem(key, JSON.stringify(settings));
  } catch(e) { console.error('保存联系人设置失败', e); }
}

// 在发送消息时附加压缩文风（小尾巴）
function appendCompressedStyle(messageText, contactId) {
  try {
    const settings = getContactSettings(contactId);
    if (settings.compressedStyle) {
      return messageText + '\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：' + settings.compressedStyle + ')';
    }
  } catch(e) {}
  return messageText;
}

// 初始化文风模块
function initWritingStyleModule() {
  loadWritingStyleEntries();
  // 绑定文风设置菜单项
  const menuItem = document.getElementById('writing-style-menu-item');
  if (menuItem) {
    menuItem.addEventListener('click', showWritingStylePage);
  }
  // 绑定模态框按钮
  const saveBtn = document.getElementById('ws-save-btn');
  if (saveBtn) saveBtn.addEventListener('click', saveWritingStyleEntry);
  const cancelBtn = document.getElementById('ws-cancel-btn');
  if (cancelBtn) cancelBtn.addEventListener('click', closeWritingStyleModal);
  const addBtn = document.getElementById('ws-add-btn');
  if (addBtn) addBtn.addEventListener('click', () => openWritingStyleEditor());
}

// 确保在 DOMContentLoaded 后初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initWritingStyleModule);
} else {
  initWritingStyleModule();
}
'''

if "writingStyleModule" not in src:
    src = src + writing_style_js
    print('Step 6 done: writing style JS module added')
else:
    print('Step 6: writing style module already exists')

# ── 7. 修正消息发送时附加文风小尾巴 ─────────────────────────────────────────
# 寻找发送消息构建 userMessage 的地方，附加 appendCompressedStyle 调用
# 常见模式：messages.push({ role: 'user', content: userMessage })
# 我们在 content: userMessage 附近插入转换
patterns_to_try = [
    ("content: userMessage", "content: appendCompressedStyle(userMessage, currentContact)"),
    ("content: userMsg", "content: appendCompressedStyle(userMsg, currentContact)"),
]
appended_style = False
for old_pat, new_pat in patterns_to_try:
    if old_pat in src and new_pat not in src:
        src = src.replace(old_pat, new_pat, 1)
        print(f'Step 7 done: style tail appended via pattern "{old_pat}"')
        appended_style = True
        break

if not appended_style:
    print('Step 7: could not find send pattern automatically (manual check needed)')

# ── 8. 写回 main.js ──────────────────────────────────────────────────────────
with open(MAIN_JS, 'w', encoding='utf-8') as fh:
    fh.write(src)
print(f'main.js written, new length: {len(src)}')

# ── 9. 修改 index.html ────────────────────────────────────────────────────────
with open(INDEX_HTML, 'r', encoding='utf-8-sig') as fh:
    html = fh.read()

# 9a. 在通讯录菜单中添加【文风设置】菜单项
# 寻找"世界书"菜单项并在其后插入
worldbook_menu_patterns = [
    '<li id="worldbook-menu-item"',
    'id="worldbook-menu-item"',
    '世界书',
]
ws_menu_item = '''
              <li id="writing-style-menu-item" class="contacts-menu-item" onclick="showWritingStylePage()">
                <span class="menu-icon">🖊️</span>
                <span class="menu-text">文风设置</span>
              </li>'''

inserted_menu = False
for pat in worldbook_menu_patterns:
    if pat in html:
        # 找到该行的结束，在其后插入
        idx = html.index(pat)
        # 找到下一个 </li> 后面
        end_li = html.index('</li>', idx) + 5
        html = html[:end_li] + ws_menu_item + html[end_li:]
        inserted_menu = True
        print(f'Step 9a done: writing style menu item added after "{pat}"')
        break

if not inserted_menu:
    print('Step 9a: could not find worldbook menu item to insert after')

# 9b. 添加文风设置页面 HTML
writing_style_page_html = '''
  <!-- 文风设置页面 -->
  <div id="writing-style-page" class="page">
    <div class="page-header">
      <button class="back-btn" onclick="history.back()">&#8592;</button>
      <h2>文风设置</h2>
      <button id="ws-add-btn" class="icon-btn" onclick="openWritingStyleEditor()" title="新建文风">＋</button>
    </div>
    <div id="writing-style-list" class="worldbook-list">
      <div class="empty-hint" style="text-align:center;color:#999;padding:40px;">暂无文风条目，点击右上角 ＋ 新建</div>
    </div>
  </div>

  <!-- 文风编辑模态框 -->
  <div id="writing-style-modal" class="modal-overlay" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;align-items:center;justify-content:center;">
    <div class="modal-box" style="background:#fff;border-radius:12px;padding:24px;width:90%;max-width:500px;max-height:80vh;overflow-y:auto;">
      <h3 id="ws-modal-title" style="margin:0 0 16px;">新建文风</h3>
      <input type="hidden" id="ws-entry-id">
      <div style="margin-bottom:12px;">
        <label style="display:block;margin-bottom:4px;font-weight:600;">文风名称</label>
        <input id="ws-entry-name" type="text" placeholder="如：温柔体贴型" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">
      </div>
      <div style="margin-bottom:16px;">
        <label style="display:block;margin-bottom:4px;font-weight:600;">文风内容描述</label>
        <textarea id="ws-entry-content" rows="8" placeholder="详细描述该文风的行为规范、语气风格等……" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;resize:vertical;"></textarea>
      </div>
      <div style="display:flex;gap:8px;justify-content:flex-end;">
        <button id="ws-cancel-btn" onclick="closeWritingStyleModal()" style="padding:8px 20px;border:1px solid #ddd;border-radius:6px;background:#f5f5f5;cursor:pointer;">取消</button>
        <button id="ws-save-btn" onclick="saveWritingStyleEntry()" style="padding:8px 20px;border:none;border-radius:6px;background:#07c160;color:#fff;cursor:pointer;font-weight:600;">保存</button>
      </div>
    </div>
  </div>'''

# 在 </body> 前插入
if 'writing-style-page' not in html:
    html = html.replace('</body>', writing_style_page_html + '\n</body>')
    print('Step 9b done: writing style page HTML added')
else:
    print('Step 9b: writing style page already exists')

# 9c. 在聊天设置区域添加文风单选下拉
# 寻找聊天设置面板（chat-settings 或 contact-settings）中的合适位置
writing_style_chat_setting = '''
    <!-- 文风选择 -->
    <div class="setting-group" id="writing-style-setting-group">
      <div class="setting-label">
        <span>📝 当前聊天文风</span>
      </div>
      <div class="setting-control">
        <select id="chat-writing-style-select" onchange="onWritingStyleSelectChange(this.value)" style="width:100%;padding:6px;border:1px solid #ddd;border-radius:6px;">
          <option value="">（不使用文风）</option>
        </select>
      </div>
      <div class="setting-hint" style="color:#e6a817;font-size:12px;margin-top:6px;padding:6px 8px;background:#fff8e1;border-radius:4px;">
        ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
      </div>
    </div>'''

# 寻找聊天设置里的世界书选择部分，在其后添加文风选择
chat_setting_patterns = [
    'chat-worldbook-setting',
    'worldbook-setting-group',
    'selected-worldbooks',
    'id="chat-settings"',
    'class="chat-settings"',
]

inserted_chat_setting = False
for pat in chat_setting_patterns:
    if pat in html and 'writing-style-setting-group' not in html:
        idx = html.index(pat)
        # 往后找 </div> 关闭该 setting group
        end_div = html.find('</div>', idx)
        if end_div > 0:
            # 找到下一个 setting-group 的起始或面板结束
            next_group = html.find('<div class="setting-group"', end_div)
            end_parent = html.find('</div>', end_div + 1)
            insert_pos = end_div + 6  # 在当前 div 关闭后插入
            html = html[:insert_pos] + writing_style_chat_setting + html[insert_pos:]
            inserted_chat_setting = True
            print(f'Step 9c done: chat writing style select added after "{pat}"')
            break

if not inserted_chat_setting:
    print('Step 9c: could not find chat settings panel to insert writing style select')

# 写回 index.html
with open(INDEX_HTML, 'w', encoding='utf-8') as fh:
    fh.write(html)
print(f'index.html written, new length: {len(html)}')

# ── 10. 在 main.js 中添加 onWritingStyleSelectChange 函数 ─────────────────────
with open(MAIN_JS, 'r', encoding='utf-8') as fh:
    src2 = fh.read()

on_change_fn = '''
// 聊天设置中文风下拉变化时触发
function onWritingStyleSelectChange(styleId) {
  if (!window.currentContact) return;
  onWritingStyleChange(window.currentContact, styleId);
}

// 打开聊天设置时初始化文风下拉
function initChatWritingStyleSelect(contactId) {
  loadWritingStyleEntries();
  const sel = document.getElementById('chat-writing-style-select');
  if (!sel) return;
  sel.innerHTML = '<option value="">（不使用文风）</option>' +
    writingStyleEntries.map(e => `<option value="${e.id}">${e.name}</option>`).join('');
  // 恢复已选择的文风
  try {
    const settings = getContactSettings(contactId);
    sel.value = settings.writingStyleId || '';
  } catch(e) {}
}
'''

if 'onWritingStyleSelectChange' not in src2:
    src2 = src2 + on_change_fn
    with open(MAIN_JS, 'w', encoding='utf-8') as fh:
        fh.write(src2)
    print('Step 10 done: onWritingStyleSelectChange added')
else:
    print('Step 10: already exists')

print('\n=== ALL DONE ===')
print(f'main.js final length: {len(src2)}')
