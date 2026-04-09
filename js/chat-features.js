// js/chat-features.js - Emoji and other features

// ----- Emoji System Management -----
window.chatFeatures = window.chatFeatures || {};

// 统一存储辅助函数（使用 storageSync，与 main.js 保持一致）
function _cfGet(key) {
    try {
        const raw = window.storageSync ? window.storageSync.getItem(key) : localStorage.getItem(key);
        if (raw === null || raw === undefined) return null;
        return JSON.parse(raw);
    } catch(e) {
        return null;
    }
}

function _cfSet(key, value) {
    try {
        const raw = JSON.stringify(value);
        if (window.storageSync) {
            window.storageSync.setItem(key, raw);
        } else {
            localStorage.setItem(key, raw);
        }
    } catch(e) {
        console.error('_cfSet failed:', e);
    }
}

// Initialize default emojis if not present
function initEmojis() {
    let emojis = _cfGet('emojis') || {};
    // Add default system emojis if empty
    if (Object.keys(emojis).length === 0) {
        emojis = {
            "系统": [
                { name: "默认", url: "haibaologo.png" }
            ]
        };
        _cfSet('emojis', emojis);
    }
}

// Render Emoji Management Page List
window.renderEmojiList = function() {
    const emojis = _cfGet('emojis') || {};
    const container = document.getElementById('emojiListContainer');
    if (!container) return;
    container.innerHTML = '';

    if (Object.keys(emojis).length === 0) {
        container.innerHTML = '<div class="empty-tip">暂无表情包<br>点击右上角新增</div>';
        return;
    }

    for (const group in emojis) {
        const groupData = emojis[group] || [];

        let html = '<div class="emoji-group-card">' +
            '<div class="emoji-group-header">' +
                '<div class="emoji-group-title">' + group + ' <span style="font-size:12px;color:#999;font-weight:normal;">(' + groupData.length + '张)</span></div>' +
                '<div class="emoji-group-delete" onclick="deleteEmojiGroup(\'' + group + '\')">删除分组</div>' +
            '</div>' +
            '<div class="emoji-grid-preview">';

        groupData.forEach(item => {
            html += '<div class="emoji-preview-item" style="background-image:url(\'' + item.url + '\')" title="' + item.name + '"></div>';
        });

        html += '</div></div>';
        container.innerHTML += html;
    }
}

// Delete Emoji Group
window.deleteEmojiGroup = function(groupName) {
    if (confirm('确认要删除表情组 [' + groupName + '] 吗？')) {
        let emojis = _cfGet('emojis') || {};
        delete emojis[groupName];
        _cfSet('emojis', emojis);
        renderEmojiList();
        showToast('删除成功');
    }
}

// Save Emoji Batch
window.saveEmojiBatch = function() {
    const groupName = document.getElementById('emojiGroupName').value.trim();
    const batchInput = document.getElementById('emojiBatchInput').value.trim();

    if (!groupName) {
        showToast('请填写表情组名称');
        return;
    }

    if (!batchInput) {
        showToast('请填写表情内容');
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
                newEmojis.push({ name, url });
            }
        }
    }

    if (newEmojis.length === 0) {
        showToast('未解析到任何有效表情，请检查格式');
        return;
    }

    if (newEmojis.length > 50) {
        showToast('一次最多只能添加50个表情');
        return;
    }

    let emojis = _cfGet('emojis') || {};
    if (!emojis[groupName]) {
        emojis[groupName] = [];
    }

    // Check for duplicates in the same group based on URL or name
    let addedCount = 0;
    newEmojis.forEach(newItem => {
        const exists = emojis[groupName].some(item => item.url === newItem.url || item.name === newItem.name);
        if (!exists) {
            emojis[groupName].push(newItem);
            addedCount++;
        }
    });

    _cfSet('emojis', emojis);

    document.getElementById('emojiGroupName').value = '';
    document.getElementById('emojiBatchInput').value = '';

    closeSub('add-emoji-page');
    renderEmojiList();
    showToast('成功添加 ' + addedCount + ' 个表情到 [' + groupName + ']');
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
        itemsContainer.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:#999; margin-top:20px; font-size:14px;">暂无表情包<br>请先在发现页添加</div>';
        return;
    }

    // Create tabs
    groups.forEach((group, index) => {
        const tab = document.createElement('div');
        tab.className = 'emoji-tab-item' + (index === 0 ? ' active' : '');
        tab.innerText = group;
        tab.onclick = function() {
            document.querySelectorAll('.emoji-tab-item').forEach(t => t.classList.remove('active'));
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
        itemsContainer.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:#999; margin-top:20px; font-size:14px;">该分组暂无表情</div>';
        return;
    }
    groupData.forEach(item => {
        const img = document.createElement('div');
        img.className = 'emoji-picker-img';
        img.style.backgroundImage = "url('" + item.url + "')";
        img.title = item.name;
        img.onclick = () => sendEmoji(item.url);
        itemsContainer.appendChild(img);
    });
}

// Send Emoji Message
window.sendEmoji = function(url) {
    const contactId = typeof currentContactId !== 'undefined' ? currentContactId : (window.currentContactId || null);
    if (!contactId) return;

    // Add user message
    const msg = {
        id: Date.now().toString(),
        content: url, // image url as content for addMsgToUI
        img: url,
        isEmoji: true,
        side: 'right', // using side instead of type to match main logic
        type: 'image', // Must be 'image' so createMsgElement renders an <img> tag instead of raw text
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
        setTimeout(() => { panel.style.display = 'none'; }, 300);
    }

    // Trigger AI Reply if in online mode
    if (typeof isOnlineMode !== 'undefined' && isOnlineMode) {
        setTimeout(() => {
            if (typeof callAIAPI === 'function') callAIAPI();
        }, 500);
    }
}

// Override selectFile to handle emoji type specifically
;(function() {
    const originalSelectFile = window.selectFile;
    window.selectFile = function(type, event) {
        if (type === 'emoji') {
            // 阻止事件冒泡，防止触发 document.click 导致立即关闭
            if (event) {
                event.stopPropagation();
            }
            
            const panel = document.getElementById('emojiPickerPanel');
            const attachPanel = document.getElementById('attachPanel');

            // Hide attach panel
            if (attachPanel && (attachPanel.style.display === 'block' || attachPanel.classList.contains('show'))) {
                attachPanel.style.display = 'none';
                attachPanel.classList.remove('show');
            }

            if (!panel) return;

            // Toggle emoji panel
            if (panel.style.display === 'none' || panel.style.display === '') {
                renderEmojiPicker();
                panel.style.display = 'flex';
                setTimeout(() => { panel.style.transform = 'translateY(0)'; }, 10);
            } else {
                panel.style.transform = 'translateY(100%)';
                setTimeout(() => { panel.style.display = 'none'; }, 300);
            }
        } else {
            // Original logic for other attach types
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
    showToast(settings.enableAiEmoji ? 'AI Emoji 已开启' : 'AI Emoji 已关闭');
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

// Helper to get emoji list for AI Prompt
window.getAiEmojiPromptAddon = function() {
    let settings = _cfGet('settings') || {};
    if (!settings.enableAiEmoji) return '';

    const emojis = _cfGet('emojis') || {};

    let hasEmojis = false;
    let emojiLines = '';
    for (const group in emojis) {
        const groupData = emojis[group] || [];
        if (groupData.length > 0) {
            hasEmojis = true;
            emojiLines += '- ' + group + ': ';
            emojiLines += groupData.map(e => '[' + e.name + ']').join(', ') + '\n';
        }
    }

    if (!hasEmojis) return '';

    return '\n\n【表情系统】\n你现在可以发送表情图片，请在合适时机使用以下表情包中的表情：\n' +
        emojiLines +
        '如果要发送表情，在回复的合适位置直接插入格式为 [表情名称] 的文字，系统会自动渲染为图片。注意：每次回复最多使用1-2个表情，不要滥用。只能使用上方列表中提供的[表情名称]。';
}

// Initialization hooks
document.addEventListener('DOMContentLoaded', function() {
    initEmojis();

    // Close emoji panel when clicking outside
    document.addEventListener('click', function(e) {
        const panel = document.getElementById('emojiPickerPanel');
        if (panel && panel.style.display === 'flex') {
            // 注意这里排除了 chat-func-btn 中的表情按钮，防止再次点击时冲突
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
