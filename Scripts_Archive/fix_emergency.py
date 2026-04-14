import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The wrong block starts with:
#           <!-- 用户人设设定 -->
#           <div class="setting-section">
#             <div class="setting-section-title">群聊世界书</div>

search_pattern = r'''          <!-- 用户人设设定 -->
          <div class="setting-section">
            <div class="setting-section-title">群聊世界书</div>
            <div class="setting-desc">将选择的世界书设定作为全局背景信息注入到AI对话中。</div>
            <select class="form-select" id="groupChatWorldbookSelect" style="margin-top:10px;">
              <option value="">--不使用世界书--</option>
            </select>
          </div>

          <!-- 文风单选 -->
          <div class="setting-section">
            <div class="setting-section-title">当前聊天文风</div>
            <div class="setting-desc">⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<b>每切换一次都会调用一次 API</b>。</div>
            <select class="form-select" id="groupChatWritingStyleSelect" onchange="processWritingStyleSelection\(this\.value\)" style="margin-top:10px;">
              <option value="">--不使用文风--</option>
            </select>
          </div>'''

replacement = '''          <!-- 用户人设设定 -->
          <div class="setting-section">
            <div class="setting-section-title">联系人设定修改</div>
            <div class="setting-desc">设置联系人的角色面具描述，定义角色的人设特征。</div>
            <textarea class="mask-textarea" id="userMaskTextarea" placeholder="输入用户面具描述..."></textarea>
          </div>

          <!-- 场景设定 -->
          <div class="setting-section">
            <div class="setting-section-title">场景设定</div>
            <div class="setting-desc">设定你们目前的情感状态、所在地点和时空背景。如果设定中包含“两人初始”或“刚认识”等词，好感度将自动重置为0。</div>
            <textarea class="mask-textarea" id="sceneSettingTextarea" placeholder="例如：我们正坐在午后的咖啡馆里..."></textarea>
          </div>

          <!-- 联系人核心备忘录 -->
          <div class="setting-section">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <div class="setting-section-title" style="margin-bottom:0;">核心设定与环境备忘录</div>
              <button class="small-btn" onclick="extractChatMemory()" style="display:flex; align-items:center; gap:4px; padding:4px 8px;">
                <img src="ICON/AI回复按钮图标.png" style="width:16px;height:16px;">
                AI 提取
              </button>
            </div>
            <div class="setting-desc">可以随时修改（例如：下雨了、吵架了），实时生效并提醒AI。</div>
            <textarea class="mask-textarea" id="coreMemoryTextarea" placeholder="记录重要的事件或当前的特殊状态..."></textarea>
          </div>'''

# Let's fix the regex to be safer, replacing by string replacing
new_content = re.sub(search_pattern, replacement, content, flags=re.MULTILINE)

# If it didn't work because of indentation or whatever, we can find the index and manually splice
if new_content == content:
    print("Regex failed, trying manual replace")
    # Finding the block
    idx1 = content.find('id="chatNicknameInput"')
    if idx1 != -1:
        idx2 = content.find('<!-- 用户人设设定 -->', idx1)
        idx3 = content.find('<!-- 我的聊天昵称 -->', idx2 + 10)
        if idx2 != -1 and idx3 != -1:
            print("Found block to replace")
            content = content[:idx2] + replacement + "\n\n" + content[idx3:]
            new_content = content

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
    print("Done")
