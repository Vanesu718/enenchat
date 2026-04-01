import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix forum detail page colors
# We need to add IDs to some elements in forum-detail-page first
html_to_replace = """    <!-- 帖子详情页面 -->
    <div class="sub-page" id="forum-detail-page">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('forum-detail-page')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">帖子详情</div>
      </div>
      <div class="page-body" id="forumDetailContent" style="padding:0; background:#f8f9fa;">
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
      </div>
    </div>"""

html_replacement = """    <!-- 帖子详情页面 -->
    <div class="sub-page" id="forum-detail-page">
      <div class="page-header" id="forum-detail-header">
        <div class="page-back" id="forum-detail-back" onclick="closeSub('forum-detail-page')"><svg viewBox="0 0 24 24" id="forum-detail-back-svg"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title" id="forum-detail-title">帖子详情</div>
      </div>
      <div class="page-body" id="forumDetailContent" style="padding:0; background:#f8f9fa;">
        <!-- 帖子正文区 -->
        <div id="forumPostDetailMain" style="background:#fff; padding:20px; margin-bottom:10px;"></div>
        <!-- 评论区标题 -->
        <div id="forumCommentTitle" style="padding:10px 20px; font-size:14px; font-weight:600; color:#666; border-bottom:1px solid #eee; background:#fff;">评论区</div>
        <!-- 评论列表 -->
        <div id="forumCommentList" style="background:#fff; padding-bottom:80px;"></div>
      </div>
      <!-- 底部评论输入框 -->
      <div id="forumCommentInputContainer" style="position:absolute; bottom:0; left:0; width:100%; padding:10px 15px; background:#fff; border-top:1px solid #eee; display:flex; gap:10px; align-items:center; z-index:10;">
        <input type="text" id="forumCommentInput" placeholder="写下你的评论..." style="flex:1; padding:10px 15px; border-radius:20px; border:1px solid #eee; outline:none; font-size:14px; background:#f5f5f5; color:#333;">
        <button id="forumCommentSubmitBtn" onclick="submitForumComment()" style="background:var(--main-pink); color:white; border:none; padding:8px 15px; border-radius:15px; font-size:14px; font-weight:500;">发布</button>
      </div>
    </div>"""

content = content.replace(html_to_replace, html_replacement)

# Update openForumDetail
open_forum_detail_old = """function openForumDetail(boardKey, postId) {
  const posts = forumPostsByBoard[boardKey] || [];
  const post = posts.find(p => p.id === postId);
  if (!post) return;
  currentDetailPost = post;
  
  const board = FORUM_BOARDS[boardKey];
  const mainEl = document.getElementById('forumPostDetailMain');
  const timeStr = new Date(post.time).toLocaleString();
  
  mainEl.innerHTML = `
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
}"""

open_forum_detail_new = """function openForumDetail(boardKey, postId) {
  const posts = forumPostsByBoard[boardKey] || [];
  const post = posts.find(p => p.id === postId);
  if (!post) return;
  currentDetailPost = post;
  
  const board = FORUM_BOARDS[boardKey];
  const mainEl = document.getElementById('forumPostDetailMain');
  const timeStr = new Date(post.time).toLocaleString();
  
  // Apply board colors to the detail page
  const header = document.getElementById('forum-detail-header');
  const backBtn = document.getElementById('forum-detail-back');
  const backSvg = document.getElementById('forum-detail-back-svg');
  const titleEl = document.getElementById('forum-detail-title');
  const detailContent = document.getElementById('forumDetailContent');
  const commentTitle = document.getElementById('forumCommentTitle');
  const commentList = document.getElementById('forumCommentList');
  const inputContainer = document.getElementById('forumCommentInputContainer');
  const commentInput = document.getElementById('forumCommentInput');
  const submitBtn = document.getElementById('forumCommentSubmitBtn');

  if (header) {
    header.style.background = board.headerBg;
    header.style.borderBottom = `1px solid ${board.headerBorder}`;
  }
  if (backBtn) {
    backBtn.style.background = `${board.accentColor}22`;
  }
  if (backSvg) {
    backSvg.style.stroke = board.accentColor;
  }
  if (titleEl) {
    titleEl.style.color = board.accentColor;
  }
  if (detailContent) {
    detailContent.style.background = board.bgColor;
  }
  if (mainEl) {
    mainEl.style.background = board.postBg;
    mainEl.style.borderBottom = `1px solid ${board.postBorder}`;
  }
  if (commentTitle) {
    commentTitle.style.background = board.postBg;
    commentTitle.style.color = board.accentColor;
    commentTitle.style.borderBottom = `1px solid ${board.postBorder}`;
  }
  if (commentList) {
    commentList.style.background = board.postBg;
  }
  if (inputContainer) {
    inputContainer.style.background = board.headerBg;
    inputContainer.style.borderTop = `1px solid ${board.headerBorder}`;
  }
  if (commentInput) {
    commentInput.style.background = board.bgColor;
    commentInput.style.color = board.postContentColor;
    commentInput.style.border = `1px solid ${board.postBorder}`;
  }
  if (submitBtn) {
    submitBtn.style.background = board.accentColor;
    submitBtn.style.color = board.publishBtnColor;
  }
  
  mainEl.innerHTML = `
    <div class="forum-board-badge" style="background:${board.accentColor}22; color:${board.accentColor};">${board.emoji} ${board.name}</div>
    <div style="display:flex; align-items:center; margin-bottom:15px;">
      <img src="${post.avatar || 'clover.png'}" style="width:40px; height:40px; border-radius:50%; margin-right:12px; border:2px solid ${board.accentColor}44;">
      <div style="flex:1;">
        <div style="font-size:14px; font-weight:600; color:${board.postNameColor};">${post.authorName}</div>
        <div style="font-size:11px; color:${board.postTimeColor}; margin-top:2px;">${timeStr}</div>
      </div>
    </div>
    <div style="font-size:18px; font-weight:700; color:${board.postTitleFontColor}; margin-bottom:12px; line-height:1.4;">${post.title}</div>
    <div style="font-size:15px; color:${board.postContentColor}; line-height:1.8; white-space:pre-wrap; margin-bottom:20px;">${post.content}</div>
    <div style="display:flex; gap:20px; border-top:1px solid ${board.postBorder}; padding-top:15px;">
      <div style="font-size:13px; color:${board.postTimeColor}; cursor:pointer;">❤️ 点赞 (${post.likes || 0})</div>
      <div style="font-size:13px; color:${board.postTimeColor}; cursor:pointer;">💬 评论 (${post.comments?.length || 0})</div>
    </div>
  `;
  
  renderForumComments();
  openSub('forum-detail-page');
}"""

content = content.replace(open_forum_detail_old, open_forum_detail_new)

# Update renderForumComments to use board colors
render_forum_comments_old = """function renderForumComments() {
  const container = document.getElementById('forumCommentList');
  const comments = currentDetailPost.comments || [];
  
  if (comments.length === 0) {
    container.innerHTML = '<div style="padding:40px; text-align:center; color:#999; font-size:13px;">暂无评论，快来抢沙发吧~</div>';
    return;
  }
  
  container.innerHTML = '';
  comments.forEach(comment => {
    const div = document.createElement('div');
    div.style.cssText = 'padding:15px 20px; border-bottom:1px solid #f5f5f5;';
    if (comment.isInteraction) {
      div.classList.add('forum-interaction-comment');
    }
    
    const timeStr = formatTime(comment.time);
    div.innerHTML = `
      <div style="display:flex; align-items:center; margin-bottom:8px;">
        <div style="font-size:13px; font-weight:600; color:var(--main-pink);">${comment.authorName}${comment.isInteraction ? '<span class="interaction-badge">互动</span>' : ''}</div>
        <div style="font-size:11px; color:#999; margin-left:auto;">${timeStr}</div>
      </div>
      <div style="font-size:14px; color:#444; line-height:1.6;">${comment.content}</div>
    `;
    container.appendChild(div);
  });
}"""

render_forum_comments_new = """function renderForumComments() {
  const container = document.getElementById('forumCommentList');
  const comments = currentDetailPost.comments || [];
  const board = FORUM_BOARDS[currentDetailPost.board];
  
  if (comments.length === 0) {
    container.innerHTML = `<div style="padding:40px; text-align:center; color:${board.postTimeColor}; font-size:13px;">暂无评论，快来抢沙发吧~</div>`;
    return;
  }
  
  container.innerHTML = '';
  comments.forEach(comment => {
    const div = document.createElement('div');
    div.style.cssText = `padding:15px 20px; border-bottom:1px solid ${board.postBorder};`;
    if (comment.isInteraction) {
      div.style.background = `${board.accentColor}11`;
      div.style.borderLeft = `3px solid ${board.accentColor}`;
    }
    
    const timeStr = formatTime(comment.time);
    div.innerHTML = `
      <div style="display:flex; align-items:center; margin-bottom:8px;">
        <div style="font-size:13px; font-weight:600; color:${board.accentColor};">${comment.authorName}${comment.isInteraction ? `<span class="interaction-badge" style="background:${board.accentColor};">互动</span>` : ''}</div>
        <div style="font-size:11px; color:${board.postTimeColor}; margin-left:auto;">${timeStr}</div>
      </div>
      <div style="font-size:14px; color:${board.postContentColor}; line-height:1.6;">${comment.content}</div>
    `;
    container.appendChild(div);
  });
}"""

content = content.replace(render_forum_comments_old, render_forum_comments_new)

# Update renderForumBoard to show dynamic comment count
render_forum_board_old = """      <div style="font-size:14px; font-weight:700; color:${board.postTitleFontColor}; margin-bottom:5px;">${titlePreview}</div>
      <div style="font-size:12px; color:${board.postContentColor}; line-height:1.5; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">${contentPreview}</div>
    `;
    container.appendChild(div);"""

render_forum_board_new = """      <div style="font-size:14px; font-weight:700; color:${board.postTitleFontColor}; margin-bottom:5px;">${titlePreview}</div>
      <div style="font-size:12px; color:${board.postContentColor}; line-height:1.5; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; margin-bottom:8px;">${contentPreview}</div>
      <div style="display:flex; justify-content:flex-end; align-items:center;">
        <div style="font-size:11px; color:${board.accentColor}; background:${board.accentColor}15; padding:3px 8px; border-radius:12px; display:flex; align-items:center; gap:4px;">
          <span>🔥</span> 已有${post.comments?.length || 0}条热议
        </div>
      </div>
    `;
    container.appendChild(div);"""

content = content.replace(render_forum_board_old, render_forum_board_new)

# Update refreshForumBoard to generate initial comments
# We need to add the initial comments generation logic after parsing the posts
refresh_forum_board_old = """    const finalPosts = generatedPosts.slice(0, 5).map((p, i) => {
      // 尽量匹配姓名，匹配不到则按顺序对应
      let poster = posters.find(postr => postr.name === p.authorName) || posters[i % posters.length];
      
      return {
        id: (Date.now() + i).toString(),
        authorName: poster.name, 
        avatar: poster.avatar || 'clover.png',
        title: p.title || '无题',
        content: p.content || '',
        time: Date.now() - (i * 3600000 + Math.floor(Math.random() * 1800000)), // 随机分布在过去几小时内
        board: boardKey,
        isAI: true
      };
    });

    forumPostsByBoard[boardKey] = finalPosts;
    await saveToStorage(`FORUM_POSTS_${boardKey}`, JSON.stringify(finalPosts));
    
    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('✅ 刷新成功');"""

refresh_forum_board_new = """    const finalPosts = generatedPosts.slice(0, 5).map((p, i) => {
      // 尽量匹配姓名，匹配不到则按顺序对应
      let poster = posters.find(postr => postr.name === p.authorName) || posters[i % posters.length];
      
      return {
        id: (Date.now() + i).toString(),
        authorName: poster.name, 
        avatar: poster.avatar || 'clover.png',
        title: p.title || '无题',
        content: p.content || '',
        time: Date.now() - (i * 3600000 + Math.floor(Math.random() * 1800000)), // 随机分布在过去几小时内
        board: boardKey,
        isAI: true,
        comments: []
      };
    });

    forumPostsByBoard[boardKey] = finalPosts;
    await saveToStorage(`FORUM_POSTS_${boardKey}`, JSON.stringify(finalPosts));
    
    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('✅ 刷新成功，正在生成现场讨论...');
    
    // Generate initial comments for each post
    for (const post of finalPosts) {
      generateInitialCommentsForPost(post, cfg, board);
    }
"""

content = content.replace(refresh_forum_board_old, refresh_forum_board_new)

# Update publishForumPost to generate initial comments
publish_forum_post_old = """  const newPost = {
    id: Date.now().toString() + Math.floor(Math.random()*1000),
    authorName: authorName,
    avatar: currentPostIdentity === 'user' ? userAvatar : 'clover.png',
    title: finalTitle,
    content: finalContent,
    time: Date.now(),
    board: currentForumBoard,
    comments: []
  };

  if (!forumPostsByBoard[currentForumBoard]) forumPostsByBoard[currentForumBoard] = [];
  forumPostsByBoard[currentForumBoard].unshift(newPost);

  await saveToStorage(`FORUM_POSTS_${currentForumBoard}`, JSON.stringify(forumPostsByBoard[currentForumBoard]));

  document.getElementById('postForumTitle').value = '';
  document.getElementById('postForumContent').value = '';
  closeSub('post-forum-page');

  if (document.getElementById(board.pageId || '').classList.contains('show')) {
    renderForumBoard(currentForumBoard);
  }

  showToast('✅ 发帖成功！正在刷新列表...');
  // 滚动到新帖子位置逻辑在 renderForumBoard 中自动处理
}"""

publish_forum_post_new = """  const newPost = {
    id: Date.now().toString() + Math.floor(Math.random()*1000),
    authorName: authorName,
    avatar: currentPostIdentity === 'user' ? userAvatar : 'clover.png',
    title: finalTitle,
    content: finalContent,
    time: Date.now(),
    board: currentForumBoard,
    comments: []
  };

  if (!forumPostsByBoard[currentForumBoard]) forumPostsByBoard[currentForumBoard] = [];
  forumPostsByBoard[currentForumBoard].unshift(newPost);

  await saveToStorage(`FORUM_POSTS_${currentForumBoard}`, JSON.stringify(forumPostsByBoard[currentForumBoard]));

  document.getElementById('postForumTitle').value = '';
  document.getElementById('postForumContent').value = '';
  closeSub('post-forum-page');

  if (document.getElementById(board.pageId || '').classList.contains('show')) {
    renderForumBoard(currentForumBoard);
  }

  showToast('✅ 发帖成功！正在生成现场讨论...');
  
  // Generate initial comments for user post
  generateInitialCommentsForPost(newPost, cfg, board);
}"""

content = content.replace(publish_forum_post_old, publish_forum_post_new)

# Add generateInitialCommentsForPost function
initial_comments_fn = """
// 核心：生成动态帖子的初始评论链
async function generateInitialCommentsForPost(post, cfg, board) {
  if (!cfg || !cfg.key || !cfg.url || !cfg.model) return;
  
  // 准备角色池
  const eligibleContacts = contacts.filter(c => !c.isGroup);
  
  // 随机挑选 4-5 个角色作为评论者
  const count = Math.floor(Math.random() * 2) + 4; // 4-5条
  const selected = [...eligibleContacts].sort(() => Math.random() - 0.5).slice(0, count);
  
  const interactionPrompt = `你现在是论坛互动模块（模块A）。请根据以下帖子内容，同步生成一个包含 ${count} 条评论的初始讨论现场。
【帖子标题】${post.title}
【帖子正文】${post.content}
【楼主】${post.authorName}
【所属板块】${board.name}
【板块规则】${board.rules}

可用身份列表：
${selected.map((c, i) => `${i+1}. 姓名: ${c.name}, 设定: ${c.persona}`).join('\\n')}
(若身份不足，请自行生成具有真实感的网友昵称)

任务要求：
1. 评论必须由上面提供的身份发出，形成一个有逻辑的对话链。
2. 必须包含直接回复楼主的评论（引爆话题），以及NPC之间的互相回复（观点交锋与扩散）。
3. 评论之间可以有引用、回复、追问、调侃。
4. 所有评论必须高度契合主帖内容、符合发言者人设、并提供信息增量，杜绝“已阅”、“666”等无效回复。
5. 必须返回 JSON 数组格式：[{"authorName": "姓名", "content": "评论内容", "isInteraction": true}, ...]。严禁返回其他文字。
6. 字数每条在 30 字以内。`;

  try {
    const res = await fetch(`${cfg.url}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${cfg.key}` },
      body: JSON.stringify({
        model: cfg.model,
        temperature: 0.8,
        messages: [{ role: 'user', content: interactionPrompt }]
      })
    });
    const data = await res.json();
    let rawText = data.choices?.[0]?.message?.content || "";
    
    // 提取 JSON
    rawText = rawText.replace(/[\\u200B-\\u200D\\uFEFF]/g, "").trim();
    if (rawText.includes("```")) {
      const match = rawText.match(/\\[[\\s\\S]*\\]/);
      if (match) rawText = match[0];
    }
    const aiRes = JSON.parse(rawText);
    
    if (Array.isArray(aiRes)) {
      aiRes.forEach((item, i) => {
        post.comments.push({
          id: (Date.now() + i + 1).toString(),
          authorName: item.authorName,
          content: item.content,
          time: Date.now() + (i + 1) * 1000,
          isInteraction: item.isInteraction || false
        });
      });
      
      await saveToStorage(`FORUM_POSTS_${post.board}`, JSON.stringify(forumPostsByBoard[post.board]));
      
      // 更新 UI
      if (document.getElementById(board.pageId || '').classList.contains('show')) {
        renderForumBoard(post.board);
      }
      if (currentDetailPost && currentDetailPost.id === post.id) {
        renderForumComments();
      }
    }
  } catch (e) { console.error('生成初始评论链失败:', e); }
}
"""

if "generateInitialCommentsForPost" not in content:
    content = content.replace("async function triggerForumInteraction", initial_comments_fn + "\nasync function triggerForumInteraction")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied successfully.")
