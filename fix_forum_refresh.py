#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复论坛两个问题：
1. 发帖须知不应显示给用户（是AI生成帖子时参考的内部指令）
2. 刷新按钮应调用AI生成新帖子，而不只是重新渲染
"""

with open('c:/Users/Administrator/Desktop/111/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

total = len(lines)
print(f"文件共 {total} 行")

# ========== 修复1: 删除 openCustomForumBoard 中显示 rulesEl 的代码 ==========
# 找到 "// 更新板块须知" 相关行（在 openCustomForumBoard 函数内）
# 根据搜索结果，该代码在约 9085-9099 行
for i in range(9060, 9110):
    if i < total and '板块须知' in lines[i] and 'rulesEl' not in lines[i]:
        print(f"找到板块须知注释在第 {i+1} 行: {lines[i].rstrip()}")
        # 找到注释的起始位置，删除注释和接下来的 if 块（共约8行）
        start = i
        # 找结束位置：下一个 if (rulesEl) 块的结束
        j = i + 1
        while j < total and '}' not in lines[j]:
            j += 1
        end = j + 1  # 包含关闭括号那行
        print(f"删除第 {start+1} 到 {end} 行（板块须知显示代码）")
        # 替换为注释
        lines[start:end] = ['  // 发帖须知仅供AI使用，不在UI中展示\n']
        break

# ========== 修复2: 删除 openPostForumPage 中的 rulesEl 显示 ==========
# 找到 post-forum-rules 相关的 if (rulesEl) 块
for i in range(9265, 9295):
    if i < total and 'rulesEl' in lines[i] and 'innerHTML' in lines[i] and 'board.rules' in lines[i]:
        print(f"找到 rulesEl innerHTML 在第 {i+1} 行")
        # 往上找 if (rulesEl) 开始
        start = i - 1
        while start > 0 and 'if (rulesEl)' not in lines[start]:
            start -= 1
        end = i + 2  # 包含 } 那行
        print(f"删除第 {start+1} 到 {end} 行（发帖页面须知显示代码）")
        lines[start:end] = []
        break

# ========== 修复3: 重写 refreshForumBoard 函数（调用AI生成帖子）==========
# 找到 refreshForumBoard 函数
refresh_start = -1
refresh_end = -1
for i in range(9200, 9270):
    if i < total and 'async function refreshForumBoard' in lines[i]:
        refresh_start = i
        print(f"找到 refreshForumBoard 函数在第 {i+1} 行")
        break

if refresh_start >= 0:
    # 找函数结束（下一个以 // 或 function 开头的行，或第一个空行后的函数定义）
    brace_count = 0
    for i in range(refresh_start, refresh_start + 50):
        if i >= total:
            break
        for ch in lines[i]:
            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
        if brace_count == 0 and i > refresh_start:
            refresh_end = i + 1
            break
    
    if refresh_end > refresh_start:
        print(f"refreshForumBoard 函数范围：第 {refresh_start+1} 到 {refresh_end} 行")
        
        # 新的 refreshForumBoard 实现（带AI生成帖子）
        new_refresh = '''async function refreshForumBoard(boardKey) {
  const board = FORUM_BOARDS[boardKey];
  const container = document.getElementById(board.containerId);

  // 显示加载提示
  const loadingDiv = document.createElement('div');
  loadingDiv.style.cssText = `text-align:center; padding:30px; color:${board.emptyColor};`;
  loadingDiv.innerHTML = '⚡ AI正在生成新帖子...';
  container.innerHTML = '';
  container.appendChild(loadingDiv);

  try {
    // 读取AI配置
    const cfgStr = await getFromStorage('AI_CHAT_CONFIG');
    const cfg = cfgStr ? (typeof cfgStr === 'string' ? JSON.parse(cfgStr) : cfgStr) : {};
    if (!cfg.url || !cfg.key || !cfg.model) {
      loadingDiv.remove();
      renderForumBoard(boardKey);
      showToast('⚠️ 请先在设置中配置AI');
      return;
    }

    // 构建prompt（发帖须知作为AI内部指令）
    const aiRule = board.rules || '';
    const boardName = board.name || boardKey;
    const prompt = `你是一个真实社区论坛的内容生成器，请为"${boardName}"板块生成3条真实感强的帖子。

内部生成规则（严格遵守，不要暴露给用户）：
${aiRule}

请严格按以下JSON格式返回，不要有任何其他文字：
[
  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"},
  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"},
  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"}
]

要求：
- 作者名用真实感的中文网名（2-4字）
- 标题简洁有力，15字以内
- 正文自然口语化，50-150字，像真人发帖
- 严格符合上述内部规则`;

    const res = await fetch(`${cfg.url}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${cfg.key}` },
      body: JSON.stringify({
        model: cfg.model,
        temperature: 0.92,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    if (!res.ok) throw new Error('AI请求失败');

    const data = await res.json();
    const rawText = data.choices?.[0]?.message?.content || '[]';

    // 解析JSON（提取JSON数组）
    const jsonMatch = rawText.match(/\[[\s\S]*\]/);
    if (!jsonMatch) throw new Error('AI返回格式错误');
    const posts = JSON.parse(jsonMatch[0]);

    if (!Array.isArray(posts) || posts.length === 0) throw new Error('没有生成帖子');

    // 随机头像列表
    const aiAvatars = [
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%23e8c87a"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">🌸</text></svg>',
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%237ab8e8"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">🌙</text></svg>',
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%237ae8a0"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">⭐</text></svg>',
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%23e87a7a"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">🔥</text></svg>',
      'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="%23c07ae8"/><text x="50%25" y="55%25" text-anchor="middle" dominant-baseline="middle" font-size="18" fill="%23333">💫</text></svg>',
    ];

    // 把AI生成的帖子加入到帖子列表（插入到最前面）
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

    // 保存到存储
    await saveToStorage(`FORUM_POSTS_${boardKey}`, JSON.stringify(forumPostsByBoard[boardKey]));

    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('✅ 已刷新，AI生成了新帖子');

  } catch (e) {
    console.error('refreshForumBoard AI error:', e);
    loadingDiv.remove();
    renderForumBoard(boardKey);
    showToast('❌ 生成失败：' + (e.message || '未知错误'));
  }
}
'''
        lines[refresh_start:refresh_end] = [new_refresh]
        print(f"refreshForumBoard 函数已替换为AI生成版本")
    else:
        print("ERROR: 找不到 refreshForumBoard 函数结束位置")
else:
    print("ERROR: 找不到 refreshForumBoard 函数")

# 写回文件
with open('c:/Users/Administrator/Desktop/111/index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ 修复完成！")
print("修改内容：")
print("1. 删除了 openCustomForumBoard 中显示发帖须知的代码（发帖须知仅供AI内部使用）")
print("2. 删除了 openPostForumPage 中显示板块规则的代码")
print("3. 重写了 refreshForumBoard 函数，现在会调用AI生成真实感帖子")
