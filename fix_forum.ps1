# fix_forum.ps1 - 修复论坛刷新和发帖须知问题

$filePath = 'c:\Users\Administrator\Desktop\111\index.html'
$enc = [System.Text.Encoding]::UTF8
$lines = [System.IO.File]::ReadAllLines($filePath, $enc)
Write-Host "文件共 $($lines.Count) 行"

# ========== 找各关键行号 ==========

# 找 refreshForumBoard 函数起始行
$refreshStart = -1
for ($i = 9200; $i -lt 9270; $i++) {
    if ($lines[$i] -match 'async function refreshForumBoard') {
        $refreshStart = $i
        Write-Host "找到 refreshForumBoard 在第 $($i+1) 行"
        break
    }
}

# 找 refreshForumBoard 函数结束行（匹配大括号）
$refreshEnd = -1
if ($refreshStart -ge 0) {
    $depth = 0
    for ($i = $refreshStart; $i -lt ($refreshStart + 60); $i++) {
        foreach ($ch in $lines[$i].ToCharArray()) {
            if ($ch -eq '{') { $depth++ }
            elseif ($ch -eq '}') { $depth-- }
        }
        if ($depth -eq 0 -and $i -gt $refreshStart) {
            $refreshEnd = $i
            Write-Host "refreshForumBoard 结束在第 $($i+1) 行"
            break
        }
    }
}

# 找 openPostForumPage 里显示 board.rules 的 if(rulesEl) 块
$rulesStart = -1
$rulesEnd = -1
for ($i = 9260; $i -lt 9310; $i++) {
    if ($lines[$i] -match 'if \(rulesEl\)') {
        $rulesStart = $i
        Write-Host "找到 if(rulesEl) 在第 $($i+1) 行"
        # 找结束 }
        for ($j = $i+1; $j -lt ($i+15); $j++) {
            if ($lines[$j].Trim() -eq '}') {
                $rulesEnd = $j
                Write-Host "if(rulesEl) 块结束在第 $($j+1) 行"
                break
            }
        }
        break
    }
}

# 找 openCustomForumBoard 里的 // 更新板块须知 注释
$customRulesStart = -1
$customRulesEnd = -1
for ($i = 9060; $i -lt 9110; $i++) {
    if ($lines[$i] -match '板块须知' -and $lines[$i] -match '//') {
        $customRulesStart = $i
        Write-Host "找到 openCustomForumBoard 板块须知 在第 $($i+1) 行"
        # 找下一个 if(rulesEl) 块的结束
        for ($j = $i+1; $j -lt ($i+20); $j++) {
            if ($lines[$j].Trim() -eq '}') {
                $customRulesEnd = $j
                Write-Host "openCustomForumBoard rulesEl 块结束在第 $($j+1) 行"
                break
            }
        }
        break
    }
}

# ========== 执行修改（从后往前，避免行号偏移）==========

$linesList = [System.Collections.Generic.List[string]]::new($lines)

# 1. 先替换 refreshForumBoard 函数（行号最大，先改）
if ($refreshStart -ge 0 -and $refreshEnd -ge $refreshStart) {
    $newRefresh = @'
async function refreshForumBoard(boardKey) {
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

    // 构建prompt（发帖须知作为AI内部指令，不展示给用户）
    const aiRule = board.rules || '';
    const boardName = board.name || boardKey;
    const prompt = `你是一个真实社区论坛的内容生成器，请为"${boardName}"板块生成3条真实感强的帖子。\n\n内部生成规则（严格遵守）：\n${aiRule}\n\n请严格按以下JSON格式返回，不要有任何其他文字：\n[\n  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"},\n  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"},\n  {"authorName": "用户昵称", "title": "帖子标题", "content": "帖子正文内容"}\n]\n\n要求：作者名用真实中文网名2-4字，标题15字内，正文50-150字口语化，严格符合内部规则。`;

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
'@
    # 删除原函数行并插入新函数
    $linesList.RemoveRange($refreshStart, $refreshEnd - $refreshStart + 1)
    $linesList.Insert($refreshStart, $newRefresh)
    Write-Host "✅ 已替换 refreshForumBoard 函数"
}

# 2. 删除 openPostForumPage 中的 if(rulesEl) 块（行号在 refreshForumBoard 之前，但要考虑前面的删除可能影响行号）
# 由于我们已经在 refreshStart 之后的区域替换了，rulesStart < refreshStart，行号不受影响
if ($rulesStart -ge 0 -and $rulesEnd -ge $rulesStart) {
    $count = $rulesEnd - $rulesStart + 1
    $linesList.RemoveRange($rulesStart, $count)
    Write-Host "✅ 已删除 openPostForumPage 中 if(rulesEl) 块（$($rulesStart+1) 到 $($rulesEnd+1) 行）"
}

# 3. 删除 openCustomForumBoard 中的板块须知显示代码
if ($customRulesStart -ge 0 -and $customRulesEnd -ge $customRulesStart) {
    $count = $customRulesEnd - $customRulesStart + 1
    $linesList.RemoveRange($customRulesStart, $count)
    $linesList.Insert($customRulesStart, '  // 发帖须知仅供AI内部使用，不在UI中展示')
    Write-Host "✅ 已删除 openCustomForumBoard 中板块须知显示代码"
}

# 写回文件
[System.IO.File]::WriteAllLines($filePath, $linesList.ToArray(), $enc)
Write-Host "`n✅ 修复完成！文件已保存，共 $($linesList.Count) 行"
