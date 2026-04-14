$html = Get-Content -Path 'index.html' -Raw -Encoding UTF8

$writingStyleWin = @"
    <div class="sub-page" id="writing-style-win">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('writing-style-win')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">文风管理</div>
        <div style="margin-left:auto; font-size:24px; color:var(--text-dark); cursor:pointer;" onclick="openSub('add-writing-style')">+</div>
      </div>
      <div class="setting-desc" style="margin:10px 15px; color:#e67e22;">⚠️ 提示：保存文风时会消耗少量 API Token 进行自动提炼压缩。压缩后的“小尾巴”将以最低 Token 成本在聊天中实现文风控制。</div>
      <div class="page-body" id="writingStyleList">
        <div class="empty-tip">暂无文风<br>点击右上角 + 添加</div>
      </div>
    </div>

    <div class="sub-page" id="add-writing-style">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('add-writing-style')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">新增/编辑文风</div>
      </div>
      <div class="page-body">
        <div class="form-section">
          <div class="form-label">文风名称</div>
          <input class="form-input" id="ws-name" placeholder="例如：温柔文艺风" oninput="saveWsDraft()">
        </div>
        <div class="form-section">
          <div class="form-label">详细文风要求</div>
          <textarea class="form-textarea" id="ws-content" placeholder="输入完整的文风设定，例如：回复需温柔、体贴，多用比喻..." oninput="saveWsDraft()"></textarea>
          <div style="margin-top:10px;">
            <label class="upload-btn" style="display:inline-block; margin:0;">
              📄 导入文档 (支持txt/docx, 1M以内)
              <input type="file" id="ws-file" accept=".txt,.docx" onchange="importWsFile(this)" style="display:none;">
            </label>
          </div>
        </div>
        <div class="form-section">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div class="form-label" style="margin-bottom:0;">提炼版小尾巴</div>
            <button class="tb-clear-btn" style="background:var(--light-pink); color:var(--main-pink); padding:4px 8px; border-radius:12px; font-size:12px; border:none;" onclick="generateWsTail()">🤖 AI 压缩提炼</button>
          </div>
          <textarea class="form-textarea" id="ws-tail" placeholder="提炼后的精简指令，将附着在每次回复末尾，极省Token..." style="min-height:60px;"></textarea>
          <div class="setting-desc" style="margin-top:4px;">聊天时实际生效的是这段精简小尾巴。请先输入详细要求，再点击 AI 压缩提炼。</div>
        </div>
        <button class="save-btn" onclick="saveWritingStyleEntry()">保存文风</button>
      </div>
    </div>
"@

$html = $html.Replace('<div class="sub-page" id="userSetting">', "$writingStyleWin`n    <div class=""sub-page"" id=""userSetting"">")

$chatSettingsInject = @"
        <!-- 文风选择 -->
        <div class="setting-section">
          <div class="setting-section-title">文风选择</div>
          <div class="setting-desc">选择要应用于当前聊天的文风（“小尾巴”机制）。</div>
          <select class="form-select" id="chatWritingStyleSelect" style="margin-top:10px;">
            <option value="">--不使用文风--</option>
          </select>
        </div>
"@

$groupChatSettingsInject = @"
        <!-- 文风选择 -->
        <div class="setting-section">
          <div class="setting-section-title">文风选择</div>
          <div class="setting-desc">选择要应用于当前群聊的文风。</div>
          <select class="form-select" id="groupChatWritingStyleSelect" style="margin-top:10px;">
            <option value="">--不使用文风--</option>
          </select>
        </div>
"@

$parts = $html -split '<!-- 用户人设设定 -->'
if ($parts.Length -ge 3) {
    $html = $parts[0] + $chatSettingsInject + "`n        <!-- 用户人设设定 -->" + $parts[1] + $groupChatSettingsInject + "`n        <!-- 用户人设设定 -->" + $parts[2]
    for ($i = 3; $i -lt $parts.Length; $i++) {
        $html += "<!-- 用户人设设定 -->" + $parts[$i]
    }
} else {
    # If not enough parts, just try normal replacement for at least the first one. We can also skip this if regex is hard in PS.
    Write-Host "Warning: Could not find exactly two or more <!-- 用户人设设定 --> tags."
}

Set-Content -Path 'index.html' -Value $html -Encoding UTF8
Write-Host "HTML updated successfully"
