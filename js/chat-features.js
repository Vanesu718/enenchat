// js/chat-features.js - Emoji and other features

// ----- Emoji System Management -----
window.chatFeatures = window.chatFeatures || {};

// 统一存储辅助函数
// 同步读取：优先从 storageSync（内存同步层）读取，保证即时可用
function _cfGet(key) {
    try {
        const raw = window.storageSync ? window.storageSync.getItem(key) : localStorage.getItem(key);
        if (raw === null || raw === undefined) return null;
        return JSON.parse(raw);
    } catch(e) {
        return null;
    }
}

// 异步读取：从 IndexedDB 读取（用于同步层读不到数据时的回退）
async function _cfGetAsync(key) {
    // 先尝试同步读
    const syncResult = _cfGet(key);
    if (syncResult !== null) return syncResult;
    // 同步层没有，从 IndexedDB 异步读取
    try {
        if (window.storage && typeof window.storage.getItem === 'function') {
            const raw = await window.storage.getItem(key);
            if (raw !== null && raw !== undefined) {
                const parsed = JSON.parse(raw);
                // 回写到同步层缓存
                if (window.storageSync) {
                    window.storageSync.cache[key] = raw;
                }
                return parsed;
            }
        }
    } catch(e) {
        console.error('_cfGetAsync failed for key:', key, e);
    }
    return null;
}

// 写入：同时写 storageSync（同步即时读）+ IndexedDB（异步持久化）
function _cfSet(key, value) {
    try {
        const raw = JSON.stringify(value);
        // 1. 同步写入 storageSync，保证下次 _cfGet 能立即读到
        if (window.storageSync) {
            window.storageSync.setItem(key, raw);
        } else {
            localStorage.setItem(key, raw);
        }
        // 2. 异步写入 IndexedDB，保证刷新后数据不丢失
        if (typeof window.saveToStorage === 'function') {
            window.saveToStorage(key, raw);
        } else if (window.storage && typeof window.storage.setItem === 'function') {
            window.storage.setItem(key, raw).catch(function(e) {
                console.error('_cfSet IndexedDB write failed:', e);
            });
        }
    } catch(e) {
        console.error('_cfSet failed:', e);
    }
}

// Initialize default emojis if not present
// 异步版本：先从 IndexedDB 读取持久化数据，只有真正为空时才写入默认值
// 同时预加载 settings 到 storageSync.cache，确保后续同步读取可用
async function initEmojis() {
    // 确保 storage (IndexedDB) 已经初始化完毕
    if (window.storage && typeof window.storage.init === 'function') {
        try { await window.storage.init(); } catch(e) { console.warn('[initEmojis] storage.init failed:', e); }
    }

    // === 预加载 settings ===
    let settings = _cfGet('settings');
    if (!settings) {
        settings = await _cfGetAsync('settings');
    }

    // === 预加载 emojis - 强制先从 IndexedDB 异步读取 ===
    let emojis = null;
    
    // 1. 优先从 IndexedDB 异步读取（最可靠的持久化源）
    try {
        if (window.storage && typeof window.storage.getItem === 'function') {
            const raw = await window.storage.getItem('emojis');
            if (raw !== null && raw !== undefined) {
                emojis = typeof raw === 'string' ? JSON.parse(raw) : raw;
                // 回写到同步缓存，确保后续 _cfGet 能读到
                if (window.storageSync && emojis) {
                    window.storageSync.cache['emojis'] = JSON.stringify(emojis);
                }
            }
        }
    } catch(e) {
        console.warn('[initEmojis] IndexedDB 读取 emojis 失败:', e);
    }
    
    // 2. 如果 IndexedDB 没有，再尝试同步缓存
    if (!emojis || Object.keys(emojis).length === 0) {
        emojis = _cfGet('emojis');
    }

    // 只有在所有存储都没有数据时，才写入默认值
    if (!emojis || Object.keys(emojis).length === 0) {
        emojis = {
            "\u7cfb\u7edf": [
                { name: "\u9ed8\u8ba4", url: "haibaologo.png" }
            ]
        };
        _cfSet('emojis', emojis);
    } else {
        // 确保同步缓存中有数据（关键：防止后续 _cfGet 读不到）
        if (window.storageSync) {
            window.storageSync.cache['emojis'] = JSON.stringify(emojis);
        }
    }

    // 同时确保 settings 也写入同步缓存
    if (settings && window.storageSync) {
        window.storageSync.cache['settings'] = JSON.stringify(settings);
    }

    console.log('[initEmojis] 完成，表情组数:', Object.keys(emojis).length, 
        '表情组名:', Object.keys(emojis).join(', '),
        'AI Emoji开关:', settings ? settings.enableAiEmoji : 'N/A');
}

// Edit Emoji Group - 点击修改按钮时，将该组数据回填到新增页面
window.editEmojiGroup = function(groupName) {
    const emojis = _cfGet('emojis') || {};
    const groupData = emojis[groupName] || [];
    if (groupData.length === 0) return;

    let textStr = '';
    groupData.forEach(function(item) {
        textStr += item.name + '\uff1a' + item.url + '\n';
    });
    
    document.getElementById('emojiGroupName').value = groupName;
    document.getElementById('emojiBatchInput').value = textStr;
    openSub('add-emoji-page');
}

// Render Emoji Management Page List
window.renderEmojiList = function() {
    const emojis = _cfGet('emojis') || {};
    const container = document.getElementById('emojiListContainer');
    if (!container) return;
    container.innerHTML = '';

    if (Object.keys(emojis).length === 0) {
        container.innerHTML = '<div class="empty-tip">\u6682\u65e0\u8868\u60c5\u5305<br>\u70b9\u51fb\u53f3\u4e0a\u89d2\u65b0\u589e</div>';
        return;
    }

    for (const group in emojis) {
        const groupData = emojis[group] || [];

        let html = '<div class="emoji-group-card">' +
            '<div class="emoji-group-header">' +
                '<div class="emoji-group-title">' + group + ' <span style="font-size:12px;color:#999;font-weight:normal;">(' + groupData.length + '\u5f20)</span></div>' +
                '<div style="display:flex;gap:10px;">' +
                    '<div class="emoji-group-delete" style="color:var(--main-pink);" onclick="editEmojiGroup(\'' + group + '\')">\u4fee\u6539</div>' +
                    '<div class="emoji-group-delete" onclick="deleteEmojiGroup(\'' + group + '\')">\u5220\u9664</div>' +
                '</div>' +
            '</div>' +
            '<div class="emoji-grid-preview">';

        // 只取前10张进行预览
        var previewData = groupData.slice(0, 10);
        previewData.forEach(function(item) {
            html += '<div class="emoji-preview-item" style="background-image:url(\'' + item.url + '\')" title="' + item.name + '"></div>';
        });

        if (groupData.length > 10) {
            html += '<div class="emoji-preview-item" style="display:flex;align-items:center;justify-content:center;background:#f5f5f5;color:#999;font-size:12px;border-radius:4px;">+' + (groupData.length - 10) + '</div>';
        }

        html += '</div></div>';
        container.innerHTML += html;
    }
}

// Delete Emoji Group
window.deleteEmojiGroup = function(groupName) {
    if (confirm('\u786e\u8ba4\u8981\u5220\u9664\u8868\u60c5\u7ec4 [' + groupName + '] \u5417\uff1f')) {
        let emojis = _cfGet('emojis') || {};
        delete emojis[groupName];
        _cfSet('emojis', emojis);
        renderEmojiList();
        showToast('\u5220\u9664\u6210\u529f');
    }
}

// Save Emoji Batch (新增 & 编辑共用，覆盖模式)
window.saveEmojiBatch = function() {
    const groupName = document.getElementById('emojiGroupName').value.trim();
    const batchInput = document.getElementById('emojiBatchInput').value.trim();

    if (!groupName) {
        showToast('\u8bf7\u586b\u5199\u8868\u60c5\u7ec4\u540d\u79f0');
        return;
    }

    if (!batchInput) {
        showToast('\u8bf7\u586b\u5199\u8868\u60c5\u5185\u5bb9');
        return;
    }

    const lines = batchInput.split('\n');
    const newEmojis = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        // Match format: Name:URL or Name：URL (supports both colon formats)
        const match = line.match(/^(.+?)[:：](.+)$/);
        if (match) {
            const name = match[1].trim();
            const url = match[2].trim();
            if (name && url) {
                newEmojis.push({ name: name, url: url });
            }
        }
    }

    if (newEmojis.length === 0) {
        showToast('\u672a\u89e3\u6790\u5230\u4efb\u4f55\u6709\u6548\u8868\u60c5\uff0c\u8bf7\u68c0\u67e5\u683c\u5f0f');
        return;
    }

    if (newEmojis.length > 100) {
        showToast('\u5355\u4e2a\u5206\u7ec4\u6700\u591a\u652f\u6301100\u4e2a\u8868\u60c5');
        return;
    }

    let emojis = _cfGet('emojis') || {};
    // 覆盖模式：编辑时用户在文本框里删掉某一行，保存后也就真正删掉了
    emojis[groupName] = newEmojis;

    _cfSet('emojis', emojis);

    document.getElementById('emojiGroupName').value = '';
    document.getElementById('emojiBatchInput').value = '';

    closeSub('add-emoji-page');
    renderEmojiList();
    showToast('\u5df2\u4fdd\u5b58 [' + groupName + ']\uff0c\u5171 ' + newEmojis.length + ' \u4e2a\u8868\u60c5');
}

// Render Emoji Picker in Chat
window.renderEmojiPicker = function() {
    const emojis = _cfGet('emojis') || {};
    const tabsContainer = document.getElementById('emojiGroupTabs');
    const itemsContainer = document.getElementById('emojiPickerItems');

    if (!tabsContainer || !itemsContainer) return;

    tabsContainer.innerHTML = '';
    itemsContainer.innerHTML = '';

    const groups = Object.keys(emojis);
    if (groups.length === 0) {
        itemsContainer.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:#999; margin-top:20px; font-size:14px;">\u6682\u65e0\u8868\u60c5\u5305<br>\u8bf7\u5148\u5728\u53d1\u73b0\u9875\u6dfb\u52a0</div>';
        return;
    }

    // Create tabs
    groups.forEach(function(group, index) {
        const tab = document.createElement('div');
        tab.className = 'emoji-tab-item' + (index === 0 ? ' active' : '');
        tab.innerText = group;
        tab.onclick = function() {
            document.querySelectorAll('.emoji-tab-item').forEach(function(t) { t.classList.remove('active'); });
            this.classList.add('active');
            renderEmojiPickerItems(group);
        };
        tabsContainer.appendChild(tab);
    });

    // Render first group items
    if (groups.length > 0) {
        renderEmojiPickerItems(groups[0]);
    }
}

// Render specific group items in picker
window.renderEmojiPickerItems = function(groupName) {
    const emojis = _cfGet('emojis') || {};
    const itemsContainer = document.getElementById('emojiPickerItems');
    if (!itemsContainer) return;
    itemsContainer.innerHTML = '';

    const groupData = emojis[groupName] || [];
    if (groupData.length === 0) {
        itemsContainer.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:#999; margin-top:20px; font-size:14px;">\u8be5\u5206\u7ec4\u6682\u65e0\u8868\u60c5</div>';
        return;
    }
    groupData.forEach(function(item) {
        const img = document.createElement('div');
        img.className = 'emoji-picker-img';
        img.style.backgroundImage = "url('" + item.url + "')";
        img.title = item.name;
        img.onclick = function() { sendEmoji(item.url); };
        itemsContainer.appendChild(img);
    });
}

// Send Emoji Message
window.sendEmoji = function(url) {
    if (typeof isOfflineMode !== 'undefined' && isOfflineMode) {
        if (typeof showToast === 'function') showToast('表情功能仅限线上聊天使用');
        return;
    }
    const contactId = typeof currentContactId !== 'undefined' ? currentContactId : (window.currentContactId || null);
    if (!contactId) return;

    // Add user message
    const msg = {
        id: Date.now().toString(),
        content: url,
        img: url,
        isEmoji: true,
        side: 'right',
        type: 'image',
        time: (typeof formatTime === 'function' ? formatTime(new Date()) : new Date().toLocaleTimeString())
    };

    // 1. UI display
    if (typeof addMsgToUI === 'function') {
        const uAvatar = (typeof chatSettings !== 'undefined' && chatSettings.chatUserAvatar) ? chatSettings.chatUserAvatar : (typeof window.userAvatar !== 'undefined' ? window.userAvatar : '');
        addMsgToUI(msg.content, 'right', uAvatar, null, undefined, 'image');
    }

    // 2. Memory records
    const records = typeof chatRecords !== 'undefined' ? chatRecords : (window.chatRecords || null);
    if (records) {
        if (!records[contactId]) records[contactId] = [];
        records[contactId].push(msg);
        
        if (typeof debouncedSave === 'function') {
            debouncedSave('CHAT_' + contactId, JSON.stringify(records[contactId]));
        } else if (typeof saveToStorage === 'function') {
            saveToStorage('CHAT_' + contactId, JSON.stringify(records[contactId]));
        }
    }

    // 3. IndexedDB Persistence
    if (typeof saveChatMessage === 'function') {
        saveChatMessage(contactId, msg);
    } else if (typeof window.saveChatMessage === 'function') {
        window.saveChatMessage(contactId, msg);
    }

    // Hide emoji panel
    const panel = document.getElementById('emojiPickerPanel');
    if (panel) {
        panel.style.transform = 'translateY(100%)';
        setTimeout(function() { panel.style.display = 'none'; }, 300);
    }

    // Trigger AI Reply if in online mode
    if (typeof isOfflineMode !== 'undefined' && !isOfflineMode) {
        setTimeout(function() {
            if (typeof triggerAIReply === 'function') {
                triggerAIReply();
            } else if (typeof window.triggerAIReply === 'function') {
                window.triggerAIReply();
            }
        }, 500);
    }
}

// Override selectFile to handle emoji type specifically
;(function() {
    const originalSelectFile = window.selectFile;
window.selectFile = function(type, event) {
        if (type === 'emoji') {
            if (typeof isOfflineMode !== 'undefined' && isOfflineMode) {
                if (typeof showToast === 'function') showToast('表情功能仅限线上聊天使用');
                return;
            }
            if (event) {
                event.stopPropagation();
            }
            
            const panel = document.getElementById('emojiPickerPanel');
            const attachPanel = document.getElementById('attachPanel');

            if (attachPanel && (attachPanel.style.display === 'block' || attachPanel.classList.contains('show'))) {
                attachPanel.style.display = 'none';
                attachPanel.classList.remove('show');
            }

            if (!panel) return;

            if (panel.style.display === 'none' || panel.style.display === '') {
                renderEmojiPicker();
                panel.style.display = 'flex';
                setTimeout(function() { panel.style.transform = 'translateY(0)'; }, 10);
            } else {
                panel.style.transform = 'translateY(100%)';
                setTimeout(function() { panel.style.display = 'none'; }, 300);
            }
        } else {
            if (originalSelectFile) {
                originalSelectFile(type);
            }
        }
    };
})();

// AI Emoji Toggle
window.toggleAiEmoji = function() {
    let settings = _cfGet('settings') || {};
    settings.enableAiEmoji = !settings.enableAiEmoji;
    _cfSet('settings', settings);
    updateAiEmojiUI();
    showToast(settings.enableAiEmoji ? 'AI Emoji \u5df2\u5f00\u542f' : 'AI Emoji \u5df2\u5173\u95ed');
}

window.updateAiEmojiUI = function() {
    let settings = _cfGet('settings') || {};
    const toggle = document.getElementById('ai-emoji-toggle');
    if (toggle) {
        if (settings.enableAiEmoji) {
            toggle.classList.add('active');
        } else {
            toggle.classList.remove('active');
        }
    }
}

// Helper to get emoji list for AI Prompt (异步版本，确保能从 IndexedDB 读到数据)
window.getAiEmojiPromptAddon = async function() {
    if (typeof isOfflineMode !== 'undefined' && isOfflineMode) {
        return '';
    }
    let settings = _cfGet('settings');
    if (!settings) settings = await _cfGetAsync('settings');
    if (!settings || !settings.enableAiEmoji) return '';

    let emojis = _cfGet('emojis');
    if (!emojis || Object.keys(emojis).length === 0) {
        emojis = await _cfGetAsync('emojis');
    }
    if (!emojis) return '';

    let hasEmojis = false;
    let emojiLines = '';
    for (const group in emojis) {
        const groupData = emojis[group] || [];
        if (groupData.length > 0) {
            hasEmojis = true;
            emojiLines += '- ' + group + ': ';
            emojiLines += groupData.map(function(e) { return '[' + e.name + ']'; }).join(', ') + '\n';
        }
    }

    if (!hasEmojis) return '';

    return '\n\n【表情系统】\n你现在可以发送表情图片。可用的表情包如下：\n' +
        emojiLines +
        '发送表情的方式：在回复的合适位置直接插入 [表情名称] 格式的文字（注意：必须严格使用上面列出的表情名称，一字不差，不要自己编造或添加后缀）。系统会自动渲染为图片。\n' +
        '规则：每次回复最多使用1-2个表情，不要滥用。只能使用上方列表中提供的[表情名称]，禁止自己编造表情名称。';
}

// Helper: 将AI回复中的 [表情名称] 替换为实际图片
window.processAiEmojiInMessage = function(text) {
    if (!text) return text;
    if (typeof isOfflineMode !== 'undefined' && isOfflineMode) return text;
    let settings = _cfGet('settings') || {};
    if (!settings.enableAiEmoji) return text;

    const emojis = _cfGet('emojis') || {};
    // 构建名称到URL的映射
    const nameToUrl = {};
    for (const group in emojis) {
        const groupData = emojis[group] || [];
        groupData.forEach(function(item) {
            nameToUrl[item.name] = item.url;
        });
    }

    // 替换 [表情名称] 为 <img> 标签
    return text.replace(/\[([^\]]+)\]/g, function(match, name) {
        if (nameToUrl[name]) {
            return '<img src="' + nameToUrl[name] + '" class="emoji-msg-img" alt="' + name + '" title="' + name + '" style="max-width:120px;max-height:120px;border-radius:8px;vertical-align:middle;">';
        }
        return match; // 不是表情名称，原样返回
    });
}

// Initialization hooks
document.addEventListener('DOMContentLoaded', function() {
    initEmojis();

    // Close emoji panel when clicking outside
    document.addEventListener('click', function(e) {
        const panel = document.getElementById('emojiPickerPanel');
        if (panel && panel.style.display === 'flex') {
            if (!panel.contains(e.target) && !e.target.closest('.attach-item') && !e.target.closest('.attach-panel') && !e.target.closest('.chat-func-btn')) {
                panel.style.transform = 'translateY(100%)';
                setTimeout(function() { panel.style.display = 'none'; }, 300);
            }
        }
    });

    // Hook into openSub to initialize emoji pages when opened
    const originalOpenSub = window.openSub;
    window.openSub = function(id) {
        if (id === 'emoji-setting-page') {
            updateAiEmojiUI();
            renderEmojiList();
        }
        if (originalOpenSub) originalOpenSub(id);
    };
});
