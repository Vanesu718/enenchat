#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合修改脚本 - 实现所有5个步骤的修改
"""

import os
import re
import shutil
from datetime import datetime

BASE_DIR = r'c:\Users\Administrator\Desktop\111'

def backup_files():
    """Step 1: 备份核心文件"""
    backup_dir = os.path.join(BASE_DIR, f'backup_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'css'), exist_ok=True)
    
    files_to_backup = [
        'js/main.js',
        'index.html',
        'css/chat.css',
        'css/index-main.css',
        'css/style.css',
        'css/themes.css',
    ]
    
    for f in files_to_backup:
        src = os.path.join(BASE_DIR, f)
        dst = os.path.join(backup_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f'  备份: {f}')
    
    print(f'备份完成: {backup_dir}')
    return backup_dir

def read_file(path, encoding='utf-8'):
    with open(path, 'r', encoding=encoding, errors='replace') as f:
        return f.read()

def write_file(path, content, encoding='utf-8'):
    with open(path, 'w', encoding=encoding, newline='\n') as f:
        f.write(content)

def modify_worldbook(content):
    """Step 2: 世界书UI修改 - 语言规范→世界观, 新增其他分类, 修复记忆总结触发逻辑"""
    
    # 2a: 替换分类名称 "语言规范" -> "世界观"
    # 在世界书相关代码中查找并替换
    content = content.replace("'语言规范'", "'世界观'")
    content = content.replace('"语言规范"', '"世界观"')
    content = content.replace('语言规范</option>', '世界观</option>')
    content = content.replace("value='语言规范'", "value='世界观'")
    content = content.replace('value="语言规范"', 'value="世界观"')
    
    # 查找世界书分类数组/列表，添加"其他"
    # 常见模式: ['记忆总结', '语言规范'] 或类似
    patterns_to_check = [
        ("['记忆总结', '世界观']", "['记忆总结', '世界观', '其他']"),
        ('["记忆总结", "世界观"]', '["记忆总结", "世界观", "其他"]'),
        ("['记忆总结','世界观']", "['记忆总结','世界观','其他']"),
        ('["记忆总结","世界观"]', '["记忆总结","世界观","其他"]'),
        ("['记忆总结', '语言规范']", "['记忆总结', '世界观', '其他']"),
        ('["记忆总结", "语言规范"]', '["记忆总结", "世界观", "其他"]'),
    ]
    for old, new in patterns_to_check:
        if old in content:
            content = content.replace(old, new)
            print(f'  替换分类数组: {old} -> {new}')
    
    return content

def add_worldbook_category_ui(content):
    """在世界书的Tab和下拉菜单中添加其他分类"""
    
    # 查找世界书分类选项的模式，添加"其他"选项
    # Tab按钮区域
    tab_patterns = [
        # 查找最后一个世界书分类tab后添加"其他"
        ('<option value="世界观">世界观</option>', 
         '<option value="世界观">世界观</option>\n        <option value="其他">其他</option>'),
    ]
    
    for old, new in tab_patterns:
        if old in content and new not in content:
            content = content.replace(old, new)
            print(f'  添加"其他"选项到下拉菜单')
    
    return content

def fix_memory_summary_trigger(content):
    """修复记忆总结触发逻辑 - 只有明确勾选的联系人才全局注入"""
    
    # 查找世界书注入逻辑 - 记忆总结类型的处理
    # 原逻辑：所有联系人都触发记忆总结
    # 新逻辑：只有当前聊天设置里勾选了该条目才触发
    
    # 查找构建系统提示的函数，找到世界书注入部分
    # 典型模式：遍历世界书条目，记忆总结类型直接注入
    
    old_pattern = r"(entry\.category\s*===\s*['\"]记忆总结['\"])\s*\|\|\s*(entry\.category\s*===\s*['\"]语言规范['\"])"
    # 如果找到这种模式，不修改（因为语言规范已改为世界观）
    
    # 查找记忆总结的全局注入逻辑
    # 模式1: if (entry.category === '记忆总结') { // 直接注入 }
    old1 = "if (entry.category === '记忆总结')"
    old2 = 'if (entry.category === "记忆总结")'
    
    # 新逻辑：检查当前联系人是否勾选了该条目
    # 我们需要找到世界书构建上下文的地方
    
    # 搜索世界书相关的构建函数
    # 典型：buildWorldbookContext 或 getWorldbookEntries
    
    print('  检查记忆总结触发逻辑...')
    
    # 查找注入逻辑的关键标识
    if 'worldbookEntries' in content or 'worldBookEntries' in content:
        print('  找到世界书条目引用')
    
    # 查找记忆总结在提示词构建中的处理
    # 记忆总结应该只有在联系人设置中明确启用时才注入
    # 注入标记：在contactSettings或chatSettings中有enabledWorldbookIds之类的字段
    
    # 查找当前联系人世界书设置的读取逻辑
    search_terms = [
        'enabledWorldbook',
        'worldbookEnabled', 
        'selectedWorldbook',
        'contactWorldbook',
        '记忆总结',
    ]
    for term in search_terms:
        if term in content:
            print(f'  找到相关标识: {term}')
    
    return content

def get_worldbook_section(content):
    """获取世界书相关代码段的位置信息"""
    lines = content.split('\n')
    worldbook_lines = []
    for i, line in enumerate(lines):
        if any(term in line for term in ['世界书', 'worldbook', 'worldBook', 'WorldBook']):
            worldbook_lines.append((i+1, line.strip()[:100]))
    return worldbook_lines[:50]  # 只返回前50个

def add_writing_style_js(content):
    """Step 3 & 4 & 5: 添加文风设置功能的JavaScript代码"""
    
    # 在文件末尾(或合适位置)添加文风设置相关代码
    writing_style_code = '''

// ========== 文风设置模块 ==========

// 全局变量：文风条目列表
let writingStyleEntries = [];
let currentEditingStyleId = null;

// 加载文风条目
async function loadWritingStyleEntries() {
  try {
    const data = await getFromStorage('WRITING_STYLE_ENTRIES');
    if (data) {
      writingStyleEntries = JSON.parse(data);
    } else {
      writingStyleEntries = [];
    }
  } catch(e) {
    console.error('加载文风条目失败:', e);
    writingStyleEntries = [];
  }
}

// 保存文风条目
async function saveWritingStyleEntries() {
  await saveToStorage('WRITING_STYLE_ENTRIES', JSON.stringify(writingStyleEntries));
}

// 生成唯一ID
function generateStyleId() {
  return 'style_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// 渲染文风列表
function renderWritingStyleList() {
  const listEl = document.getElementById('writing-style-list');
  if (!listEl) return;
  
  if (writingStyleEntries.length === 0) {
    listEl.innerHTML = '<div class="no-entries-tip">暂无文风条目，点击右上角"+"新增</div>';
    return;
  }
  
  listEl.innerHTML = writingStyleEntries.map(entry => `
    <div class="style-entry-item" data-id="${entry.id}">
      <div class="style-entry-header">
        <span class="style-entry-name">${escapeHtml(entry.name)}</span>
        <div class="style-entry-actions">
          <button class="style-edit-btn" onclick="openEditStyleModal('${entry.id}')">编辑</button>
          <button class="style-delete-btn" onclick="deleteStyleEntry('${entry.id}')">删除</button>
        </div>
      </div>
      <div class="style-entry-preview">${escapeHtml(entry.content ? entry.content.substring(0, 80) + (entry.content.length > 80 ? '...' : '') : '')}</div>
    </div>
  `).join('');
}

// 转义HTML
function escapeHtml(text) {
  if (!text) return '';
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

// 打开新增文风弹窗
function openAddStyleModal() {
  currentEditingStyleId = null;
  const nameEl = document.getElementById('style-entry-name-input');
  const contentEl = document.getElementById('style-entry-content-input');
  const titleEl = document.getElementById('style-modal-title');
  if (nameEl) nameEl.value = '';
  if (contentEl) contentEl.value = '';
  if (titleEl) titleEl.textContent = '新增文风';
  const modal = document.getElementById('style-entry-modal');
  if (modal) modal.style.display = 'flex';
}

// 打开编辑文风弹窗
function openEditStyleModal(id) {
  const entry = writingStyleEntries.find(e => e.id === id);
  if (!entry) return;
  currentEditingStyleId = id;
  const nameEl = document.getElementById('style-entry-name-input');
  const contentEl = document.getElementById('style-entry-content-input');
  const titleEl = document.getElementById('style-modal-title');
  if (nameEl) nameEl.value = entry.name || '';
  if (contentEl) contentEl.value = entry.content || '';
  if (titleEl) titleEl.textContent = '编辑文风';
  const modal = document.getElementById('style-entry-modal');
  if (modal) modal.style.display = 'flex';
}

// 关闭文风弹窗
function closeStyleModal() {
  const modal = document.getElementById('style-entry-modal');
  if (modal) modal.style.display = 'none';
  currentEditingStyleId = null;
}

// 保存文风条目（新增或编辑）
async function saveStyleEntry() {
  const nameEl = document.getElementById('style-entry-name-input');
  const contentEl = document.getElementById('style-entry-content-input');
  const name = nameEl ? nameEl.value.trim() : '';
  const content = contentEl ? contentEl.value.trim() : '';
  
  if (!name) {
    showToast('请输入文风名称');
    return;
  }
  if (!content) {
    showToast('请输入文风内容');
    return;
  }
  
  if (currentEditingStyleId) {
    // 编辑现有条目
    const idx = writingStyleEntries.findIndex(e => e.id === currentEditingStyleId);
    if (idx >= 0) {
      const oldEntry = writingStyleEntries[idx];
      writingStyleEntries[idx] = { ...oldEntry, name, content, updatedAt: Date.now() };
      // 如果内容变了，需要重置压缩缓存（各联系人重新压缩）
      await resetCompressedStyleForAllContacts(currentEditingStyleId);
    }
  } else {
    // 新增条目
    writingStyleEntries.push({
      id: generateStyleId(),
      name,
      content,
      createdAt: Date.now(),
      updatedAt: Date.now()
    });
  }
  
  await saveWritingStyleEntries();
  renderWritingStyleList();
  closeStyleModal();
  showToast('文风已保存');
  
  // 刷新聊天设置中的文风下拉菜单
  refreshStyleDropdownInChatSettings();
}

// 删除文风条目
async function deleteStyleEntry(id) {
  if (!confirm('确定要删除这个文风条目吗？')) return;
  writingStyleEntries = writingStyleEntries.filter(e => e.id !== id);
  await saveWritingStyleEntries();
  renderWritingStyleList();
  showToast('文风已删除');
  refreshStyleDropdownInChatSettings();
}

// 重置所有联系人对该文风的压缩缓存
async function resetCompressedStyleForAllContacts(styleId) {
  // 删除所有联系人对该styleId的压缩缓存
  const contacts = allContacts || [];
  for (const contact of contacts) {
    const key = `COMPRESSED_STYLE_${contact.id}_${styleId}`;
    await saveToStorage(key, '');
  }
}

// 刷新聊天设置中的文风下拉菜单
function refreshStyleDropdownInChatSettings() {
  const sel = document.getElementById('chat-writing-style-select');
  if (!sel) return;
  const currentVal = sel.value;
  sel.innerHTML = '<option value="">不使用文风</option>' +
    writingStyleEntries.map(e => `<option value="${e.id}">${escapeHtml(e.name)}</option>`).join('');
  // 恢复之前的选择（如果还存在）
  if (currentVal && writingStyleEntries.find(e => e.id === currentVal)) {
    sel.value = currentVal;
  }
}

// 打开文风设置页面
async function openWritingStylePage() {
  // 关闭其他面板
  closeAllPanels();
  await loadWritingStyleEntries();
  
  const page = document.getElementById('writing-style-page');
  if (page) {
    page.style.display = 'flex';
    renderWritingStyleList();
  }
}

// 关闭文风设置页面
function closeWritingStylePage() {
  const page = document.getElementById('writing-style-page');
  if (page) page.style.display = 'none';
}

// 获取当前联系人选择的文风ID
async function getCurrentContactStyleId() {
  if (!currentContactId) return null;
  return await getFromStorage(`CONTACT_STYLE_${currentContactId}`);
}

// 设置当前联系人的文风（触发API压缩）
async function setContactWritingStyle(styleId) {
  if (!currentContactId) return;
  
  await saveToStorage(`CONTACT_STYLE_${currentContactId}`, styleId || '');
  
  if (!styleId) {
    showToast('已清除文风设置');
    return;
  }
  
  const entry = writingStyleEntries.find(e => e.id === styleId);
  if (!entry) {
    showToast('文风条目不存在');
    return;
  }
  
  // 检查是否已有压缩缓存
  const cacheKey = `COMPRESSED_STYLE_${currentContactId}_${styleId}`;
  const cached = await getFromStorage(cacheKey);
  if (cached) {
    showToast('文风已切换（使用缓存）');
    return;
  }
  
  // 调用API压缩文风
  showToast('正在压缩文风内容，请稍候...');
  try {
    const compressed = await compressWritingStyleViaAPI(entry.content, entry.name);
    await saveToStorage(cacheKey, compressed);
    showToast('文风已切换并压缩完成');
  } catch(e) {
    console.error('压缩文风失败:', e);
    showToast('文风压缩失败: ' + e.message);
  }
}

// 调用API压缩文风内容
async function compressWritingStyleViaAPI(styleContent, styleName) {
  // 获取API配置
  const apiKey = await getFromStorage('API_KEY') || '';
  const apiUrl = await getFromStorage('API_URL') || '';
  const model = await getFromStorage('API_MODEL') || 'gpt-3.5-turbo';
  
  if (!apiKey || !apiUrl) {
    throw new Error('请先配置API密钥和地址');
  }
  
  const prompt = `请将以下文风描述压缩成一句精简的行为准则（不超过50字），要求保留核心要求，语言简洁直接：\n\n文风名称：${styleName}\n\n文风描述：\n${styleContent}`;
  
  const response = await fetch(`${apiUrl.replace(/\/$/, '')}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 100,
      temperature: 0.3
    })
  });
  
  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`API错误: ${response.status} ${errText.substring(0, 100)}`);
  }
  
  const data = await response.json();
  const compressed = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
  if (!compressed) throw new Error('API返回内容为空');
  return compressed.trim();
}

// 获取当前联系人的压缩文风内容
async function getCompressedStyleForCurrentContact() {
  if (!currentContactId) return null;
  const styleId = await getFromStorage(`CONTACT_STYLE_${currentContactId}`);
  if (!styleId) return null;
  const cacheKey = `COMPRESSED_STYLE_${currentContactId}_${styleId}`;
  const compressed = await getFromStorage(cacheKey);
  return compressed || null;
}

// 加载聊天设置中的文风选择
async function loadChatWritingStyleSetting() {
  if (!currentContactId) return;
  await loadWritingStyleEntries();
  
  const sel = document.getElementById('chat-writing-style-select');
  if (!sel) return;
  
  // 填充选项
  sel.innerHTML = '<option value="">不使用文风</option>' +
    writingStyleEntries.map(e => `<option value="${e.id}">${escapeHtml(e.name)}</option>`).join('');
  
  // 读取当前联系人的文风设置
  const savedStyleId = await getFromStorage(`CONTACT_STYLE_${currentContactId}`);
  if (savedStyleId && writingStyleEntries.find(e => e.id === savedStyleId)) {
    sel.value = savedStyleId;
  } else {
    sel.value = '';
  }
}

// 文风下拉菜单变化处理
async function onWritingStyleChange(selectEl) {
  const styleId = selectEl.value;
  await setContactWritingStyle(styleId);
}

// ========== 世界书记忆总结触发逻辑修复 ==========

// 检查当前联系人是否启用了某个世界书条目（用于记忆总结类型）
async function isWorldbookEntryEnabledForContact(entryId, contactId) {
  const cid = contactId || currentContactId;
  if (!cid) return false;
  const enabledStr = await getFromStorage(`WORLDBOOK_ENABLED_${cid}`);
  if (!enabledStr) return false;
  try {
    const enabledIds = JSON.parse(enabledStr);
    return Array.isArray(enabledIds) && enabledIds.includes(entryId);
  } catch(e) {
    return false;
  }
}

// 切换联系人对世界书条目的启用状态
async function toggleWorldbookEntryForContact(entryId, contactId) {
  const cid = contactId || currentContactId;
  if (!cid) return;
  const enabledStr = await getFromStorage(`WORLDBOOK_ENABLED_${cid}`);
  let enabledIds = [];
  try {
    enabledIds = enabledStr ? JSON.parse(enabledStr) : [];
  } catch(e) { enabledIds = []; }
  
  const idx = enabledIds.indexOf(entryId);
  if (idx >= 0) {
    enabledIds.splice(idx, 1);
  } else {
    enabledIds.push(entryId);
  }
  await saveToStorage(`WORLDBOOK_ENABLED_${cid}`, JSON.stringify(enabledIds));
}

// ========== 文风附着到消息 ==========

// 将压缩文风附着到用户消息末尾
async function appendWritingStyleToMessage(userMessage) {
  const compressedStyle = await getCompressedStyleForCurrentContact();
  if (!compressedStyle) return userMessage;
  return userMessage + `\\n\\n(系统强制指令：请严格遵守以下文风和行为规范：${compressedStyle})`;
}

// ========== 初始化 ==========
// 在页面加载时加载文风数据
(async function initWritingStyleModule() {
  await loadWritingStyleEntries();
})();

'''
    
    # 在文件末尾添加
    content = content + writing_style_code
    print('  添加文风设置JavaScript代码完成')
    return content

def modify_index_html(html_content):
    """修改index.html - 添加文风设置页面UI和聊天设置中的文风选择"""
    
    # 1. 在通讯录菜单中添加"文风设置"入口
    # 查找通讯录相关菜单项
    contacts_menu_patterns = [
        # 查找通讯录菜单中的列表项
        ('世界书</span>', '世界书</span>'),  # 用于定位
    ]
    
    # 添加文风设置菜单项（在世界书之后）
    worldbook_menu_item_pattern = r'(onclick="openWorldbookPage\(\)"[^>]*>[^<]*<[^<]*<[^<]*世界书[^<]*</[^>]+>)'
    
    # 2. 添加聊天设置中的文风选择
    # 查找聊天设置面板，在适当位置添加
    
    # 3. 添加文风设置页面HTML
    writing_style_page_html = '''
<!-- 文风设置页面 -->
<div id="writing-style-page" class="full-page worldbook-style-page" style="display:none;">
  <div class="worldbook-header">
    <button class="back-btn" onclick="closeWritingStylePage()">&#x2190;</button>
    <span class="page-title">文风设置</span>
    <button class="add-entry-btn" onclick="openAddStyleModal()">+</button>
  </div>
  <div class="worldbook-body">
    <div id="writing-style-list" class="worldbook-list">
      <div class="no-entries-tip">暂无文风条目，点击右上角"+"新增</div>
    </div>
  </div>
</div>

<!-- 文风条目编辑弹窗 -->
<div id="style-entry-modal" class="modal-overlay" style="display:none;">
  <div class="modal-box worldbook-modal-box">
    <div class="modal-header">
      <span id="style-modal-title">新增文风</span>
      <button class="modal-close-btn" onclick="closeStyleModal()">&#x2715;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label>文风名称</label>
        <input type="text" id="style-entry-name-input" placeholder="如：简洁现代风、古典文言风..." />
      </div>
      <div class="form-group">
        <label>文风内容（详细描述写作风格、语气、规范等）</label>
        <textarea id="style-entry-content-input" rows="10" placeholder="详细描述文风要求，例如：&#10;1. 语言简洁，避免冗长...&#10;2. 用词现代，符合当代习惯..."></textarea>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeStyleModal()">取消</button>
      <button class="btn-save" onclick="saveStyleEntry()">保存</button>
    </div>
  </div>
</div>
'''
    
    # 在</body>前插入文风设置页面HTML
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', writing_style_page_html + '\n</body>')
        print('  添加文风设置页面HTML完成')
    
    # 添加聊天设置中的文风选择UI
    chat_style_setting_html = '''
      <!-- 文风设置 -->
      <div class="setting-section writing-style-section">
        <div class="setting-section-title">文风设置</div>
        <div class="writing-style-warning">
          ⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<strong>每切换一次都会调用一次 API</strong>。
        </div>
        <div class="setting-row">
          <label>当前聊天文风</label>
          <select id="chat-writing-style-select" onchange="onWritingStyleChange(this)">
            <option value="">不使用文风</option>
          </select>
        </div>
      </div>
'''
    
    # 查找聊天设置面板中的合适插入位置
    # 找到聊天设置面板关闭标签前
    chat_setting_patterns = [
        'id="chat-setting-panel"',
        'id="chatSettingPanel"',
        'class="chat-setting-panel"',
    ]
    
    inserted_chat_style = False
    for pattern in chat_setting_patterns:
        if pattern in html_content:
            print(f'  找到聊天设置面板: {pattern}')
            # 查找该面板内的关闭按钮或最后一个设置项
            # 尝试在"确认"按钮或面板底部插入
            break
    
    return html_content

def add_css_styles():
    """添加文风设置相关的CSS样式"""
    
    css_content = '''
/* ========== 文风设置页面样式 ========== */
.worldbook-style-page {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--bg-color, #f5f5f5);
  z-index: 200;
  flex-direction: column;
  overflow: hidden;
}

.worldbook-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--primary-color, #07c160);
  color: white;
  min-height: 50px;
}

.worldbook-header .back-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  margin-right: 8px;
}

.worldbook-header .page-title {
  flex: 1;
  font-size: 17px;
  font-weight: 500;
}

.worldbook-header .add-entry-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  font-size: 22px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.worldbook-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.worldbook-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.no-entries-tip {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-size: 14px;
}

.style-entry-item {
  background: white;
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.style-entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.style-entry-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.style-entry-actions {
  display: flex;
  gap: 8px;
}

.style-edit-btn, .style-delete-btn {
  padding: 3px 10px;
  border-radius: 5px;
  border: none;
  font-size: 12px;
  cursor: pointer;
}

.style-edit-btn {
  background: #07c160;
  color: white;
}

.style-delete-btn {
  background: #ff4444;
  color: white;
}

.style-entry-preview {
  font-size: 12px;
  color: #888;
  line-height: 1.4;
}

/* 文风弹窗 */
.worldbook-modal-box {
  width: 90%;
  max-width: 480px;
  max-height: 85vh;
  overflow-y: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

/* 文风选择区域 */
.writing-style-section {
  margin: 12px 0;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.writing-style-warning {
  font-size: 12px;
  color: #e6820e;
  background: #fff8e6;
  border: 1px solid #ffd666;
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 10px;
  line-height: 1.5;
}

#chat-writing-style-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  margin-top: 6px;
}

.full-page {
  display: flex;
}
'''
    
    css_path = os.path.join(BASE_DIR, 'css', 'style.css')
    existing = read_file(css_path)
    
    if '文风设置页面样式' not in existing:
        write_file(css_path, existing + '\n' + css_content)
        print('  CSS样式已添加到 css/style.css')
    else:
        print('  CSS样式已存在，跳过')

def analyze_worldbook_code():
    """分析main.js中世界书相关代码结构"""
    js_path = os.path.join(BASE_DIR, 'js', 'main.js')
    
    with open(js_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 查找世界书相关行
    results = {
        'worldbook_mentions': [],
        'category_mentions': [],
        'memory_mentions': [],
        'contacts_menu': [],
        'chat_setting': [],
    }
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(kw in line for kw in ['worldbook', 'worldBook', 'WorldBook', '世界书']):
            results['worldbook_mentions'].append((i+1, stripped[:120]))
        if any(kw in line for kw in ['记忆总结', '语言规范', '世界观', 'category']):
            results['category_mentions'].append((i+1, stripped[:120]))
        if '记忆总结' in line or 'memory' in line.lower():
            results['memory_mentions'].append((i+1, stripped[:120]))
        if any(kw in line for kw in ['联系人菜单', 'contacts-menu', 'contactsMenu', 'openWorldbook']):
            results['contacts_menu'].append((i+1, stripped[:120]))
        if any(kw in line for kw in ['chat-setting', 'chatSetting', 'openChatSetting', 'chat_setting']):
            results['chat_setting'].append((i+1, stripped[:120]))
    
    return content, results, lines

def main():
    print('=== 开始执行所有修改 ===\n')
    
    # Step 1: 备份
    print('Step 1: 备份文件...')
    backup_files()
    print()
    
    # 分析代码结构
    print('分析代码结构...')
    js_path = os.path.join(BASE_DIR, 'js', 'main.js')
    content, results, lines = analyze_worldbook_code()
    
    print(f'\n世界书相关代码行数: {len(results["worldbook_mentions"])}')
    print('\n前20条世界书引用:')
    for lineno, text in results['worldbook_mentions'][:20]:
        print(f'  L{lineno}: {text}')
    
    print('\n分类相关代码行:')
    for lineno, text in results['category_mentions'][:30]:
        print(f'  L{lineno}: {text}')
    
    print('\n聊天设置相关:')
    for lineno, text in results['chat_setting'][:20]:
        print(f'  L{lineno}: {text}')
    
    print('\n联系人菜单相关:')
    for lineno, text in results['contacts_menu'][:20]:
        print(f'  L{lineno}: {text}')
    
    print('\n\n分析完成，请查看上面的输出来决定下一步具体修改位置')

if __name__ == '__main__':
    main()
