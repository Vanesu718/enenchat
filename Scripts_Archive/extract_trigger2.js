try {
    await window.storage.setItem(key, value);
    return true;
  } catch(e) {
    console.error('保存失败:', key, e);
    return false;
  }
}

async function getFromStorage(key) {
  try {
    return await window.storage.getItem(key);
  } catch(e) {
    console.error('读取失败:', key, e);
    return null;
  }
}

// 主题切换函数
  async function selectTheme(themeName) {
    document.body.classList.remove('theme-pink', 'theme-blue', 'theme-green', 'theme-dark');
    if (themeName) {
      document.body.classList.add(themeName);
      await saveToStorage('THEME_CLASS', themeName);
      try { localStorage.setItem('THEME_CLASS', themeName); } catch(e) {}
    } else {
      await saveToStorage('THEME_CLASS', '');
      try { localStorage.setItem('THEME_CLASS', ''); } catch(e) {}
    }
  // 更新叙事美化页面中的主题勾选状态
  updateThemeChecks(themeName);
  
  if (themeName === 'theme-blue') {
    const card = document.getElementById('statusCard');
    if (card && card.style.display === 'block') {
      card.style.display = 'none';
    }
    // 强制切换到线下模式
    if (!isOfflineMode) {
      isOfflineMode = true;
      if (currentContactId) {
        await saveToStorage(`isOfflineMode_${currentContactId}`, String(isOfflineMode));
      }
      const toggle = document.getElementById('mode-toggle');
      const label = document.getElementById('mode-label');
      if (toggle) toggle.classList.remove('active');
      if (label) label.innerText = '线上模式';
    }
  }
  
  showToast('? 主题已应用');
}

// 更新叙事美化页面中的主题勾选标记
function updateThemeChecks(themeName) {
  const checkDefault = document.getElementById('theme-check-default');
  const checkBlue = document.getElementById('theme-check-blue');
  const checkDark = document.getElementById('theme-check-dark');
  if (!checkDefault) return;
  checkDefault.style.display = (!themeName || themeName === '') ? 'inline' : 'none';
  if (checkBlue) checkBlue.style.display = (themeName === 'theme-blue') ? 'inline' : 'none';
  if (checkDark) checkDark.style.display = (themeName === 'theme-dark') ? 'inline' : 'none';
}

// 同步保存函数（用于需要立即保存的场景）
function saveSyncToStorage(key, value) {
  window.storageSync.setItem(key, value);
}

// ======== 世界书草稿自动保存到IndexedDB（刷新不丢失）========
let _wbDraftTimer = null;
function saveWorldBookDraft() {
  // 编辑已有条目时不覆盖草稿
  if (window._isEditingWb) return;
  clearTimeout(_wbDraftTimer);
  _wbDraftTimer = setTimeout(async () => {
    try {
      const nameEl = document.getElementById('worldbook-name');
      const catEl = document.getElementById('worldbook-category');
      const contentEl = document.getElementById('worldbook-content');
      const kwEl = document.getElementById('worldbook-keywords');
      const triggerEl = document.querySelector('input[name="wb-trigger-type"]:checked');
      const draft = {
        name: nameEl ? nameEl.value : '',
        category: catEl ? catEl.value : '',
        content: contentEl ? contentEl.value : '',
        keywords: kwEl ? kwEl.value : '',
        triggerType: triggerEl ? triggerEl.value : 'always'
      };
      // 只有有内容时才保存草稿
      if (draft.name || draft.content) {
        await saveToStorage('WORLDBOOK_DRAFT', JSON.stringify(draft));
      }
    } catch(e) { console.error('保存世界书草稿失败:', e); }
  }, 600);
}

async function restoreWorldBookDraft() {
  try {
    const draftStr = await getFromStorage('WORLDBOOK_DRAFT');
    if (!draftStr) return;
    const draft = JSON.parse(draftStr);
    if (!draft.name && !draft.content) return; // 空草稿不恢复
    const nameEl = document.getElementById('worldbook-name');
    const catEl = document.getElementById('worldbook-category');
    const contentEl = document.getElementById('worldbook-content');
    const kwEl = document.getElementById('worldbook-keywords');
    if (nameEl) nameEl.value = draft.name || '';
    if (catEl && draft.category) catEl.value = draft.category;
    if (contentEl) contentEl.value = draft.content || '';
    if (kwEl) kwEl.value = draft.keywords || '';
    if (draft.triggerType === 'keyword') {
      const kwRadio = document.querySelector('input[name="wb-trigger-type"][value="keyword"]');
      if (kwRadio) {
        kwRadio.checked = true;
        if (typeof window.toggleWbKeywordInput === 'function') window.toggleWbKeywordInput();
      }
    }
  } catch(e) { console.error('恢复世界书草稿失败:', e); }
}

// 更新时间显示
function updateTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const timeStr = `${hours}:${minutes}`;
  
  // 更新状态栏时间
  const statusTimes = document.querySelectorAll('#status-time, #status-time2, #status-time3');
  statusTimes.forEach(el => {
    if (el) el.textContent = timeStr;
  });
  
  // 更新"我"页面的大时钟
  const currentTime = document.getElementById('currentTime');
  if (currentTime) {
    currentTime.textContent = timeStr;
  }
}

// Toast提示函数 - 替代alert
function showToast(message, duration = 2000) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, duration);
}

// 底部图标永久保存 - 使用 IndexedDB
function pickDock(index) {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = async e => {
    const file = e.target.files?.[0];
    if(!file) return;
    if(file.size > 1 * 1024 * 1024) {
      showToast('?? 图片大小超过1M，请选择更小的图片！');
      return;
    }
    const reader = new FileReader();
    reader.onload = async res => {
      const data = res.target.result;
      const prev = document.getElementById(`prev${index}`);
      const dock = document.getElementById(`dock${index}`);
      
      prev.style.backgroundImage = `url(${data})`;
      prev.style.backgroundSize = 'cover';
      prev.style.backgroundPosition = 'center';
      prev.dataset.src = data;
      
      dock.style.backgroundImage = `url(${data})`;
      dock.style.backgroundSize = 'cover';
      dock.style.backgroundPosition = 'center';
      dock.classList.add('has-custom-icon');
      
      // 使用 IndexedDB 保存
      try {
        await IndexedDBManager.saveImage(`dock${index}`, data, 'image');
        console.log(`? 图标${index}已保存到 IndexedDB`);
      } catch(e) {
        console.error('IndexedDB 保存失败:', e);
        showToast('? 图标保存失败');
      }
    };
    reader.readAsDataURL(file);
  };
  input.click();
}

async function restoreDockIconsOnLoad(){
  for(let i=1;i<=4;i++){
    try {
      let src = await IndexedDBManager.getImage(`dock${i}`);
      if (!src) {
        src = localStorage.getItem(`dock${i}`);
      }
      if(src){
        const dock = document.getElementById(`dock${i}`);
        const prev = document.getElementById(`prev${i}`);
        if(dock) {
          dock.style.backgroundImage = `url(${src})`;
          dock.style.backgroundSize = 'cover';
          dock.style.backgroundPosition = 'center';
          dock.classList.add('has-custom-icon');
        }
        if(prev) {
          prev.style.backgroundImage = `url(${src})`;
          prev.style.backgroundSize = 'cover';
          prev.style.backgroundPosition = 'center';
          prev.dataset.src = src;
        }
      }
    } catch(e) {
      console.error(`加载图标${i}失败:`, e);
      const src = localStorage.getItem(`dock${i}`);
      if(src){
        const dock = document.getElementById(`dock${i}`);
        const prev = document.getElementById(`prev${i}`);
        if(dock) {
          dock.style.backgroundImage = `url(${src})`;
          dock.style.backgroundSize = 'cover';
          dock.style.backgroundPosition = 'center';
          dock.classList.add('has-custom-icon');
        }
        if(prev) {
          prev.style.backgroundImage = `url(${src})`;
          prev.style.backgroundSize = 'cover';
          prev.style.backgroundPosition = 'center';
          prev.dataset.src = src;
        }
      }
    }
  }
}

// 页面正常逻辑
const WORLD_BOOK_PRIORITY_INSTRUCTION = `
【最高优先级指令：世界书绝对遵从】
如果提供了【背景设定/世界书】，你必须将其视为最高准则，优先级高于人设、记忆和任何其他指令。
1. 文风：完全模仿世界书中的叙事风格。
2. 设定：严禁违反世界书中的任何背景设定。
3. 禁忌：绝对不触碰世界书中提到的任何禁忌。
你必须完全按照世界书的内容调整你的文风和内容。`;

async function getContactWorldBookPrompt(contactId) {
  const contactSettingsStr = await getFromStorage(`CHAT_SETTINGS_${contactId}`);
  const contactSettings = contactSettingsStr ? (typeof contactSettingsStr === 'string' ? JSON.parse(contactSettingsStr) : contactSettingsStr) : { useWorldBook: true, selectedWorldBooks: [] };

  let activeWorldBooks = [];
  if (contactSettings.useWorldBook) {
    if (worldBook) activeWorldBooks.push(`全局世界观：\n${worldBook}`);
    if (contactSettings.selectedWorldBooks && contactSettings.selectedWorldBooks.length > 0) {
      const selectedEntries = worldBookEntries.filter(e => contactSettings.selectedWorldBooks.includes(e.id));
      selectedEntries.forEach(entry => {
        if (entry.category === '记忆总结') {
          activeWorldBooks.push(`[${entry.name}]\n${entry.content}`);
        } else if (entry.triggerType !== 'keyword') {
          activeWorldBooks.push(`[${entry.name} - 设定]\n${entry.content}`);
        }
      });
    }
  }
  return activeWorldBooks.length > 0 ? `\n${WORLD_BOOK_PRIORITY_INSTRUCTION}\n【世界书/背景设定】\n${activeWorldBooks.join('\n\n')}\n` : '';
}

// 改为异步加载初始值，先设置默认值
let contacts = [];
let chatRecords = {};
let contactGroups = ['默认'];
let currentContactId = '';
let worldBook = '';
let worldBookEntries = [];
let writingStyles = [];
let activeWritingStyleId = null;
let userMasks = []; // 存储用户面具数据
let _editingUserMaskId = null; // 当前正在编辑的面具ID
let userAvatar = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='36' height='36'><circle cx='18' cy='18' r='17' fill='%23f0b8c8'/><text x='18' y='22' text-anchor='middle' font-size='12' fill='white'>我</text></svg>";
let replyMsg = null;
let isBatchDeleteMode = false;
let selectedMsgIndices = [];
let chatSettings = {
    hideAvatar: false,
    chatBg: '',
    chatUserAvatar: '',
    chatNickname: '',
    sceneSetting: '',
    userMask: '',
    contactMask: '',
    useWorldBook: true
};
let isOfflineMode = false;
let activeAIRequests = new Set();

function isCurrentChatBlueMinimalEnabled(isOfflineMsg, statusData) {
  const currentContact = contacts.find(x => x.id === currentContactId);
  let effectiveOfflineMode = false;
  if (isOfflineMsg !== undefined) {
    effectiveOfflineMode = isOfflineMsg;
  } else if (statusData) {
    effectiveOfflineMode = true;
  }
  return !!(
    currentContactId &&
    currentContact &&
    !currentContact.isGroup &&
    effectiveOfflineMode &&
    document.body.classList.contains('theme-blue')
  );
}

// 异步加载全局变量
async function loadGlobalData() {
  try {
    const rawContacts = await getFromStorage('CHAT_CONTACTS');
    try {
      contacts = rawContacts ? (typeof rawContacts === 'string' ? JSON.parse(rawContacts) : rawContacts) : [];
      if (!Array.isArray(contacts)) contacts = [];
    } catch(e) { console.error('解析联系人失败:', e); contacts = []; }
    
    const rawRecords = await getFromStorage('CHAT_RECORDS');
    try {
      chatRecords = rawRecords ? (typeof rawRecords === 'string' ? JSON.parse(rawRecords) : rawRecords) : {};
      if (typeof chatRecords !== 'object' || Array.isArray(chatRecords)) chatRecords = {};
    } catch(e) { console.error('解析聊天记录失败:', e); chatRecords = {}; }
    
    const rawWb = await getFromStorage('WORLD_BOOK');
    worldBook = rawWb || '';
    
    const rawWbEntries = await getFromStorage('WORLDBOOK_ENTRIES');
    try {
      worldBookEntries = rawWbEntries ? (typeof rawWbEntries === 'string' ? JSON.parse(rawWbEntries) : rawWbEntries) : [];
      if (!Array.isArray(worldBookEntries)) worldBookEntries = [];
    } catch(e) { console.error('解析世界书失败:', e); worldBookEntries = []; }

      const rawUserMasks = await getFromStorage('USER_MASKS');
      try {
        userMasks = rawUserMasks ? (typeof rawUserMasks === 'string' ? JSON.parse(rawUserMasks) : rawUserMasks) : [];
        if (!Array.isArray(userMasks)) userMasks = [];
      } catch(e) { console.error('解析用户面具失败:', e); userMasks = []; }

      const rawWritingStyles = await getFromStorage('WRITING_STYLES');
      try {
        writingStyles = rawWritingStyles ? (typeof rawWritingStyles === 'string' ? JSON.parse(rawWritingStyles) : rawWritingStyles) : [];
        if (!Array.isArray(writingStyles)) writingStyles = [];
      } catch(e) { console.error('解析文风设定失败:', e); writingStyles = []; }
      
      const rawActiveWs = await getFromStorage('ACTIVE_WRITING_STYLE');
      if (rawActiveWs) activeWritingStyleId = rawActiveWs;

      const rawAvatar = await getFromStorage('USER_AVATAR');
    if (rawAvatar) userAvatar = rawAvatar;

    // ?? 页面初始化时重新应用主题类，修复刷新后“勾选还是简约，但实际掉回默认样式”的问题
    const savedThemeClass = await getFromStorage('THEME_CLASS');
    document.body.classList.remove('theme-pink', 'theme-blue', 'theme-green', 'theme-dark');
    if (savedThemeClass) {
      document.body.classList.add(savedThemeClass);
    }
    
    const rawOffline = await getFromStorage('isOfflineMode');
    isOfflineMode = String(rawOffline) === 'true';

    // ?? 如果当前主题是线下简约，则页面初始化时也强制保持线下模式
    if (savedThemeClass === 'theme-blue') {
      isOfflineMode = true;
      await saveToStorage('isOfflineMode', 'true');
    }
  } catch(e) {
    console.error('加载全局数据失败:', e);
  }
}

function navTo(id, el) {
    // 关闭所有sub-page
    document.querySelectorAll('.sub-page').forEach(p => {
        p.classList.remove('show');
    });
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    document.querySelectorAll('.dock-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    document.querySelector('.dock').style.display = 'flex';
    
    const island = document.getElementById('dynamic-island');
    if (id === 'page-chat') {
        island.classList.remove('hidden');
    } else {
        island.classList.add('hidden');
    }
    // 切换到"我"页面时自动更新文字颜色
    if (id === 'page-me') {
        setTimeout(updateMePageTextColor, 100);
    }
    
    // 切换页面时，确保背景设置正确
    const userBgEl = document.getElementById('user-bg');
    if (userBgEl && userBgEl.style.backgroundImage && userBgEl.style.backgroundImage !== 'none') {
        const bgUrl = userBgEl.style.backgroundImage.match(/url\(["']?([^"')]+)["']?\)/);
        if (bgUrl && bgUrl[1]) {
            syncBgToAllPages(bgUrl[1]);
        }
    }
}

let subPageZIndex = 6000;
function openSub(id) { 
    const el = document.getElementById(id);
    
    // 如果打开的是添加用户面具页面且不是编辑状态，重置表单
    if (id === 'add-user-mask' && !_editingUserMaskId) {
        document.getElementById('add-user-mask-title').innerText = '新建用户面具';
        document.getElementById('userMaskId').value = '';
        document.getElementById('userMaskPersona').value = '';
        document.getElementById('userMaskAvatarPreview').innerHTML = `<img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><circle cx='40' cy='40' r='38' fill='%23f8d7e0'/><text x='40' y='45' text-anchor='middle' font-size='20' fill='%23886677'>面具</text></svg>">`;
    }

    // 如果打开的是添加世界书页面，重置一下表单状态
    if (id === 'add-worldbook' && !window._isEditingWb) {
        const nameEl = document.getElementById('worldbook-name');
        if (nameEl) nameEl.value = '';
        const catEl = document.getElementById('worldbook-category');
        if (catEl) catEl.value = '记忆总结';
        const contentEl = document.getElementById('worldbook-content');
        if (contentEl) contentEl.value = '';
        const kwEl = document.getElementById('worldbook-keywords');
        if (kwEl) kwEl.value = '';
        const alwaysRadio = document.querySelector('input[name="wb-trigger-type"][value="always"]');
        if (alwaysRadio) alwaysRadio.checked = true;
        if (typeof window.toggleWbKeywordInput === 'function') window.toggleWbKeywordInput();
        // 恢复未提交的草稿（异步，不阻塞UI）
        restoreWorldBookDraft();
    }
    window._isEditingWb = false;

    // 使用 requestAnimationFrame 确保在下一帧渲染，提高响应速度
    requestAnimationFrame(() => {
        subPageZIndex++;
        el.style.zIndex = subPageZIndex;
        el.classList.add('show'); 
        el.style.visibility = 'visible';
        if(id === 'chat-win') {
            document.querySelector('.dock').style.display = 'none';
            document.getElementById('dynamic-island').classList.add('hidden');
            hideChatRedDot(); // 打开聊天窗口时隐藏红点
        }
        // 初始化聊天设置页面
        if (id === 'chat-settings-page') {
            initChatSettingsPage();
        }
        // 初始化叙事美化页面中的主题勾选状态
        if (id === 'theme-text-setting') {
            getFromStorage('THEME_CLASS').then(savedTheme => {
                updateThemeChecks(savedTheme || '');
            });
        }
    });
}
function closeSub(id) { 
    const el = document.getElementById(id);
    el.classList.remove('show');
    // 重置所有可能的定位样式
    el.style.visibility = '';
    if(id === 'chat-win') {
        document.querySelector('.dock').style.display = 'flex';
        if (document.getElementById('page-chat').classList.contains('active')) {
            document.getElementById('dynamic-island').classList.remove('hidden');
        }
        const searchContainer = document.getElementById('chatSearchContainer');
        if (searchContainer) searchContainer.style.display = 'none';
    }
}

function triggerUpload(id) { document.getElementById(id).click(); }
async function safeSaveAsync(key, value) {
    try {
        await saveToStorage(key, value);
        return true;
    } catch(e) {
        console.error('保存失败:', key, e);
        showToast('?? 存储空间不足！请清理数据或使用图片链接');
        // 尝试清理旧数据后重试
        if (await cleanupOldDataAsync()) {
            try {
                await saveToStorage(key, value);
                showToast('? 清理后保存成功');
                return true;
            } catch(e2) {
                showToast('? 存储空间严重不足，请手动清理');
                return false;
            }
        }
        return false;
    }
}

// 兼容旧的同步调用，但建议后续全部改为异步
function safeSave(key, value) {
    console.warn('正在调用同步 safeSave，建议改为异步 safeSaveAsync:', key);
    saveSyncToStorage(key, value);
    return true;
}

// 清理旧数据释放空间 (异步)
async function cleanupOldDataAsync() {
    try {
        // 1. 清理超过50条的聊天记录
        Object.keys(chatRecords).forEach(contactId => {
            if (chatRecords[contactId] && chatRecords[contactId].length > 50) {
                chatRecords[contactId] = chatRecords[contactId].slice(-50);
            }
        });
        await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
        
        // 2. 清理超过30条的朋友圈
        if (moments.length > 30) {
            moments = moments.slice(0, 30);
            await saveMomentsToDB();
        }
        
          // 3. 不再清理世界书条目，因为它们是用户永久保存的记忆
          // 取消清理限制，让世界书可以无限保存
        
        showToast('? 已自动清理旧数据');
        return true;
    } catch(e) {
        console.error('清理失败:', e);
        return false;
    }
}

// 兼容旧的同步调用
function cleanupOldData() {
    console.warn('正在调用同步 cleanupOldData，建议改为异步 cleanupOldDataAsync');
    cleanupOldDataAsync();
    return true;
}

// 检查存储空间使用情况
async function checkStorageUsage() {
    try {
      const storageInfo = await IndexedDBManager.getStorageInfo();
      console.log('?? IndexedDB 存储空间:', storageInfo);
      return storageInfo;
    } catch(e) {
      console.error('检查存储空间失败:', e);
      return { usedMB: '0', percentage: '0' };
    }
}

function hdlImg(input, tid, type) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
// 统一压缩所有图片
        compressAndSave(file, tid, type);
    }
}

// 替换所有alert为自定义的Toast以防手机端报错
window.alert = function(msg) {
    showToast(msg, 3000);
};

// 保存原生prompt引用（必须在任何覆盖之前）
const _nativePrompt = window.prompt.bind(window);

// 覆盖prompt，使用原生实现但增加错误处理
window.prompt = function(msg, defaultText = '') {
    try {
        return _nativePrompt(msg, defaultText);
    } catch (e) {
        console.error('Prompt failed:', e);
        return defaultText;
    }
};

// 压缩大图片后保存（使用 IndexedDB）
async function compressAndSave(file, tid, type) {
    const reader = new FileReader();
    reader.onload = async e => {
        const img = new Image();
        img.onload = async () => {
            const canvas = document.createElement('canvas');
            const maxSize = 800;
            let w = img.width, h = img.height;
            if (w > maxSize || h > maxSize) {
                if (w > h) { h = h * maxSize / w; w = maxSize; }
                else { w = w * maxSize / h; h = maxSize; }
            }
            canvas.width = w;
            canvas.height = h;
            canvas.getContext('2d').drawImage(img, 0, 0, w, h);
            const compressed = canvas.toDataURL('image/jpeg', 0.7);
            
            const el = document.getElementById(tid);
            if(type==='img') {
                el.src = compressed;
                if(tid === 'user-avatar') {
                  userAvatar = compressed;
                  safeSaveAsync('USER_AVATAR', userAvatar);
                }
            } else {
                el.style.backgroundImage = `url(${compressed})`;
                el.style.backgroundSize = 'cover';
                el.style.backgroundPosition = 'center';
            }
            
            // ?? 使用 IndexedDB 保存图片
            try {
                await IndexedDBManager.saveImage('SVD_'+tid, compressed, 'image');
                console.log(`??? 图片已保存到 IndexedDB: SVD_${tid}`);
                showToast('??? 图片已保存！');
            } catch(e) {
                console.error('IndexedDB 保存失败，回退到 storage:', e);
                await safeSaveAsync('SVD_'+tid, compressed);
            }
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

let currentContactGroupFilter = 'all';

// ========== 分组管理功能 ==========
async function loadContactGroups() {
  const saved = await getFromStorage('CONTACT_GROUPS');
  if (saved) {
    try {
      contactGroups = typeof saved === 'string' ? JSON.parse(saved) : saved;
      if (!Array.isArray(contactGroups)) contactGroups = ['默认'];
    } catch(e) { contactGroups = ['默认']; }
  }
  // 确保"默认"分组始终存在
  if (!contactGroups.includes('默认')) {
    contactGroups.unshift('默认');
  }
  // 从联系人中收集已有分组（兼容旧数据）
  contacts.forEach(c => {
    if (c.group && !contactGroups.includes(c.group)) {
      contactGroups.push(c.group);
    }
  });
  renderGroupTabs();
  updateGroupDropdowns();
  renderGroupManageList();
}

async function saveContactGroups() {
  await saveToStorage('CONTACT_GROUPS', JSON.stringify(contactGroups));
}

async function addGroup() {
  const input = document.getElementById('new-group-name');
  const name = input.value.trim();
  if (!name) { showToast('请输入分组名称'); return; }
  if (contactGroups.includes(name)) { showToast('该分组已存在'); return; }
  contactGroups.push(name);
  await saveContactGroups();
  input.value = '';
  renderGroupTabs();
  updateGroupDropdowns();
  renderGroupManageList();
  showToast('? 分组已添加');
}

async function deleteGroup(name) {
  if (name === '默认') { showToast('默认分组不可删除'); return; }
  if (!confirm(`确定删除分组"${name}"吗？该分组下的联系人将移至"默认"分组。`)) return;
  // 将该分组下的联系人移至默认
  contacts.forEach(c => {
    if (c.group === name) c.group = '默认';
  });
  await saveToStorage('CHAT_CONTACTS', JSON.stringify(contacts));
  contactGroups = contactGroups.filter(g => g !== name);
  await saveContactGroups();
  renderGroupTabs();
  updateGroupDropdowns();
  renderGroupManageList();
  renderContactList();
  showToast('??? 分组已删除');
}

// renderGroupTabs 已废弃，改为折叠菜单，保留空函数避免报错
function renderGroupTabs() {}

function updateGroupDropdowns() {
  // 更新新建联系人页面的分组下拉
  const contactGroupSelect = document.getElementById('contactGroup');
  if (contactGroupSelect) {
    contactGroupSelect.innerHTML = '';
    contactGroups.forEach(g => {
      const opt = document.createElement('option');
      opt.value = g;
      opt.textContent = g;
      contactGroupSelect.appendChild(opt);
    });
  }
  // 更新聊天设置页面的分组下拉
  const chatContactGroupSelect = document.getElementById('chatContactGroup');
  if (chatContactGroupSelect) {
    const currentVal = chatContactGroupSelect.value;
    chatContactGroupSelect.innerHTML = '';
    contactGroups.forEach(g => {
      const opt = document.createElement('option');
      opt.value = g;
      opt.textContent = g;
      chatContactGroupSelect.appendChild(opt);
    });
    // 恢复当前联系人的分组选中状态
    if (currentContactId) {
      const contact = contacts.find(c => c.id === currentContactId);
      if (contact) {
        chatContactGroupSelect.value = contact.group || '默认';
      }
    }
  }
}

function renderGroupManageList() {
  const container = document.getElementById('group-list-container');
  if (!container) return;
  container.innerHTML = '';
  
  contactGroups.forEach((g, index) => {
    const count = contacts.filter(c => (c.group || '默认') === g).length;
    const div = document.createElement('div');
    div.className = 'group-item-drag';
    div.dataset.index = index;
    div.dataset.group = g;
    div.style.cssText = 'display:flex; align-items:center; justify-content:space-between; padding:12px 15px; background:#fff; border-radius:12px; margin-bottom:8px; box-shadow:0 2px 6px rgba(0,0,0,0.05); cursor:grab;';
    
    div.innerHTML = `
      <div style="display:flex; align-items:center; flex:1;">
        <div class="drag-handle" style="color:#ccc; margin-right:15px; font-size:20px; padding: 5px;">?</div>
        <div>
          <div style="font-size:15px; color:var(--text-dark); font-weight:500;">${g}</div>
          <div style="font-size:12px; color:var(--text-light); margin-top:2px;">${count} 个联系人</div>
        </div>
      </div>
      ${g !== '默认' ? `<button onclick="deleteGroup('${g.replace(/'/g, "\\'")}')" style="padding:6px 12px; background:#ffcdd2; border:none; border-radius:8px; cursor:pointer; color:#c62828; font-size:13px; position:relative; z-index:2;">删除</button>` : '<span style="font-size:12px; color:var(--text-light);">默认</span>'}
    `;
    container.appendChild(div);
  });

  if (container._sortable) {
    container._sortable.destroy();
  }
  container._sortable = new Sortable(container, {
    animation: 150,
    filter: 'button',
    delay: 100,
    delayOnTouchOnly: true,
    fallbackTolerance: 5,
    onEnd: async function (evt) {
      const newItems = [...container.querySelectorAll('.group-item-drag')];
      const newOrder = newItems.map(item => item.dataset.group);
      
      let orderChanged = false;
      if (newOrder.length === contactGroups.length) {
        for (let i = 0; i < contactGroups.length; i++) {
          if (contactGroups[i] !== newOrder[i]) {
            orderChanged = true;
            break;
          }
        }
      }
      
      if (orderChanged) {
        contactGroups = newOrder;
        await saveContactGroups();
        renderContactList();
        updateGroupDropdowns();
      }
    }
  });
}

function filterContacts(groupName) {
  currentContactGroupFilter = groupName;
  // 更新标签样式
  document.querySelectorAll('.group-tab').forEach(tab => {
    if (tab.dataset.group === groupName) {
      tab.style.background = 'var(--main-pink)';
      tab.style.color = 'white';
    } else {
      tab.style.background = '#f5f5f5';
      tab.style.color = 'var(--text-dark)';
    }
  });
  renderContactList();
}

// 记录每个分组的展开/折叠状态
let groupCollapsedState = {};

function renderContactList() {
  const el = document.getElementById('contactList');
  
  if (contacts.length === 0) {
    el.innerHTML = '<div class="empty-tip">暂无联系人<br>点击右上角 + 添加</div>';
    return;
  }
  el.innerHTML = '';
  
  // 按分组归类联系人
  const groupMap = {};
  contacts.forEach(c => {
    const g = c.group || '默认';
    if (!groupMap[g]) groupMap[g] = [];
    groupMap[g].push(c);
  });
  
  // 按 contactGroups 顺序渲染，再补充未在列表中的分组
  const orderedGroups = [...contactGroups];
  Object.keys(groupMap).forEach(g => {
    if (!orderedGroups.includes(g)) orderedGroups.push(g);
  });
  
  orderedGroups.forEach(groupName => {
    const groupContacts = groupMap[groupName];
    if (!groupContacts || groupContacts.length === 0) return;
    
    // 默认展开（如果没有记录过折叠状态）
    const isCollapsed = groupCollapsedState[groupName] === true;
    
    // 按最后对话时间排序
    const sorted = [...groupContacts].sort((a, b) => {
      const aRecs = chatRecords[a.id] || [];
      const bRecs = chatRecords[b.id] || [];
      const getTime = (recs, ct) => recs.length > 0 ? (recs[recs.length - 1].time || 0) : (parseInt(ct.id) || 0);
      return getTime(bRecs, b) - getTime(aRecs, a);
    });
    
    const groupContainer = document.createElement('div');
    groupContainer.className = 'contact-group-container';
    groupContainer.dataset.group = groupName;
    groupContainer.style.marginBottom = '10px';
    
    // 分组标题（可折叠）
    const header = document.createElement('div');
    header.className = 'contact-group-header';
    header.style.cssText = 'display:flex; align-items:center; padding:10px 5px 6px; cursor:grab; user-select:none; color:var(--text-dark);';
    header.innerHTML = `
      <span style="font-size:12px; color:inherit; margin-right:6px; transition:transform 0.2s; display:inline-block; transform:rotate(${isCollapsed ? '0' : '90'}deg);">?</span>
      <span style="font-size:14px; font-weight:600; color:inherit; pointer-events:none;">${groupName}</span>
      <span style="font-size:12px; color:inherit; margin-left:6px; pointer-events:none;">(${sorted.length})</span>
    `;
    
    // 联系人容器
    const body = document.createElement('div');
    body.style.display = isCollapsed ? 'none' : 'block';
    
    sorted.forEach(c => {
      const recs = chatRecords[c.id] || [];
      let lastMsg = '暂无消息';
      if (recs.length > 0) {
        const msg = recs[recs.length - 1].content;
        lastMsg = msg.replace(/<STATUS>[\s\S]*?<\/STATUS>/g, '').trim();
      }
      const div = document.createElement('div');
      div.className = 'contact-item';
      const ringClass = c.isMarried && !c.isGroup ? ' ring-avatar-frame' : '';
      const displayName = c.isGroup ? `${c.name} (${c.members ? c.members.length : 0})` : c.name;
      div.innerHTML = `
        <div class="contact-avatar${ringClass}"><img src="${c.avatar}"></div>
        <div class="contact-info" style="flex:1; overflow:hidden;">
          <div class="contact-name">${displayName}</div>
          <div class="contact-desc" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${lastMsg}</div>
        </div>
      `;
      div.onclick = () => openChatPage(c);
      body.appendChild(div);
    });
    
    // 点击标题切换折叠
    header.onclick = (e) => {
      const arrow = header.querySelector('span');
      if (body.style.display === 'none') {
        body.style.display = 'block';
        arrow.style.transform = 'rotate(90deg)';
        groupCollapsedState[groupName] = false;
      } else {
        body.style.display = 'none';
        arrow.style.transform = 'rotate(0deg)';
        groupCollapsedState[groupName] = true;
      }
    };
    
    groupContainer.appendChild(header);
    groupContainer.appendChild(body);
    el.appendChild(groupContainer);
  });

  if (el._sortable) {
    el._sortable.destroy();
  }
  el._sortable = new Sortable(el, {
    handle: '.contact-group-header',
    animation: 150,
    delay: 200,
    delayOnTouchOnly: true,
    fallbackTolerance: 5,
    onEnd: async function (evt) {
      const newItems = [...el.querySelectorAll('.contact-group-container')];
      const newOrder = newItems.map(item => item.dataset.group);
      
      const updatedGroups = [...newOrder];
      contactGroups.forEach(g => {
        if (!updatedGroups.includes(g)) {
          updatedGroups.push(g);
        }
      });
      
      let orderChanged = false;
      if (updatedGroups.length === contactGroups.length) {
        for (let i = 0; i < contactGroups.length; i++) {
          if (contactGroups[i] !== updatedGroups[i]) {
            orderChanged = true;
            break;
          }
        }
      }
      
      if (orderChanged) {
        contactGroups = updatedGroups;
        await saveContactGroups();
        updateGroupDropdowns();
        renderGroupManageList();
      }
    }
  });
}

function previewAvatarFile(input) {
  const f = input.files?.[0];
  if (!f) return;
  
  // 压缩图片
  const r = new FileReader();
  r.onload = e => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const maxSize = 800;
      let w = img.width, h = img.height;
      if (w > maxSize || h > maxSize) {
        if (w > h) { h = h * maxSize / w; w = maxSize; }
        else { w = w * maxSize / h; h = maxSize; }
      }
      canvas.width = w;
      canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      const compressed = canvas.toDataURL('image/jpeg', 0.7);
      document.getElementById('avatarPreview').innerHTML = `<img src="${compressed}">`;
    };
    img.src = e.target.result;
  };
  r.readAsDataURL(f);
}
function uploadAvatarByUrl() {
  const u = prompt('图片链接：');
  if (u) document.getElementById('avatarPreview').innerHTML = `<img src="${u}">`;
}

// 导入人设文档 - 支持txt和docx格式
function importPersonaFile(input) {
  const file = input.files?.[0];
  if (!file) return;
  
  // 检查文件大小（1M = 1024 * 1024 bytes）
  if (file.size > 1 * 1024 * 1024) {
    alert('?? 文件大小超过1M，请选择更小的文件！');
    input.value = '';
    return;
  }
  
  const fileName = file.name.toLowerCase();
  
  // 处理txt文件
  if (fileName.endsWith('.txt')) {
    const reader = new FileReader();
    reader.onload = e => {
      const content = e.target.result;
      const textarea = document.getElementById('contactPersona');
      textarea.value = content;
      alert('? 文档内容已成功导入！');
    };
    reader.onerror = () => {
      alert('? 文件读取失败，请重试！');
    };
    reader.readAsText(file, 'UTF-8');
    input.value = '';
    return;
  }
  
  // 处理docx文件（使用mammoth.js）
  if (fileName.endsWith('.docx')) {
    // 检查mammoth库是否加载
    if (typeof mammoth === 'undefined') {
      alert('?? Word文档解析库未加载！请刷新页面重试。');
      input.value = '';
      return;
    }
    
    const reader = new FileReader();
    reader.onload = e => {
      const arrayBuffer = e.target.result;
      
      // 使用mammoth解析docx
      mammoth.extractRawText({ arrayBuffer: arrayBuffer })
        .then(result => {
          const text = result.value.trim();
          if (text) {
            const textarea = document.getElementById('contactPersona');
            textarea.value = text;
            alert('? Word文档内容已成功导入！');
          } else {
            alert('?? 文档内容为空或无法解析！');
          }
        })
        .catch(err => {
          console.error('docx解析失败:', err);
          alert('? Word文档解析失败！\n\n建议：\n1. 确保文件是有效的.docx格式\n2. 或将文档另存为.txt格式后重新上传');
        });
    };
    reader.onerror = () => {
      alert('? 文件读取失败，请重试！');
    };
    reader.readAsArrayBuffer(file);
    input.value = '';
    return;
  }
  
  // 不支持的格式
  alert('?? 不支持的文件格式！\n\n支持的格式：\n?? .txt（纯文本）\n?? .docx（Word 2007及以上版本）\n\n注意：不支持.doc（旧版Word）和.wps格式');
  input.value = '';
}

// 导入世界书文档 - 支持txt和docx格式
function importWorldBookFile(input) {
  const file = input.files?.[0];
  if (!file) return;
  
  // 检查文件大小（1M = 1024 * 1024 bytes）
  if (file.size > 1 * 1024 * 1024) {
    showToast('?? 文件大小超过1M，请选择更小的文件！');
    input.value = '';
    return;
  }
  
  const fileName = file.name.toLowerCase();
  
  // 处理txt文件
  if (fileName.endsWith('.txt')) {
    const reader = new FileReader();
    reader.onload = e => {
      const content = e.target.result;
      const textarea = document.getElementById('worldbook-content');
      textarea.value = content;
      showToast('? 文档内容已成功导入！');
    };
    reader.onerror = () => {
      showToast('? 文件读取失败，请重试！');
    };
    reader.readAsText(file, 'UTF-8');
    input.value = '';
    return;
  }
  
  // 处理docx文件（使用mammoth.js）
  if (fileName.endsWith('.docx')) {
    // 检查mammoth库是否加载
    if (typeof mammoth === 'undefined') {
      showToast('?? Word文档解析库未加载！请刷新页面重试。');
      input.value = '';
      return;
    }
    
    const reader = new FileReader();
    reader.onload = e => {
      const arrayBuffer = e.target.result;
      
      // 使用mammoth解析docx
      mammoth.extractRawText({ arrayBuffer: arrayBuffer })
        .then(result => {
          const text = result.value.trim();
          if (text) {
            const textarea = document.getElementById('worldbook-content');
            textarea.value = text;
            showToast('? Word文档内容已成功导入！');
          } else {
            showToast('?? 文档内容为空或无法解析！');
          }
        })
        .catch(err => {
          console.error('docx解析失败:', err);
          showToast('? Word文档解析失败！建议将文档另存为.txt格式后重新上传');
        });
    };
    reader.onerror = () => {
      showToast('? 文件读取失败，请重试！');
    };
    reader.readAsArrayBuffer(file);
    input.value = '';
    return;
  }
  
  // 不支持的格式
  showToast('?? 不支持的文件格式！仅支持 .txt 和 .docx 格式');
  input.value = '';
}


function openAddGroupChat() {
  const listEl = document.getElementById('groupChatMembersList');
  listEl.innerHTML = '';
  const regularContacts = contacts.filter(c => !c.isGroup);
  if (regularContacts.length === 0) {
    listEl.innerHTML = '<div style="text-align:center; color:#999; padding:20px;">暂无联系人，请先添加角色</div>';
  } else {
    regularContacts.forEach(c => {
      const div = document.createElement('div');
      div.style.cssText = 'display:flex; align-items:center; padding:8px 0; border-bottom:1px solid #f0e8df;';
      div.innerHTML = `
        <input type="checkbox" id="gmember-${c.id}" value="${c.id}" style="width:18px; height:18px; margin-right:10px; cursor:pointer;">
        <img src="${c.avatar}" style="width:30px; height:30px; border-radius:50%; margin-right:10px; object-fit:cover;">
        <label for="gmember-${c.id}" style="flex:1; cursor:pointer; font-size:14px; color:var(--text-dark);">${c.name}</label>
      `;
      listEl.appendChild(div);
    });
  }
  document.getElementById('groupChatName').value = '';
  document.getElementById('groupAvatarPreview').innerHTML = `<img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><circle cx='40' cy='40' r='38' fill='%23f8d7e0'/><text x='40' y='45' text-anchor='middle' font-size='20' fill='%23886677'>群</text></svg>">`;
  originalOpenSub('addGroupChat');
}

// Intercept openSub to handle addGroupChat and add-forum-board-page initialization
const originalOpenSub = openSub;
openSub = function(id) {
  if (id === 'addGroupChat') {
    openAddGroupChat();
    return;
  }
  if (id === 'add-forum-board-page') {
    originalOpenSub(id);
    renderAddForumBoardPage();
    return;
  }
  originalOpenSub(id);
};

function previewGroupAvatarFile(input) {
  const f = input.files?.[0];
  if (!f) return;
  const r = new FileReader();
  r.onload = e => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const maxSize = 800;
      let w = img.width, h = img.height;
      if (w > maxSize || h > maxSize) {
        if (w > h) { h = h * maxSize / w; w = maxSize; }
        else { w = w * maxSize / h; h = maxSize; }
      }
      canvas.width = w;
      canvas.height = h;
      canvas.getContext('2d').drawImage(img, 0, 0, w, h);
      const compressed = canvas.toDataURL('image/jpeg', 0.7);
      document.getElementById('groupAvatarPreview').innerHTML = `<img src="${compressed}">`;
    };
    img.src = e.target.result;
  };
  r.readAsDataURL(f);
}

function uploadGroupAvatarByUrl() {
  const u = prompt('图片链接：');
  if (u) document.getElementById('groupAvatarPreview').innerHTML = `<img src="${u}">`;
}

async function saveGroupChat() {
  const name = document.getElementById('groupChatName').value.trim();
  const avatar = document.querySelector('#groupAvatarPreview img').src;
  
  const checkboxes = document.querySelectorAll('#groupChatMembersList input[type="checkbox"]:checked');
  const members = Array.from(checkboxes).map(cb => cb.value);
  
  if (!name) { showToast('请输入群名称'); return; }
  if (members.length < 2) { showToast('请至少选择2个群成员'); return; }
  
  contacts.push({ 
    id: 'group_' + Date.now().toString(), 
    name, 
    group: '默认', 
    isGroup: true,
    members: members,
    avatar 
  });
  
  try {
    await saveToStorage('CHAT_CONTACTS', JSON.stringify(contacts));
    renderContactList();
    showToast('? 群聊已创建！');
    closeSub('addGroupChat');
  } catch(e) {
    showToast('? 保存失败：' + e.message);
  }
}

  async function saveContact() {
    const name = document.getElementById('contactName').value.trim();
    const group = document.getElementById('contactGroup').value || '默认';
    const p = document.getElementById('contactPersona').value.trim();
    const memo = document.getElementById('contactMemo').value.trim();
    const avatar = document.querySelector('#avatarPreview img').src;
    if (!name) { 
      showToast('请输入名称');
      return; 
    }
    
    const newId = Date.now().toString();
    contacts.push({ id: newId, name, group, persona: p, avatar });

    let finalMemo = memo;

    if (p && !memo) {
      try {
        const cfgStr = await getFromStorage('AI_CHAT_CONFIG');
        const cfg = cfgStr ? (typeof cfgStr === 'string' ? JSON.parse(cfgStr) : cfgStr) : {};
        if (cfg.key && cfg.url && cfg.model) {
          showToast('? AI 正在自动提炼核心设定，请稍候...');
          const prompt = `请将以下长篇人设浓缩为 1-2 句话（限100字），重点保留角色的核心设定与当前与用户的关系、此时的情绪状态等\n\n${p}\n\n只返回文本摘要，不要任何前缀或引号。`;
          const res = await fetch(`${cfg.url}/chat/completions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${cfg.key}` },
            body: JSON.stringify({
              model: cfg.model,
              temperature: 0.5,
              messages: [{ role: 'user', content: prompt }]
            })
          });
          const data = await res.json();
          let summary = data.choices?.[0]?.message?.content || '';
          summary = summary.replace(/^"|"$/g, '').trim();
          finalMemo = summary;
          document.getElementById('contactMemo').value = summary; // 生成到文本框中
        }
      } catch(e) { 
        console.error('自动提取人设摘要失败', e);
        showToast('? 自动提炼失败，将保存为空');
      }
    }
    
    try {
      await saveToStorage('CHAT_CONTACTS', JSON.stringify(contacts));
      
      // 保存到对应的聊天设置中，确保基础属性齐全
      const newSettings = {
        chatNickname: "你",
        sceneSetting: "",
        userMask: "",
        contactMask: "",
        contactMemo: finalMemo || "",
        hideAvatar: false,
        chatBg: '',
        chatUserAvatar: '',
        useWorldBook: true,
        selectedWorldBooks: []
      };
      await saveToStorage(`CHAT_SETTINGS_${newId}`, JSON.stringify(newSettings));
      
      renderContactList();
      showToast('? 联系人已永久保存');
      
      // 等待一下让用户能看到提炼结果
      setTimeout(() => {
        closeSub('addContact');
        // 清空输入框，防止下次打开时还有残留内容
        document.getElementById('contactName').value = '';
        document.getElementById('contactPersona').value = '';
        document.getElementById('contactMemo').value = '';
      }, finalMemo && !memo ? 1000 : 0);
    } catch(e) {
      showToast('? 保存失败: ' + e.message);
    }
  }


async function openChatPage(contact) {
  currentContactId = contact.id;
  window.aiReplyCounter = 0; // 切换联系人时重置人设发送计数器
  // 立即更新标题，提升响应感
  document.getElementById('chatHeaderTitle').innerText = contact.name + (contact.isGroup ? ` (${contact.members.length})` : '');
  const ringClass = contact.isMarried && !contact.isGroup ? 'class="ring-avatar-frame"' : '';
  document.getElementById('chatHeaderAvatar').innerHTML = `<div ${ringClass}><img src="${contact.avatar}"></div>`;
  
  // 初始化群聊发言人索引
  if (contact.isGroup) {
    if (typeof window.groupSpeakerIndices === 'undefined') {
      window.groupSpeakerIndices = {};
    }
    if (window.groupSpeakerIndices[contact.id] === undefined) {
      window.groupSpeakerIndices[contact.id] = 0;
    }
  }
  
  // 清空旧内容，防止切换瞬间看到别人的消息
  document.getElementById('chatContent').innerHTML = '';
  
  cancelReply();
  exitBatchDelete();
  
  // 重置输入状态
  document.getElementById('typingStatus').style.display = 'none';
  hideLoading();
  
  // 先恢复当前联系人的模式，再渲染，避免切窗口时先按旧状态渲染导致“掉回初始模式”
  if (contact.isGroup) {
    isOfflineMode = false;
    await saveToStorage(`isOfflineMode_${contact.id}`, 'false');
  } else {
    const rawContactOffline = await getFromStorage(`isOfflineMode_${contact.id}`);
    if (rawContactOffline !== null) {
      isOfflineMode = String(rawContactOffline) === 'true';
    } else {
      const rawGlobal = await getFromStorage('isOfflineMode');
      isOfflineMode = String(rawGlobal) === 'true';
    }

    if (document.body.classList.contains('theme-blue')) {
      isOfflineMode = true;
      await saveToStorage(`isOfflineMode_${contact.id}`, 'true');
    }
  }

  // 核心：先跳转页面，再异步加载内容
  openSub('chat-win');
  
  // 异步加载设置和渲染，不阻塞跳转动画
  await loadChatSettings();
  renderChat();
  
  if (activeAIRequests.has(currentContactId)) {
    document.getElementById('typingStatus').style.display = 'inline';
    showLoading();
  } else {
    document.getElementById('typingStatus').style.display = 'none';
    hideLoading();
  }
  

  // 更新UI开关状态
  const toggle = document.getElementById('mode-toggle');
  const label = document.getElementById('mode-label');
  if (isOfflineMode) {
    toggle.classList.remove('active'); // 线下模式 = 灰色（关闭状态）
  } else {
    toggle.classList.add('active'); // 线上模式 = 粉色（打开状态）
  }
  if (label) label.innerText = '线上模式';
}

async function toggleMode() {
  if (document.body.classList.contains('theme-blue')) {
    showToast('线下简约模式不支持切换为线上模式');
    return;
  }

  isOfflineMode = !isOfflineMode;
  // ?? 保存为当前联系人独立的模式设置
  if (currentContactId) {
    await saveToStorage(`isOfflineMode_${currentContactId}`, String(isOfflineMode));
  }
  const toggle = document.getElementById('mode-toggle');
  const label = document.getElementById('mode-label');
  if (isOfflineMode) {
    toggle.classList.remove('active'); // 灰色 = 线下模式
  } else {
    toggle.classList.add('active'); // 粉色 = 线上模式
  }
  if (label) label.innerText = '线上模式';
  showToast(isOfflineMode ? '已切换为线下模式 ??' : '已切换为线上模式 ??');
}

function renderChat(forceStartIdx) {
  const el = document.getElementById('chatContent');
  const rec = chatRecords[currentContactId] || [];
  const c = contacts.find(x => x.id === currentContactId);
  if (!c) return;
  const showCount = 30;
  const startIdx = forceStartIdx !== undefined ? forceStartIdx : Math.max(0, rec.length - showCount);
  const displayRecords = rec.slice(startIdx);
  el.innerHTML = '';
  
  const fragment = document.createDocumentFragment();
  
  if (startIdx > 0) {
    const loadMore = document.createElement('div');
    loadMore.style.textAlign = 'center';
    loadMore.style.padding = '10px';
    loadMore.style.color = '#999';
    loadMore.style.fontSize = '12px';
    loadMore.style.cursor = 'pointer';
    loadMore.innerText = '↑ 点击加载更早消息';
    loadMore.onclick = () => loadMoreMessages(el, rec, startIdx);
    fragment.appendChild(loadMore);
  }

  displayRecords.forEach((m, idx) => {
    if (m.side==='notif' && m.type==='rp_notif') { const nd=document.createElement('div'); nd.innerHTML=m.content; fragment.appendChild(nd.firstElementChild || nd); return; }
    if (m.isHidden) return;
    let ava = chatSettings.chatUserAvatar || userAvatar;
    let sName = null;
    if (m.side === 'left') {
      if (c.isGroup && m.senderId) {
        const member = contacts.find(x => x.id === m.senderId);
        if (member) {
          ava = member.avatar;
          sName = member.name;
        } else {
          ava = c.avatar;
        }
      } else {
        ava = c.avatar;
        if (c.isGroup) sName = c.name; // fallback
      }
    }
    const div = createMsgElement(m.content, m.side, ava, m.quote, startIdx + idx, m.type, sName, m.statusData, m.isOfflineMsg);
    fragment.appendChild(div);
  });
  
  el.appendChild(fragment);

  function loadMoreMessages(el, rec, currentStartIdx) {
    const pageSize = 20;
    const endIdx = currentStartIdx;
    const startIdx = Math.max(0, endIdx - pageSize);
    const messagesToLoad = rec.slice(startIdx, endIdx);
    
    // 移除旧的加载更多按钮
    const oldLoadMore = el.querySelector('div[style*="cursor: pointer"]');
    if (oldLoadMore) oldLoadMore.remove();

    // 插入消息
    const fragment = document.createDocumentFragment();
      messagesToLoad.forEach((m, idx) => {
        if (m.isHidden) return;
        let ava = chatSettings.chatUserAvatar || userAvatar;
        let sName = null;
        const c = contacts.find(x => x.id === currentContactId);
        if (c && c.isGroup && m.senderId) {
          const member = contacts.find(x => x.id === m.senderId);
          if (member) {
            ava = member.avatar;
            sName = member.name;
          } else {
            ava = c.avatar;
          }
        } else if (c) {
          ava = m.side === 'left' ? c.avatar : (chatSettings.chatUserAvatar || userAvatar);
          if (c.isGroup) sName = c.name;
        }
        
        const div = createMsgElement(m.content, m.side, ava, m.quote, startIdx + idx, m.type, sName, m.statusData, m.isOfflineMsg);
      fragment.appendChild(div);
    });
    el.insertBefore(fragment, el.firstChild);
    
    // 应用隐藏头像设置
    if (chatSettings.hideAvatar) {
      fragment.querySelectorAll('.msg-avatar').forEach(item => {
        item.style.display = 'none';
      });
    }
    
    // 如果还有更多，添加新的按钮
    if (startIdx > 0) {
      const loadMore = document.createElement('div');
      loadMore.style.textAlign = 'center';
      loadMore.style.padding = '10px';
      loadMore.style.color = '#999';
      loadMore.style.fontSize = '12px';
      loadMore.style.cursor = 'pointer';
      loadMore.innerText = '↑ 点击加载更早消息';
      loadMore.onclick = () => loadMoreMessages(el, rec, startIdx);
      el.insertBefore(loadMore, el.firstChild);
    }
  }
  
  // 应用隐藏头像设置
  applyHideAvatarSetting();
  
  // 滚动到底部（延迟执行确保DOM渲染完成）
  setTimeout(() => {
    el.scrollTop = el.scrollHeight;
  }, 50);
}

// 应用隐藏头像设置 - 隐藏双方头像
function applyHideAvatarSetting() {
  const allAvatars = document.querySelectorAll('.msg-item .msg-avatar');
  if (chatSettings && chatSettings.hideAvatar) {
    allAvatars.forEach(item => {
      item.style.display = 'none';
    });
  } else {
    allAvatars.forEach(item => {
      item.style.display = 'block';
    });
  }
}

function parseTextBeautify(text) {
  if (!text) return '';
  // 1. 转义 HTML 实体，防止特殊字符破坏 DOM 结构导致渲染卡顿
  let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  
  // 2. 保护换行符
  html = html.replace(/\n/g, '<br>');
  
  // 3. 使用单引号包裹 class 属性，避免被后续的 "" 匹配到
  html = html.replace(/\{([^{}]+)\}/g, "<span class='text-brace'>{$1}</span>");
  
  // 4. 匹配 “” 和 "" 对话
  html = html.replace(/“([^“”]+)”/g, "<span class='text-quote'>“$1”</span>");
  html = html.replace(/"([^"]+)"/g, "<span class='text-quote'>\"$1\"</span>");
  
  // 将没有被 span 包裹的普通文本用 text-normal 包裹
  return `<span class='text-normal'>${html}</span>`;
}

function createMsgElement(content, side, avatar, quote, idx, type, senderName, statusData, isOfflineMsg) {
  if (idx === undefined) {
    const rec = chatRecords[currentContactId] || [];
    idx = rec.length;
  }

  const div = document.createElement('div');
  
  if (side === 'notif') {
    div.className = 'msg-item notif';
    div.style.cssText = 'display: flex; justify-content: center; width: 100%; margin: 10px 0;';
    const notifP = document.createElement('p');
    notifP.innerHTML = content;
    notifP.style.cssText = 'font-size: 12px; color: #999; text-align: center; margin: 0; background-color: rgba(0,0,0,0.05); padding: 4px 10px; border-radius: 4px;';
    div.appendChild(notifP);
    return div;
  }

  const isBlueOfflineCard = isCurrentChatBlueMinimalEnabled(isOfflineMsg, statusData) && side === 'left' && type !== 'red_packet' && type !== 'transfer';
  
  if (isBlueOfflineCard) {
    div.className = `msg-item ${side} blue-offline-mode`;
  } else {
    div.className = `msg-item ${side}`;
  }
  
  if (selectedMsgIndices.includes(idx)) div.classList.add('selected');
  const qhtml = quote ? `<div class="msg-quote">${quote}</div>` : '';

  const replyText = encodeURIComponent(type === 'image' ? '[图片]' : content);

  let ringClass = '';
  if (side === 'left' && currentContactId) {
    const c = contacts.find(x => x.id === currentContactId);
    if (c && c.isMarried && !c.isGroup) {
      ringClass = ' ring-avatar-frame';
    }
  }

  const bubble = document.createElement('div');
  bubble.dataset.msgIdx = idx;

  if (isBlueOfflineCard) {
    bubble.className = 'msg-blue-card';
    let parsedContent = type === 'image' ? `<img src="${content}" style="max-width:180px; max-height:180px; border-radius:10px; display:block; cursor:zoom-in; object-fit:cover;" onclick="event.stopPropagation(); viewFullImage('${content}')">` : parseTextBeautify(content);
    // AI表情包替换：蓝色卡片模式也需要处理
    if (type !== 'image' && typeof processAiEmojiInMessage === 'function') {
      parsedContent = processAiEmojiInMessage(parsedContent);
    }
    
    bubble.innerHTML = `
      <div class="blue-card-top">
        <div class="blue-card-avatar${ringClass}"><img src="${avatar}"></div>
          <div class="blue-card-status">
            <div class="bc-status-item thoughts"><div class="bc-label"><img src="ICON/心声.png" style="width:14px; height:14px; margin-right:2px; vertical-align:-0.15em; filter: opacity(0.7);"> 心声</div><div class="bc-val">${(statusData?.thoughts || '没有想法').substring(0,15)}</div></div>
            <div class="bc-status-item"><div class="bc-label"><img src="ICON/地点.png" style="width:14px; height:14px; margin-right:2px; vertical-align:-0.15em; filter: opacity(0.7);"> 地点</div><div class="bc-val">${statusData?.location || '未知'}</div></div>
            <div class="bc-status-item"><div class="bc-label"><img src="ICON/心情.png" style="width:14px; height:14px; margin-right:2px; vertical-align:-0.15em; filter: opacity(0.7);"> 心情</div><div class="bc-val">${(statusData?.mood || '平静').substring(0,15)}</div></div>
            <div class="bc-status-item favor"><div class="bc-label"><img src="ICON/好感阶段.png" style="width:14px; height:14px; margin-right:2px; vertical-align:-0.15em; filter: opacity(0.7);"> 好感度</div><div class="bc-val">${statusData?.favor || 0}%</div></div>
          </div>
      </div>
      ${statusData && statusData.physiological ? `
      <div class="blue-card-middle">
        <div class="bc-toggle" onclick="const c = this.nextElementSibling; c.style.display = c.style.display === 'none' ? 'block' : 'none';">
          <div style="display: flex; align-items: center; justify-content: center; gap: 6px;">
            <span>?? 情欲指数：</span>
            <div class="bc-lust-bar-bg" style="width: 80px; flex: none;"><div class="bc-lust-bar-fill" style="width:${statusData.lust || 0}%"></div></div>
            <span>${statusData.lust || 0}%</span>
          </div>
        </div>
        <div class="bc-hidden-content" style="display:none; text-align: center; padding-top: 4px;">
          <div class="bc-phys-row"><span>生理状态：</span><span>${statusData.physiological}</span></div>
        </div>
      </div>
      ` : ''}
      <div class="blue-card-bottom">
        ${qhtml}${parsedContent}
      </div>
    `;
    
    const bubbleWrapper = document.createElement('div');
    bubbleWrapper.style.cssText = 'display:flex; flex-direction:column; max-width:100%; width:100%;';
    if (senderName) {
      const nameEl = document.createElement('div');
      nameEl.style.cssText = 'font-size:11px; color:var(--text-light); margin-bottom:4px; margin-left:4px;';
      nameEl.innerText = senderName;
      bubbleWrapper.appendChild(nameEl);
    }
    bubbleWrapper.appendChild(bubble);

    // 如果有多个roll版本，在气泡正下方追加切换控件（线下蓝卡模式）
    // 只在该回合最后一条气泡下显示计数器
    {
      const recNow2 = chatRecords[currentContactId] || [];
      // 找到该回合第一条消息（持有 alternatives）
      let firstAltIdx2 = idx;
      let msgDataNow2 = recNow2[idx];
      // 如果当前消息没有 alternatives，向前查找持有 alternatives 的首条消息
      if ((!msgDataNow2 || !msgDataNow2.alternatives) && side === 'left') {
        for (let si = idx - 1; si >= 0; si--) {
          if (recNow2[si] && recNow2[si].side === 'left' && recNow2[si].senderId === (recNow2[idx] && recNow2[idx].senderId)) {
            if (recNow2[si].alternatives) { firstAltIdx2 = si; msgDataNow2 = recNow2[si]; break; }
          } else { break; }
        }
      }
      if (msgDataNow2 && msgDataNow2.alternatives && msgDataNow2.alternatives.length > 1 && side === 'left') {
        // 找该回合最后一条气泡的 idx
        const firstSenderId2 = recNow2[firstAltIdx2] && recNow2[firstAltIdx2].senderId;
        let lastAltIdx2 = firstAltIdx2;
        for (let li = firstAltIdx2 + 1; li < recNow2.length; li++) {
          if (recNow2[li] && recNow2[li].side === 'left' && recNow2[li].senderId === firstSenderId2 && !recNow2[li].alternatives) {
            lastAltIdx2 = li;
          } else { break; }
        }
        // 只在最后一条气泡上渲染计数器
        if (idx === lastAltIdx2) {
          const altCount2 = msgDataNow2.alternatives.length;
          const altCur2 = (msgDataNow2.currentIndex !== undefined ? msgDataNow2.currentIndex : altCount2 - 1) + 1;
          const switcherDiv2 = document.createElement('div');
          switcherDiv2.style.cssText = 'display:flex; align-items:center; justify-content:flex-start; gap:0; margin-top:2px; margin-left:4px; padding:0; user-select:none;';
          const prevBtn2 = document.createElement('span');
          prevBtn2.textContent = '<';
          prevBtn2.style.cssText = 'font-size:12px; color:var(--text-light); cursor:pointer; padding:0 4px;';
          prevBtn2.onclick = (e) => { e.stopPropagation(); switchMsgAlternative(firstAltIdx2, 'prev'); };
          const indexSpan2 = document.createElement('span');
          indexSpan2.textContent = altCur2 + '/' + altCount2;
          indexSpan2.style.cssText = 'font-size:12px; color:var(--text-light);';
          const nextBtn2 = document.createElement('span');
          nextBtn2.textContent = '>';
          nextBtn2.style.cssText = 'font-size:12px; color:var(--text-light); cursor:pointer; padding:0 4px;';
          nextBtn2.onclick = (e) => { e.stopPropagation(); switchMsgAlternative(firstAltIdx2, 'next'); };
          switcherDiv2.appendChild(prevBtn2);
          switcherDiv2.appendChild(indexSpan2);
          switcherDiv2.appendChild(nextBtn2);
          bubbleWrapper.appendChild(switcherDiv2);
        }
      }
    }

    div.innerHTML = `
      <div class="check-icon">?</div>
    `;
    div.appendChild(bubbleWrapper);
    
  } else {
      bubble.className = 'msg-bubble';
      if (type === 'image') {
        bubble.style.cssText = 'padding:4px; background:transparent !important; border:none !important; box-shadow:none !important;';
        if (qhtml) bubble.innerHTML = qhtml;
        const imgEl = document.createElement('img');
        imgEl.src = content;
        imgEl.style.cssText = 'max-width:180px; max-height:180px; border-radius:10px; display:block; cursor:zoom-in; object-fit:cover;';
        imgEl.onclick = (e) => { e.stopPropagation(); viewFullImage(content); };
        bubble.appendChild(imgEl);
      } else if (type === 'red_packet' || type === 'transfer') {
        bubble.style.cssText = 'padding: 0; background: transparent !important; border: none !important; box-shadow: none !important; margin-bottom: 5px; cursor: pointer;';
        if (qhtml) bubble.innerHTML = qhtml;
        
        let data = {};
        try { data = JSON.parse(content); } catch
