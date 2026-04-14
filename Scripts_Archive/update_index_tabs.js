const fs = require('fs');

function modifyHtml() {
    let content = fs.readFileSync('index.html', 'utf8');

    const startPattern = /(<div class="sub-page" id="chat-settings-page">\s*<div class="page-header">[\s\S]*?<\/svg><\/div>\s*<div class="page-title">.*?<\/div>\s*<\/div>\s*<div class="page-body">)/;
    
    const match = content.match(startPattern);
    if (!match) {
        console.log("Could not find start pattern");
        return;
    }
    
    const startIdx = match.index + match[0].length;
    
    const endPattern = /(<!-- 保存按钮 -->\s*<button class="tb-btn" style="width:100%; margin-top:20px;" onclick="saveAllChatSettings\(\)">)/;
    const endMatch = content.substring(startIdx).match(endPattern);
    
    if (!endMatch) {
        console.log("Could not find end pattern");
        return;
    }
    
    const endIdx = startIdx + endMatch.index;
    
    const bodyContent = content.substring(startIdx, endIdx);
    
    const sectionsSplit = bodyContent.split('<!-- ');
    const sections = sectionsSplit.filter(s => s.trim().length > 0).map(s => '<!-- ' + s);
    
    let basicFeatures = [];
    let roleSettings = [];
    let memoryAdvanced = [];
    
    for (let s of sections) {
        if (s.includes('sceneSettingTextarea')) {
            continue; // Skip scene setting
        }
        
        if (s.includes('hide-avatar-toggle') || s.includes('chatBgPreview') || s.includes('chatContactMemo')) {
            basicFeatures.push(s);
        } else if (s.includes('chatUserAvatarPreview') || s.includes('chatUserMaskSelect') || s.includes('chatNicknameInput') || s.includes('userMaskTextarea') || s.includes('chatContactGroup') || s.includes('contactAvatarPreview') || s.includes('contactMaskTextarea')) {
            roleSettings.push(s);
        } else if (s.includes('worldbook-checkbox-list')) {
            memoryAdvanced.push(s);
        } else {
            console.log("Uncategorized section, assigning to basic: ", s.substring(0, 50));
            basicFeatures.push(s);
        }
    }
    
    const tabsHtml = `
        <!-- Tabs Header -->
        <div class="chat-settings-tabs">
          <button class="settings-tab-btn active" onclick="switchChatSettingsTab('basic')">基础功能</button>
          <button class="settings-tab-btn" onclick="switchChatSettingsTab('role')">角色设定</button>
          <button class="settings-tab-btn" onclick="switchChatSettingsTab('memory')">记忆与高阶</button>
        </div>

        <!-- Tab Content: 基础功能 -->
        <div class="settings-tab-content active" id="chat-settings-tab-basic">
${basicFeatures.join('')}        </div>

        <!-- Tab Content: 角色设定 -->
        <div class="settings-tab-content" id="chat-settings-tab-role">
${roleSettings.join('')}        </div>

        <!-- Tab Content: 记忆与高阶 -->
        <div class="settings-tab-content" id="chat-settings-tab-memory">
${memoryAdvanced.join('')}        </div>
`;

    const newContent = content.substring(0, startIdx) + tabsHtml + content.substring(endIdx);
    
    fs.writeFileSync('index.html', newContent, 'utf8');
    console.log("Modified index.html successfully.");
}

modifyHtml();