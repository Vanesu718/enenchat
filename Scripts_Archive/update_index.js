const fs = require('fs');

let html = fs.readFileSync('index.html', 'utf8');

// 1. Add menu item
if (!html.includes('writing-style-win')) {
    html = html.replace(
        '<div class="menu-item" onclick="openSub(\'world-win\')">世界书管理</div>',
        '<div class="menu-item" onclick="openSub(\'world-win\')">世界书管理</div>\n        <div class="menu-item" onclick="openSub(\'writing-style-win\')">文风设置</div>'
    );
    console.log("Added contacts menu item.");
}

// 2. Add Writing Style Pages
if (!html.includes('id="writing-style-win"')) {
    const pages = `
    <!-- 文风设置管理页面 -->
    <div class="sub-page" id="writing-style-win">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('writing-style-win')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">文风设置</div>
        <div style="margin-left:auto; font-size:24px; color:var(--text-dark); cursor:pointer;" onclick="openSub('add-writing-style')">+</div>
      </div>
      <div class="page-body" id="writingStyleList">
        <div class="empty-tip">暂无文风设置<br>点击右上角 + 新增</div>
      </div>
    </div>

    <div class="sub-page" id="add-writing-style">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('add-writing-style')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title" id="add-ws-title">新增文风</div>
      </div>
      <div class="page-body">
        <div class="form-section">
          <div class="form-label">文风名称</div>
          <input class="form-input" id="ws-name" placeholder="输入文风名称">
        </div>
        <div class="form-section">
          <div class="form-label">文风内容 (长文本)</div>
          <textarea class="form-textarea" id="ws-content" placeholder="输入详细的文风和行为规范" style="height:200px;"></textarea>
        </div>
        <input type="hidden" id="ws-id" value="">
        <button class="save-btn" onclick="saveWritingStyle()">保存</button>
      </div>
    </div>
`;
    html = html.replace(
        /<\/div>\s*<\/div>\s*<!-- 用户面具设置页面 -->/,
        '</div>\n    </div>\n' + pages + '\n    <!-- 用户面具设置页面 -->'
    );
    console.log("Added Writing Style pages.");
}

// 3. Add to chat setting (single chat)
if (!html.includes('id="chatWritingStyleSelect"')) {
    const chat_ws = `
        <!-- 文风单选 -->
        <div class="setting-section">
          <div class="setting-section-title">当前聊天文风</div>
          <div class="setting-desc">⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<b>每切换一次都会调用一次 API</b>。</div>
          <select class="form-select" id="chatWritingStyleSelect" style="margin-top:10px;">
            <option value="">--不使用文风--</option>
          </select>
        </div>
`;
    html = html.replace(
        /<\/select>\s*<\/div>\s*<!-- 称呼选项 -->/,
        '</select>\n        </div>\n' + chat_ws + '\n        <!-- 称呼选项 -->'
    );
    console.log("Added Chat Writing Style setting.");
}

// 4. Add to group chat setting
if (!html.includes('id="groupChatWritingStyleSelect"')) {
    const group_ws = `
        <!-- 文风单选 -->
        <div class="setting-section">
          <div class="setting-section-title">当前聊天文风</div>
          <div class="setting-desc">⚠️ 注意：选择文风后会调用一次 API，请确定好再切换，<b>每切换一次都会调用一次 API</b>。</div>
          <select class="form-select" id="groupChatWritingStyleSelect" style="margin-top:10px;">
            <option value="">--不使用文风--</option>
          </select>
        </div>
`;
    // Find where groupChatWorldbookSelect section ends
    const regex = /<select class="form-select" id="groupChatWorldbookSelect" style="margin-top:10px;">[\s\S]*?<\/select>\s*<\/div>/;
    html = html.replace(regex, match => match + '\n' + group_ws);
    console.log("Added Group Chat Writing Style setting.");
}

fs.writeFileSync('index.html', html, 'utf8');
console.log("index.html updated successfully.");
