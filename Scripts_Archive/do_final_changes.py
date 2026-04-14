import sys

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. chatSettings default
search1 = """let chatSettings = {
    hideAvatar: false,
    chatBg: '',
    chatUserAvatar: '',
    chatNickname: '',
    sceneSetting: '',
    userMask: '',
    contactMask: '',
    useWorldBook: true
};"""

replace1 = """let chatSettings = {
    hideAvatar: false,
    chatBg: '',
    chatUserAvatar: '',
    chatNickname: '',
    sceneSetting: '',
    userMask: '',
    contactMask: '',
    useWorldBook: true,
    selectedWritingStyle: '',
    compressedWritingStyle: ''
};"""

content = content.replace(search1, replace1)

search2 = """    chatSettings = {
      hideAvatar: false,
      chatBg: '',
      chatUserAvatar: '',
      chatNickname: '',
      sceneSetting: '',
      userMask: '',
      contactMask: '',
      useWorldBook: true,
      selectedWorldBooks: []
    };"""

replace2 = """    chatSettings = {
      hideAvatar: false,
      chatBg: '',
      chatUserAvatar: '',
      chatNickname: '',
      sceneSetting: '',
      userMask: '',
      contactMask: '',
      useWorldBook: true,
      selectedWorldBooks: [],
      selectedWritingStyle: '',
      compressedWritingStyle: ''
    };"""

content = content.replace(search2, replace2)

# 2. append to initChatSettingsPage
searchInitChat = """  // 联系人设定：优先使用已保存的设定，若为空则回退到创建联系人时输入的人设
  const currentContact = contacts.find(c => c.id === currentContactId);
  document.getElementById('contactMaskTextarea').value = chatSettings.contactMask || (currentContact ? currentContact.persona : '') || '';
  
  // 加载联系人头像和名字"""

replaceInitChat = """  // 联系人设定：优先使用已保存的设定，若为空则回退到创建联系人时输入的人设
  const currentContact = contacts.find(c => c.id === currentContactId);
  document.getElementById('contactMaskTextarea').value = chatSettings.contactMask || (currentContact ? currentContact.persona : '') || '';

  // 填充文风下拉菜单
  const styleSelect = document.getElementById('chatWritingStyleSelect');
  if (styleSelect) {
    styleSelect.innerHTML = '<option value="">--不使用文风--</option>';
    writingStyleEntries.forEach(style => {
      const opt = document.createElement('option');
      opt.value = style.id;
      opt.textContent = style.name;
      if (chatSettings.selectedWritingStyle === style.id) {
        opt.selected = true;
      }
      styleSelect.appendChild(opt);
    });
  }
  
  // 加载联系人头像和名字"""
  
content = content.replace(searchInitChat, replaceInitChat)

# 3. append to initGroupChatSettingsPage
searchInitGroup = """  // 场景设定和用户人设
  const maskTextarea = document.getElementById('groupUserMaskTextarea');
  if (maskTextarea) {
    maskTextarea.value = chatSettings.userMask || '';
  }
  const sceneTextarea = document.getElementById('groupSceneSettingTextarea');
  if (sceneTextarea) {
    sceneTextarea.value = chatSettings.sceneSetting || '';
  }

  // 关联世界书列表"""

replaceInitGroup = """  // 场景设定和用户人设
  const maskTextarea = document.getElementById('groupUserMaskTextarea');
  if (maskTextarea) {
    maskTextarea.value = chatSettings.userMask || '';
  }
  const sceneTextarea = document.getElementById('groupSceneSettingTextarea');
  if (sceneTextarea) {
    sceneTextarea.value = chatSettings.sceneSetting || '';
  }

  // 填充文风下拉菜单
  const groupStyleSelect = document.getElementById('groupChatWritingStyleSelect');
  if (groupStyleSelect) {
    groupStyleSelect.innerHTML = '<option value="">--不使用文风--</option>';
    writingStyleEntries.forEach(style => {
      const opt = document.createElement('option');
      opt.value = style.id;
      opt.textContent = style.name;
      if (chatSettings.selectedWritingStyle === style.id) {
        opt.selected = true;
      }
      groupStyleSelect.appendChild(opt);
    });
  }

  // 关联世界书列表"""
  
content = content.replace(searchInitGroup, replaceInitGroup)

# 4. handleWritingStyleChange function
searchFunc = """// 预览聊天背景文件
function previewChatBgFile(input) {"""

replaceFunc = """// 处理文风切换
window.handleWritingStyleChange = async function(styleId) {
  if (!currentContactId) return;
  
  if (styleId === '') {
    chatSettings.selectedWritingStyle = '';
    chatSettings.compressedWritingStyle = '';
    await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(chatSettings));
    showToast('已取消文风设置');
    return;
  }
  
  const styleEntry = writingStyleEntries.find(s => s.id === styleId);
  if (!styleEntry) return;
  
  chatSettings.selectedWritingStyle = styleId;
  
  // 显示压缩中提示
  const styleSelect1 = document.getElementById('chatWritingStyleSelect');
  const styleSelect2 = document.getElementById('groupChatWritingStyleSelect');
  const styleSelect = styleSelect1 || styleSelect2;
  
  if (styleSelect && styleSelect.options[styleSelect.selectedIndex]) {
    styleSelect.options[styleSelect.selectedIndex].text = '压缩处理中...';
  }
  
  try {
    const cfgStr = await getFromStorage('AI_CHAT_CONFIG');
    const cfg = cfgStr ? (typeof cfgStr === 'string' ? JSON.parse(cfgStr) : cfgStr) : {};
    if (!cfg.key || !cfg.url || !cfg.model) {
      showToast('请先配置API，否则无法压缩文风');
      chatSettings.compressedWritingStyle = styleEntry.content.substring(0, 100);
      await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(chatSettings));
      return;
    }

    const systemPrompt = "请将以下长篇文风指南压缩成一句约50字的核心行为准则，直接返回结果，不要有任何多余的话语。";
    const response = await fetch(`${cfg.url}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${cfg.key}`
      },
      body: JSON.stringify({
        model: cfg.model,
        temperature: 0.7,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: styleEntry.content }
        ]
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      const compressed = data.choices[0].message.content.trim();
      chatSettings.compressedWritingStyle = compressed;
      await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(chatSettings));
      showToast('文风已应用并压缩');
    } else {
      throw new Error('API请求失败');
    }
  } catch (error) {
    console.error('压缩文风失败:', error);
    showToast('压缩文风失败，将使用原始内容的前100字');
    chatSettings.compressedWritingStyle = styleEntry.content.substring(0, 100);
    await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(chatSettings));
  } finally {
    if (styleSelect && styleSelect.options[styleSelect.selectedIndex]) {
      styleSelect.options[styleSelect.selectedIndex].text = styleEntry.name;
    }
  }
};

// 预览聊天背景文件
function previewChatBgFile(input) {"""

content = content.replace(searchFunc, replaceFunc)

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Modifications applied successfully.')
