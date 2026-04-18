import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# page-contacts
content = content.replace(
    '''      <div class="page-body">
        <div class="menu-item" onclick="openSub('api-win')">聊天API设置</div>
        <div class="menu-item" onclick="openSub('writing-style-win')">文风设置</div>
        <div class="menu-item" onclick="openSub('world-win')">世界书管理</div>
        <div class="menu-item" onclick="openSub('user-mask-setting')">用户面具设置</div>
        <div class="menu-item" onclick="openSub('userSetting')">记忆设置</div>
        <div class="menu-item" onclick="openSub('theme-setting')">美化设置</div>
        <div class="menu-item" onclick="openSub('personal-setting')">个人设置</div>
      </div>''',
    '''      <div class="page-body">
        <div class="menu-item" onclick="openSub('api-win')"><i class="iconfont icon-rule" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>聊天API设置</div>
        <div class="menu-item" onclick="openSub('writing-style-win')"><i class="iconfont icon-yuedu" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>文风设置</div>
        <div class="menu-item" onclick="openSub('world-win')"><i class="iconfont icon-rili" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>世界书管理</div>
        <div class="menu-item" onclick="openSub('user-mask-setting')"><i class="iconfont icon-wode" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>用户面具设置</div>
        <div class="menu-item" onclick="openSub('userSetting')"><i class="iconfont icon-activity1" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>记忆设置</div>
        <div class="menu-item" onclick="openSub('theme-setting')"><i class="iconfont icon-yanjing" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>美化设置</div>
        <div class="menu-item" onclick="openSub('personal-setting')"><i class="iconfont icon-shareOrder" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>个人设置</div>
      </div>'''
)

# page-discover
content = content.replace(
    '''      <div class="page-body">
        <div class="menu-item" onclick="openSub('moments-page')">朋友圈</div>
        <div class="menu-item" onclick="openSub('forum-page')">论坛</div>
      </div>''',
    '''      <div class="page-body">
        <div class="menu-item" onclick="openSub('moments-page')"><i class="iconfont icon-shareOrder" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>朋友圈</div>
        <div class="menu-item" onclick="openSub('forum-page')"><i class="iconfont icon-activity1" style="margin-right:10px; color:var(--main-pink); font-size:18px;"></i>论坛</div>
      </div>'''
)

# Couple space
content = content.replace(
    '''      <div class="page-body">
        <div class="menu-item" onclick="openCoupleAlbum()">💑 情侣相册</div>
        <div class="menu-item" id="coupleMarriageBtn" onclick="openProposalPage()">💍 浪漫关系</div>
        <div style="text-align:center; margin-top:40px; color:var(--text-light); font-size:12px;">更多甜蜜功能敬请期待...</div>
      </div>''',
    '''      <div class="page-body">
        <div class="menu-item" onclick="openCoupleAlbum()"><i class="iconfont icon-dianzan1" style="margin-right:10px; color:#ff6b81; font-size:18px;"></i>情侣相册</div>
        <div class="menu-item" id="coupleMarriageBtn" onclick="openProposalPage()"><i class="iconfont icon-VIP" style="margin-right:10px; color:#ff6b81; font-size:18px;"></i>浪漫关系</div>
        <div style="text-align:center; margin-top:40px; color:var(--text-light); font-size:12px;">更多甜蜜功能敬请期待...</div>
      </div>'''
)

# Chat Search
content = content.replace(
    '''          <div style="cursor:pointer; width:32px; height:32px; display:flex; align-items:center; justify-content:center; font-size: 18px;" onclick="toggleChatSearch(event)">
            🔍
          </div>''',
    '''          <div style="cursor:pointer; width:32px; height:32px; display:flex; align-items:center; justify-content:center; font-size: 20px;" onclick="toggleChatSearch(event)">
            <i class="iconfont icon-sousuo"></i>
          </div>'''
)

content = content.replace(
    '''<span style="font-size:14px; color:#999; margin-right:8px;">🔍</span>''',
    '''<i class="iconfont icon-sousuo" style="font-size:16px; color:#999; margin-right:8px;"></i>'''
)

# Status card
content = content.replace(
    '<div style="font-size:11px; color:rgba(255,255,255,0.7); margin-bottom:6px;">📍 地点</div>',
    '<div style="font-size:11px; color:rgba(255,255,255,0.7); margin-bottom:6px;"><i class="iconfont icon-didian" style="font-size:12px; margin-right:2px;"></i>地点</div>'
)
content = content.replace(
    '<div style="font-size:11px; color:rgba(255,255,255,0.7); margin-bottom:6px;">😊 心情</div>',
    '<div style="font-size:11px; color:rgba(255,255,255,0.7); margin-bottom:6px;"><i class="iconfont icon--happy-" style="font-size:12px; margin-right:2px;"></i>心情</div>'
)
content = content.replace(
    '<div style="font-size:11px; color:rgba(255,255,255,0.7); margin-bottom:6px;">💭 心声</div>',
    '<div style="font-size:11px; color:rgba(255,255,255,0.7); margin-bottom:6px;"><i class="iconfont icon-neixindubai" style="font-size:12px; margin-right:2px;"></i>心声</div>'
)
content = content.replace(
    '<div style="font-size:11px; color:rgba(255,255,255,0.7);">💚 好感度</div>',
    '<div style="font-size:11px; color:rgba(255,255,255,0.7);"><i class="iconfont icon-xintiao1" style="font-size:12px; margin-right:2px;"></i>好感度</div>'
)

# STM delete button
content = content.replace(
    '<div style="font-size:18px; color:var(--main-pink); cursor:pointer;" onclick="toggleStmBatchDelete()" id="stm-delete-btn">🗑️</div>',
    '<div style="font-size:20px; color:var(--main-pink); cursor:pointer;" onclick="toggleStmBatchDelete()" id="stm-delete-btn"><i class="iconfont icon-shanchu"></i></div>'
)

# Memory settings emojis
content = content.replace(
    '<div class="setting-section-title">🧠 记忆总结设置</div>',
    '<div class="setting-section-title"><i class="iconfont icon-activity1" style="font-size:18px; margin-right:4px;"></i>记忆总结设置</div>'
)
content = content.replace(
    '<div class="setting-desc">🔄 容错说明：',
    '<div class="setting-desc"><i class="iconfont icon-suspend" style="font-size:14px; margin-right:4px;"></i>容错说明：'
)
content = content.replace(
    '<div onclick="resetLtmPrompt()" style="font-size:12px; color:var(--main-pink); cursor:pointer;">🔄 恢复默认</div>',
    '<div onclick="resetLtmPrompt()" style="font-size:12px; color:var(--main-pink); cursor:pointer;"><i class="iconfont icon-suspend" style="font-size:12px; margin-right:2px;"></i>恢复默认</div>'
)
content = content.replace(
    '<div onclick="resetStmPrompt()" style="font-size:12px; color:var(--main-pink); cursor:pointer;">🔄 恢复默认</div>',
    '<div onclick="resetStmPrompt()" style="font-size:12px; color:var(--main-pink); cursor:pointer;"><i class="iconfont icon-suspend" style="font-size:12px; margin-right:2px;"></i>恢复默认</div>'
)
content = content.replace(
    '<button class="save-btn" onclick="saveMemorySettings()" style="margin-bottom:20px;">💾 保存记忆设置</button>',
    '<button class="save-btn" onclick="saveMemorySettings()" style="margin-bottom:20px;"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>保存记忆设置</button>'
)

# other save buttons
content = re.sub(
    r'<button class="save-btn" onclick="saveAllChatSettings\(\)">(.*?)保存所有设置</button>',
    r'<button class="save-btn" onclick="saveAllChatSettings()"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>保存所有设置</button>',
    content
)
content = re.sub(
    r'<button class="save-btn" onclick="saveAllGroupChatSettings\(\)">(.*?)保存群聊设置</button>',
    r'<button class="save-btn" onclick="saveAllGroupChatSettings()"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>保存群聊设置</button>',
    content
)

# Replace more emojis with icons
content = content.replace(
    '<div style="font-size:13px; color:var(--main-pink); margin-bottom:8px; font-weight: 500;">🔑 触发关键词</div>',
    '<div style="font-size:13px; color:var(--main-pink); margin-bottom:8px; font-weight: 500;"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>触发关键词</div>'
)

content = content.replace(
    '<button class="save-btn" onclick="saveWritingStyleEntry()">保存</button>',
    '<button class="save-btn" onclick="saveWritingStyleEntry()"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>保存</button>'
)
content = content.replace(
    '<button class="save-btn" onclick="saveUserMask()">保存面具</button>',
    '<button class="save-btn" onclick="saveUserMask()"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>保存面具</button>'
)
content = content.replace(
    '<button class="save-btn" onclick="saveWorldBookEntry()">保存条目</button>',
    '<button class="save-btn" onclick="saveWorldBookEntry()"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>保存条目</button>'
)
content = content.replace(
    '<button class="save-btn" onclick="saveGroupChat()">创建群聊</button>',
    '<button class="save-btn" onclick="saveGroupChat()"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>创建群聊</button>'
)
content = content.replace(
    '<button class="save-btn" onclick="saveContact()">创建角色</button>',
    '<button class="save-btn" onclick="saveContact()"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>创建角色</button>'
)
content = content.replace(
    '<button class="save-btn" onclick="saveMarriedSettings()" style="margin-top:10px;">保存甜蜜设置</button>',
    '<button class="save-btn" onclick="saveMarriedSettings()" style="margin-top:10px;"><i class="iconfont icon-rule" style="font-size:14px; margin-right:4px;"></i>保存甜蜜设置</button>'
)

content = content.replace(
    '<span>🖼️</span> 上传头像',
    '<i class="iconfont icon-tupian" style="font-size:14px; margin-right:4px;"></i> 上传头像'
)
content = content.replace(
    '<span>⬆️</span> 上传背景',
    '<i class="iconfont icon-tupian" style="font-size:14px; margin-right:4px;"></i> 上传背景'
)
content = content.replace(
    '<span>🖼️</span> 上传背景',
    '<i class="iconfont icon-tupian" style="font-size:14px; margin-right:4px;"></i> 上传背景'
)
content = content.replace(
    '<span>♻️</span> 恢复默认',
    '<i class="iconfont icon-suspend" style="font-size:14px; margin-right:4px;"></i> 恢复默认'
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Replacements done in index.html")