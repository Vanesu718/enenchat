import re
import sys

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update forum post list UI to add comment count icon
    # Find renderForumBoard
    old_board_ui = r'''<div onclick="event.stopPropagation(); deleteForumPost('\${boardKey}', \${idx})" style="font-size:16px; color:\${board.postTimeColor}; cursor:pointer; padding:4px;">×</div>
      </div>
      <div style="font-size:14px; font-weight:700; color:\${board.postTitleFontColor}; margin-bottom:5px;">\${titlePreview}</div>
      <div style="font-size:12px; color:\${board.postContentColor}; line-height:1.5; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">\${contentPreview}</div>
    `;'''
    
    new_board_ui = r'''<div onclick="event.stopPropagation(); deleteForumPost('${boardKey}', ${idx})" style="font-size:16px; color:${board.postTimeColor}; cursor:pointer; padding:4px;">×</div>
      </div>
      <div style="font-size:14px; font-weight:700; color:${board.postTitleFontColor}; margin-bottom:5px;">${titlePreview}</div>
      <div style="font-size:12px; color:${board.postContentColor}; line-height:1.5; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; margin-bottom:8px;">${contentPreview}</div>
      <div style="display:flex; justify-content:flex-end; font-size:11px; color:${board.postTimeColor};">
        <span>🔥 已有${post.comments ? post.comments.length : 0}条热议</span>
      </div>
    `;'''

    if old_board_ui in content:
        content = content.replace(old_board_ui, new_board_ui)
        print("Updated forum board UI.")
    else:
        print("Failed to find old board UI.")

    # 2. Update openForumDetail to use board colors
    old_detail = r'''<div class="page-body" id="forumDetailContent" style="padding:0; background:#f8f9fa;">
        <!-- 帖子正文区 -->
        <div id="forumPostDetailMain" style="background:#fff; padding:20px; margin-bottom:10px;"></div>
        <!-- 评论区标题 -->
        <div style="padding:10px 20px; font-size:14px; font-weight:600; color:#666; border-bottom:1px solid #eee; background:#fff;">评论区</div>
        <!-- 评论列表 -->
        <div id="forumCommentList" style="background:#fff; padding-bottom:80px;"></div>
      </div>
      <!-- 底部评论输入框 -->
      <div style="position:absolute; bottom:0; left:0; width:100%; padding:10px 15px; background:#fff; border-top:1px solid #eee; display:flex; gap:10px; align-items:center; z-index:10;">
        <input type="text" id="forumCommentInput" placeholder="写下你的评论..." style="flex:1; padding:10px 15px; border-radius:20px; border:1px solid #eee; outline:none; font-size:14px; background:#f5f5f5;">
        <button onclick="submitForumComment()" style="background:var(--main-pink); color:white; border:none; padding:8px 15px; border-radius:15px; font-size:14px; font-weight:500;">发布</button>
      </div>'''

    new_detail_html = r'''<div class="page-body" id="forumDetailContent" style="padding:0; background:var(--forum-bg, #f8f9fa);">
        <!-- 帖子正文区 -->
        <div id="forumPostDetailMain" style="background:var(--forum-card-bg, #fff); padding:20px; margin-bottom:10px;"></div>
        <!-- 评论区标题 -->
        <div style="padding:10px 20px; font-size:14px; font-weight:600; color:var(--forum-text-light, #666); border-bottom:1px solid var(--forum-border, #eee); background:var(--forum-card-bg, #fff);">评论区</div>
        <!-- 评论列表 -->
        <div id="forumCommentList" style="background:var(--forum-card-bg, #fff); padding-bottom:80px;"></div>
      </div>
      <!-- 底部评论输入框 -->
      <div style="position:absolute; bottom:0; left:0; width:100%; padding:10px 15px; background:var(--forum-card-bg, #fff); border-top:1px solid var(--forum-border, #eee); display:flex; gap:10px; align-items:center; z-index:10;">
        <input type="text" id="forumCommentInput" placeholder="写下你的评论..." style="flex:1; padding:10px 15px; border-radius:20px; border:1px solid var(--forum-border, #eee); outline:none; font-size:14px; background:var(--forum-bg, #f5f5f5); color:var(--forum-text-dark, #333);">
        <button onclick="submitForumComment()" style="background:var(--forum-accent, var(--main-pink)); color:var(--forum-btn-text, white); border:none; padding:8px 15px; border-radius:15px; font-size:14px; font-weight:500;">发布</button>
      </div>'''

    if old_detail in content:
        content = content.replace(old_detail, new_detail_html)
        print("Updated forum detail HTML.")
    else:
        print("Failed to find old forum detail HTML.")

    old_open_detail = r'''    mainEl.innerHTML = `
      <div class="forum-board-badge" style="background:${board.accentColor}22; color:${board.accentColor};">${board.emoji} ${board.name}</div>
      <div style="display:flex; align-items:center; margin-bottom:15px;">
        <img src="${post.avatar || 'clover.png'}" style="width:40px; height:40px; border-radius:50%; margin-right:12px; border:2px solid var(--light-pink);">
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:600; color:#333;">${post.authorName}</div>
          <div style="font-size:11px; color:#999; margin-top:2px;">${timeStr}</div>
        </div>
      </div>
      <div style="font-size:18px; font-weight:700; color:#333; margin-bottom:12px; line-height:1.4;">${post.title}</div>
      <div style="font-size:15px; color:#444; line-height:1.8; white-space:pre-wrap; margin-bottom:20px;">${post.content}</div>
      <div style="display:flex; gap:20px; border-top:1px solid #eee; padding-top:15px;">
        <div style="font-size:13px; color:#666; cursor:pointer;">❤️ 点赞 (${post.likes || 0})</div>
        <div style="font-size:13px; color:#666; cursor:pointer;">💬 评论 (${post.comments?.length || 0})</div>
      </div>
    `;

    renderForumComments();
    openSub('forum-detail-page');
  }'''

    new_open_detail = r'''    // Set CSS variables for detail page color scheme
    const detailPage = document.getElementById('forum-detail-page');
    detailPage.style.setProperty('--forum-bg', board.bgColor || '#f8f9fa');
    detailPage.style.setProperty('--forum-card-bg', board.cardBg || '#fff');
    detailPage.style.setProperty('--forum-text-dark', board.postNameColor || '#333');
    detailPage.style.setProperty('--forum-text-light', board.postTimeColor || '#999');
    detailPage.style.setProperty('--forum-border', board.postBorder || '#eee');
    detailPage.style.setProperty('--forum-accent', board.accentColor || 'var(--main-pink)');
    detailPage.style.setProperty('--forum-btn-text', board.publishBtnColor || '#fff');

    // Update detail page header colors
    const header = detailPage.querySelector('.page-header');
    if (header) {
      header.style.background = board.headerBg || '#fff';
      header.style.borderBottom = `1px solid ${board.headerBorder || '#f0e8df'}`;
      const backBtn = header.querySelector('.page-back');
      if (backBtn) {
        backBtn.style.background = 'rgba(255,255,255,0.1)';
        backBtn.querySelector('svg').style.stroke = board.accentColor || '#333';
      }
      const title = header.querySelector('.page-title');
      if (title) {
        title.style.color = board.accentColor || 'var(--main-pink)';
      }
    }

    mainEl.innerHTML = `
      <div class="forum-board-badge" style="background:${board.accentColor}22; color:${board.accentColor};">${board.emoji} ${board.name}</div>
      <div style="display:flex; align-items:center; margin-bottom:15px;">
        <img src="${post.avatar || 'clover.png'}" style="width:40px; height:40px; border-radius:50%; margin-right:12px; border:2px solid ${board.accentColor}55;">
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:600; color:var(--forum-text-dark);">${post.authorName}</div>
          <div style="font-size:11px; color:var(--forum-text-light); margin-top:2px;">${timeStr}</div>
        </div>
      </div>
      <div style="font-size:18px; font-weight:700; color:${board.postTitleFontColor || '#333'}; margin-bottom:12px; line-height:1.4;">${post.title}</div>
      <div style="font-size:15px; color:${board.postContentColor || '#444'}; line-height:1.8; white-space:pre-wrap; margin-bottom:20px;">${post.content}</div>
      <div style="display:flex; gap:20px; border-top:1px solid var(--forum-border); padding-top:15px;">
        <div style="font-size:13px; color:var(--forum-text-light); cursor:pointer;">❤️ 点赞 (${post.likes || 0})</div>
        <div style="font-size:13px; color:var(--forum-text-light); cursor:pointer;">💬 评论 (${post.comments?.length || 0})</div>
      </div>
    `;

    renderForumComments();
    openSub('forum-detail-page');
  }'''
    if old_open_detail in content:
        content = content.replace(old_open_detail, new_open_detail)
        print("Updated openForumDetail logic.")
    else:
        print("Failed to find openForumDetail logic.")

    # 3. Update renderForumComments colors
    old_render_comments = r'''    const timeStr = formatTime(comment.time);
    div.innerHTML = `
      <div style="display:flex; align-items:center; margin-bottom:8px;">
        <div style="font-size:13px; font-weight:600; color:var(--main-pink);">${comment.authorName}${comment.isInteraction ? '<span class="interaction-badge">互动</span>' : ''}</div>
        <div style="font-size:11px; color:#999; margin-left:auto;">${timeStr}</div>
      </div>
      <div style="font-size:14px; color:#444; line-height:1.6;">${comment.content}</div>
    `;
    container.appendChild(div);'''

    new_render_comments = r'''    const timeStr = formatTime(comment.time);
    div.style.borderColor = 'var(--forum-border, #f5f5f5)';
    div.innerHTML = `
      <div style="display:flex; align-items:center; margin-bottom:8px;">
        <div style="font-size:13px; font-weight:600; color:var(--forum-accent, var(--main-pink));">${comment.authorName}${comment.isInteraction ? '<span class="interaction-badge" style="background:var(--forum-accent); color:var(--forum-btn-text);">互动</span>' : ''}</div>
        <div style="font-size:11px; color:var(--forum-text-light, #999); margin-left:auto;">${timeStr}</div>
      </div>
      <div style="font-size:14px; color:var(--forum-text-dark, #444); line-height:1.6;">${comment.content}</div>
    `;
    container.appendChild(div);'''
    if old_render_comments in content:
        content = content.replace(old_render_comments, new_render_comments)
        print("Updated renderForumComments colors.")
    else:
        print("Failed to find renderForumComments colors.")

    # 4. Add initial comment chain generation logic
    generate_initial_comments_code = r'''
async function generateInitialComments(post, cfg) {
  const board = FORUM_BOARDS[post.board] || { name: '综合版块', rules: '' };
  
  // 选择角色池
  const eligibleContacts = contacts.filter(c => !c.isGroup);
  if (eligibleContacts.length === 0) return;

  // 1-2个第一层角色
  const layer1Count = Math.floor(Math.random() * 2) + 1;
  const layer1Contacts = [...eligibleContacts].sort(() => Math.random() - 0.5).slice(0, layer1Count);
  
  // 2-3个第二层角色
  const remainingContacts = eligibleContacts.filter(c => !layer1Contacts.includes(c));
  const layer2Count = Math.min(Math.floor(Math.random() * 2) + 2, remainingContacts.length);
  const layer2Contacts = [...remainingContacts].sort(() => Math.random() - 0.5).slice(0, layer2Count);

  const allSelected = [...layer1Contacts, ...layer2Contacts];
  if (allSelected.length === 0) return;

  const prompt = `你现在是一个动态论坛的评论生成器。用户刚刚发布了一篇新帖子。
【帖子标题】${post.title}
【帖子正文】${post.content}
【楼主】${post.authorName}
【所属板块】${board.name}
【板块规则】${board.rules}

你需要立刻为这篇帖子生成一个热闹的初始评论链（共${allSelected.length}条评论）。
请严格按照以下层级逻辑生成：
1. 第一层（前${layer1Count}条）：直接回复楼主，引爆话题，质疑或补充细节。
2. 第二层（后${layer2Count}条）：NPC之间的观点交锋与扩散，可以回复楼主，也可以回复前排的某条评论。

可用角色列表：
${allSelected.map((c, i) => `${i+1}. 姓名: ${c.name}, 设定: ${c.persona}`).join('\n')}

任务要求：
1. 必须返回一个纯 JSON 数组，严禁包含任何 Markdown 标记（如 \`\`\`json），严禁任何解释性文字。
2. 格式必须严格如下：
[
  { "authorName": "角色姓名", "content": "评论内容", "replyTo": "被回复人姓名（如果是回复楼主，填楼主姓名；如果是回复前排评论，填前排评论人姓名）" },
  ...
]
3. 评论必须高度契合帖子内容，符合角色设定，提供信息增量，杜绝“已阅”、“666”等无效回复。
4. 确保输出的编码为标准的 UTF-8，不要使用特殊字符。`;

  try {
    const res = await fetch(`${cfg.url}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${cfg.key}` },
      body: JSON.stringify({
        model: cfg.model,
        temperature: 0.8,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    
    const data = await res.json();
    let rawText = data.choices?.[0]?.message?.content || "";
    
    let generatedComments = [];
    try {
      rawText = rawText.replace(/[\u200B-\u200D\uFEFF]/g, "").trim();
      if (rawText.includes("```")) {
        const match = rawText.match(/\[[\s\S]*\]/);
        if (match) rawText = match[0];
      }
      generatedComments = JSON.parse(rawText);
    } catch (e) {
      const jsonMatch = rawText.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        generatedComments = JSON.parse(jsonMatch[0]);
      }
    }

    if (generatedComments && generatedComments.length > 0) {
      if (!post.comments) post.comments = [];
      
      generatedComments.forEach((c, i) => {
        let content = c.content;
        if (c.replyTo && c.replyTo !== post.authorName) {
          content = `回复 @${c.replyTo} : ${content}`;
        }
        post.comments.push({
          id: (Date.now() + i).toString(),
          authorName: c.authorName,
          content: content,
          time: Date.now() + i * 60000, // 间隔1分钟
          isInteraction: true
        });
      });
      
      await saveToStorage(`FORUM_POSTS_${post.board}`, JSON.stringify(forumPostsByBoard[post.board]));
      
      // 如果当前在板块列表页，重新渲染以更新评论数
      if (document.getElementById(board.pageId || '').classList.contains('show')) {
        renderForumBoard(post.board);
      }
    }
  } catch (e) {
    console.error('生成初始评论链失败:', e);
  }
}
'''
    
    if 'async function generateInitialComments' not in content:
        # Insert before publishForumPost
        content = content.replace('async function publishForumPost() {', generate_initial_comments_code + '\nasync function publishForumPost() {')
        print("Added generateInitialComments function.")

    # 5. Call generateInitialComments in publishForumPost
    old_publish_end = r'''  await saveToStorage(`FORUM_POSTS_${currentForumBoard}`, JSON.stringify(forumPostsByBoard[currentForumBoard]));

  document.getElementById('postForumTitle').value = '';
  document.getElementById('postForumContent').value = '';
  closeSub('post-forum-page');

  if (document.getElementById(board.pageId || '').classList.contains('show')) {
    renderForumBoard(currentForumBoard);
  }

  showToast('✅ 发帖成功！正在刷新列表...');
  // 滚动到新帖子位置逻辑在 renderForumBoard 中自动处理
}'''

    new_publish_end = r'''  await saveToStorage(`FORUM_POSTS_${currentForumBoard}`, JSON.stringify(forumPostsByBoard[currentForumBoard]));

  document.getElementById('postForumTitle').value = '';
  document.getElementById('postForumContent').value = '';
  closeSub('post-forum-page');

  if (document.getElementById(board.pageId || '').classList.contains('show')) {
    renderForumBoard(currentForumBoard);
  }

  showToast('✅ 发帖成功！正在生成评论...');
  
  // Generate initial comments for user post
  if (cfg.key && cfg.url && cfg.model) {
    generateInitialComments(newPost, cfg);
  }
}'''

    if old_publish_end in content:
        content = content.replace(old_publish_end, new_publish_end)
        print("Updated publishForumPost to call generateInitialComments.")
    else:
        print("Failed to find publishForumPost end.")

    # 6. Call generateInitialComments in refreshForumBoard for each generated post
    old_refresh_end = r'''    forumPostsByBoard[boardKey] = finalPosts;
    await saveToStorage(`FORUM_POSTS_${boardKey}`, JSON.stringify(finalPosts));
    
    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('✅ 刷新成功');

  } catch (e) {'''

    new_refresh_end = r'''    forumPostsByBoard[boardKey] = finalPosts;
    await saveToStorage(`FORUM_POSTS_${boardKey}`, JSON.stringify(finalPosts));
    
    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('✅ 刷新成功，正在生成现场讨论...');

    // Generate initial comments for all new NPC posts in parallel
    if (cfg.key && cfg.url && cfg.model) {
      Promise.all(finalPosts.map(post => generateInitialComments(post, cfg))).then(() => {
        if (document.getElementById(board.pageId || '').classList.contains('show')) {
          renderForumBoard(boardKey);
        }
      });
    }

  } catch (e) {'''

    if old_refresh_end in content:
        content = content.replace(old_refresh_end, new_refresh_end)
        print("Updated refreshForumBoard to call generateInitialComments.")
    else:
        print("Failed to find refreshForumBoard end.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done.")

patch_file('index.html')
