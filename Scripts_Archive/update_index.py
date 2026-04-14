import re

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 在通讯录页面添加“文风设置”入口
    target_menu_item = '<div class="menu-item" onclick="openSub('world-win')">世界书管理</div>'
    replacement_menu_item = '<div class="menu-item" onclick="openSub('writing-style-win')">文风设置</div>
        <div class="menu-item" onclick="openSub('world-win')">世界书管理</div>'
    
    if target_menu_item in content and '<div class="menu-item" onclick="openSub('writing-style-win')">文风设置</div>' not in content:
        content = content.replace(target_menu_item, replacement_menu_item)
    
    # 2. 修改世界书管理页面的分类tab
    old_tabs = """<div class="wb-tab" onclick="filterWorldBook('语言规范')" data-category="语言规范" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">语言规范</div>
        <div class="wb-tab" onclick="filterWorldBook('html')" data-category="html" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">html</div>"""
    new_tabs = """<div class="wb-tab" onclick="filterWorldBook('世界观')" data-category="世界观" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">世界观</div>
        <div class="wb-tab" onclick="filterWorldBook('其他')" data-category="其他" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">其他</div>"""
    
    if old_tabs in content:
        content = content.replace(old_tabs, new_tabs)
        
    # 3. 修改新增世界书页面的分类选项
    old_options = """<option value="记忆总结">记忆总结</option>
            <option value="语言规范">语言规范</option>
            <option value="html">html</option>"""
    new_options = """<option value="记忆总结">记忆总结</option>
            <option value="世界观">世界观</option>
            <option value="其他">其他</option>"""
            
    if old_options in content:
        content = content.replace(old_options, new_options)
        
    # 4. 新增两个二级页面，加在 add-worldbook 后面
    add_worldbook_end = '<button class="save-btn" onclick="saveWorldBookEntry()">保存条目</button>
      </div>
    </div>'
    
    writing_style_pages = """
    <div class="sub-page" id="writing-style-win">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('writing-style-win')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">文风设置</div>
        <div style="margin-left:auto; font-size:24px; color:var(--text-dark); cursor:pointer;" onclick="openSub('add-writing-style')">+</div>
      </div>
      <div style="display:flex; gap:8px; padding:10px 20px; border-bottom:1px solid #f0e8df; background:rgba(255,255,255,0.7);">
        <div class="wb-tab active" data-category="文风" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:var(--main-pink); color:white;">全部文风</div>
      </div>
      <div class="page-body" id="writingStyleList">
        <div class="empty-tip">暂无文风设定<br>点击右上角 + 添加</div>
      </div>
    </div>

    <div class="sub-page" id="add-writing-style">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('add-writing-style')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">新增文风设定</div>
      </div>
      <div class="page-body">
        <div style="background: rgba(255, 192, 203, 0.2); padding: 10px; border-radius: 8px; margin-bottom: 15px; color: #d81b60; font-size: 13px;">
          ⚠️ 提示：上传/保存文风后会消耗一次API进行压缩提炼，方便后续选择切换。
        </div>
        <div class="form-section">
          <div class="form-label">名称</div>
          <input class="form-input" id="writing-style-name" placeholder="输入文风名称" oninput="saveWritingStyleDraft()">
        </div>
        <div class="form-section" style="display:none;">
          <div class="form-label">分类</div>
          <select class="form-select" id="writing-style-category">
            <option value="文风" selected>文风</option>
          </select>
        </div>
        <div class="form-section">
          <div class="form-label">触发方式</div>
          <div style="display:flex; gap:15px; margin-top:8px; margin-bottom:10px;">
            <label style="display:flex; align-items:center; font-size:14px; color:var(--text-dark); cursor:pointer;" onclick="setTimeout(() => { toggleWsKeywordInput(); saveWritingStyleDraft(); }, 10)">
              <input type="radio" name="ws-trigger-type" value="always" checked style="margin-right:6px;"> 常驻（全局生效）
            </label>
            <label style="display:flex; align-items:center; font-size:14px; color:var(--text-dark); cursor:pointer;" onclick="setTimeout(() => { toggleWsKeywordInput(); saveWritingStyleDraft(); }, 10)">
              <input type="radio" name="ws-trigger-type" value="keyword" style="margin-right:6px;"> 关键词触发
            </label>
          </div>
          <div id="ws-keyword-container" style="display:none; background: #fff8fa; padding: 12px; border-radius: 12px; border: 1px solid var(--light-pink); margin-bottom: 10px;">
            <div style="font-size:13px; color:var(--main-pink); margin-bottom:8px; font-weight: 500;">🔑 触发关键词</div>
            <input class="form-input" id="writing-style-keywords" placeholder="多个用逗号隔开 (如: 咖啡馆，左岸)" oninput="saveWritingStyleDraft()">
            <div class="tip-text" style="margin-top:8px; line-height: 1.4;">当最近的聊天记录中包含上述关键词时，此设定才会被发送给AI。推荐使用关键词触发以节省Token。</div>
          </div>
        </div>
        <div class="form-section">
          <div class="form-label">文风设定内容</div>
          <textarea class="form-textarea" id="writing-style-content" placeholder="输入详细的文风设定内容..." oninput="saveWritingStyleDraft()"></textarea>
          <div style="margin-top:10px;">
            <label class="upload-btn" style="display:inline-block; margin:0;">
              📄 导入文档 (支持txt/docx, 1M以内)
              <input type="file" id="writing-style-file" accept=".txt,.docx" onchange="importWritingStyleFile(this)" style="display:none;">
            </label>
            <span style="font-size:12px; color:var(--text-light); margin-left:10px;">支持txt和docx格式</span>
          </div>
        </div>
        <button class="save-btn" onclick="saveWritingStyleEntry()">保存并提炼</button>
      </div>
    </div>"""

    if writing_style_pages not in content and add_worldbook_end in content:
        content = content.replace(add_worldbook_end, add_worldbook_end + "
" + writing_style_pages)
        
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()