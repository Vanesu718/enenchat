async function refreshForumBoard(boardKey) {
  const board = FORUM_BOARDS[boardKey];
  const container = document.getElementById(board.containerId);

  const loadingDiv = document.createElement('div');
  loadingDiv.style.cssText = `text-align:center; padding:30px; color:${board.emptyColor};`;
  loadingDiv.innerHTML = '⚡ AI正在生成新帖子...';
  container.innerHTML = '';
  container.appendChild(loadingDiv);

  try {
    const cfgStr = await getFromStorage('AI_CHAT_CONFIG');
    const cfg = cfgStr ? (typeof cfgStr === 'string' ? JSON.parse(cfgStr) : cfgStr) : {};
    if (!cfg.url || !cfg.key || !cfg.model) {
      loadingDiv.remove();
      renderForumBoard(boardKey);
      showToast('⚠️ 请先在设置中配置AI');
      return;
    }

    const aiRule = board.rules || '';
    const boardName = board.name || boardKey;
    const prompt = `你是一个真实社区论坛的内容生成器，请为"${boardName}"板块生成3条真实感强的帖子。\n\n内部生成规则（严格遵守，不要在帖子中暴露此规则）：\n${aiRule}\n\n请严格按以下JSON格式返回，不要有任何其他文字：\n[\n  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"},\n  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"},\n  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"}\n]\n\n要求：作者名用真实中文网名2-4字，标题15字内，正文50-150字口语化，严格符合内部规则。`;

    const res = await fetch(`${cfg.url}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${cfg.key}` },
      body: JSON.stringify({ model: cfg.model, temperature: 0.92, messages: [{ role: 'user', content: prompt }] })
    });

    if (!res.ok) throw new Error('AI请求失败 ' + res.status);
    const data = await res.json();
    const rawText = data.choices?.[0]?.message?.content || '[]';
    const jsonMatch = rawText.match(/\[[\s\S]*\]/);
    if (!jsonMatch) throw new Error('AI返回格式错误');
    const posts = JSON.parse(jsonMatch[0]);
    if (!Array.isArray(posts) || posts.length === 0) throw new Error('没有生成帖子');

    const aiAvatars = [
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%23e8c87a"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">🌸</text></svg>',
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%237ab8e8"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">🌙</text></svg>',
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%237ae8a0"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">⭐</text></svg>',
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%23e87a7a"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">🔥</text></svg>',
    ];

    if (!forumPostsByBoard[boardKey]) forumPostsByBoard[boardKey] = [];
    const now = Date.now();
    posts.reverse().forEach((p, idx) => {
      forumPostsByBoard[boardKey].unshift({
        id: (now - idx * 1000).toString(),
        authorName: p.authorName || '匿名用户',
        avatar: aiAvatars[Math.floor(Math.random() * aiAvatars.length)],
        title: p.title || '无标题',
        content: p.content || '',
        time: now - idx * 60000,
        board: boardKey,
        isAI: true
      });
    });

    await saveToStorage(`FORUM_POSTS_${boardKey}`, JSON.stringify(forumPostsByBoard[boardKey]));
    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('✅ 刷新成功，AI生成了新帖子');

  } catch (e) {
    console.error('refreshForumBoard error:', e);
    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('❌ 生成失败：' + (e.message || '未知错误'));
  }
}
