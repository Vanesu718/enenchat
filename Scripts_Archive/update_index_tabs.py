import re
import sys

def modify_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start of the chat-settings-page body
    start_pattern = r'(<div class="sub-page" id="chat-settings-page">\s*<div class="page-header">.*?</svg></div>\s*<div class="page-title">.*?</div>\s*</div>\s*<div class="page-body">)'
    
    match = re.search(start_pattern, content, re.DOTALL)
    if not match:
        print("Could not find start pattern")
        return
    
    start_idx = match.end()
    
    # Find the end of the sections, which is before the save button
    end_pattern = r'(<!-- 保存按钮 -->\s*<button class="tb-btn" style="width:100%; margin-top:20px;" onclick="saveAllChatSettings\(\)">)'
    end_match = re.search(end_pattern, content[start_idx:])
    if not end_match:
        print("Could not find end pattern")
        return
        
    end_idx = start_idx + end_match.start()
    
    body_content = content[start_idx:end_idx]
    
    # We need to extract all setting-sections
    sections = re.findall(r'(<!-- .*? -->\s*<div class="setting-section">.*?</div>)', body_content, re.DOTALL)
    
    if len(sections) < 10:
        print(f"Only found {len(sections)} sections, expected more.")
        # Let's try splitting by '<!-- ' instead
        sections_split = body_content.split('<!-- ')
        sections = ['<!-- ' + s for s in sections_split if s.strip()]
    
    # Let's map sections to the tabs
    # 基础功能: 显示设置, 聊天背景设置, 核心设定与环境备忘录 (chatContactMemo)
    # 角色设定: 自定义我的头像, 用户面具选择, 我的专属昵称, 用户面具设定, 联系人分组设置, 联系人头像和名称设置, 联系人设定修改 (contactMaskTextarea)
    # 记忆与高阶: 世界书勾选列表
    
    basic_features = []
    role_settings = []
    memory_advanced = []
    
    for s in sections:
        if 'sceneSettingTextarea' in s:
            continue # Skip scene setting
        
        if 'hide-avatar-toggle' in s or 'chatBgPreview' in s or 'chatContactMemo' in s:
            basic_features.append(s)
        elif 'chatUserAvatarPreview' in s or 'chatUserMaskSelect' in s or 'chatNicknameInput' in s or 'userMaskTextarea' in s or 'chatContactGroup' in s or 'contactAvatarPreview' in s or 'contactMaskTextarea' in s:
            role_settings.append(s)
        elif 'worldbook-checkbox-list' in s:
            memory_advanced.append(s)
        else:
            print("Uncategorized section:", s[:50])
            basic_features.append(s) # fallback
            
    # Now build the new body
    tabs_html = """
        <!-- Tabs Header -->
        <div class="chat-settings-tabs">
          <button class="settings-tab-btn active" onclick="switchChatSettingsTab('basic')">基础功能</button>
          <button class="settings-tab-btn" onclick="switchChatSettingsTab('role')">角色设定</button>
          <button class="settings-tab-btn" onclick="switchChatSettingsTab('memory')">记忆与高阶</button>
        </div>

        <!-- Tab Content: 基础功能 -->
        <div class="settings-tab-content active" id="chat-settings-tab-basic">
""" + "".join(basic_features) + """
        </div>

        <!-- Tab Content: 角色设定 -->
        <div class="settings-tab-content" id="chat-settings-tab-role">
""" + "".join(role_settings) + """
        </div>

        <!-- Tab Content: 记忆与高阶 -->
        <div class="settings-tab-content" id="chat-settings-tab-memory">
""" + "".join(memory_advanced) + """
        </div>
"""
    
    new_content = content[:start_idx] + tabs_html + content[end_idx:]
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("Modified index.html successfully.")

if __name__ == "__main__":
    modify_html()
