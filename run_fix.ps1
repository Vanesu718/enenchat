
$content = [IO.File]::ReadAllText("$PWD\js\main.js", [System.Text.Encoding]::UTF8)

$evaluator = [MatchEvaluator]{
    param($match)
    $prefix = $match.Groups[1].Value
    $ahead = $match.Groups[2].Value
    
    $emoji = "✅"
    if ($ahead -match "失败|不正确|错误|不是有效|严重不足|异常") { $emoji = "❌" }
    elseif ($ahead -match "不足|超过|为空|不支持|未加载|格式不正确|必须|警告|请先") { $emoji = "⚠️" }
    elseif ($ahead -match "AI|智能|提炼|构思|提取|回忆") { $emoji = "✨" }
    elseif ($ahead -match "正在|请稍候|稍等|打包") { $emoji = "⏳" }
    elseif ($ahead -match "删除|清空|清零|解除") { $emoji = "🗑️" }
    elseif ($ahead -match "求婚|结婚") { $emoji = "💍" }
    elseif ($ahead -match "图片|背景图|封面图") { $emoji = "🖼️" }
    elseif ($ahead -match "存储|容量|空间") { $emoji = "📦" }
    
    return "$prefix$emoji $ahead"
}

$newContent = [Regex]::Replace($content, "(['`"``])\s*(?:\?\?|\?)\s+([^'`"``\n]{1,20})", $evaluator)

$newContent = $newContent -replace "// \?\? ", "// ⚠️ "
$newContent = $newContent -replace "// \? ", "// ⚠️ "
$newContent = $newContent -replace "\?\? 情欲指数", "🔥 情欲指数"
$newContent = $newContent -replace "\?\? 这将同时删除", "⚠️ 这将同时删除"
$newContent = $newContent -replace "'\?\?\?'", "'📰'"
$newContent = $newContent -replace "'\?\?', name: '星海瞭望台'", "'🌟', name: '星海瞭望台'"
$newContent = $newContent -replace "'\?\?', name: '夜谈档案馆'", "'👻', name: '夜谈档案馆'"
$newContent = $newContent -replace "\['\?\?', '\?\?', '\?\?', '\?\?', '\?\?', '\?\?', '\?\?', '\?\?'\]", "['😀', '😂', '🥰', '😎', '🤔', '😭', '😡', '😴']"
$newContent = $newContent -replace "emoji: '\?\?\?'", "emoji: '📰'"
$newContent = $newContent -replace "emoji: '\?\?'", "emoji: '🌟'"
$newContent = $newContent -replace "<span>\?\?</span>", "<span>🔥</span>"
$newContent = $newContent -replace "\?\? 发帖须知", "📢 发帖须知"
$newContent = $newContent -replace "来了来了！\?\?", "来了来了！🏃"
$newContent = $newContent -replace "我们还是分开吧\.\.\.\?\?", "我们还是分开吧...💔"
$newContent = $newContent -replace "\?\? 我们还是分开吧", "💔 我们还是分开吧"
$newContent = $newContent -replace "\? \?\?: ", "❌ 错误: "
$newContent = $newContent -replace "\?\? 编辑", "✏️ 编辑"
$newContent = $newContent -replace "\? Word文档", "📄 Word文档"
$newContent = $newContent -replace "\\n\? \.txt", "\n📄 .txt"
$newContent = $newContent -replace "\\n\? \.docx", "\n📄 .docx"

[IO.File]::WriteAllText("$PWD\js\main.js", $newContent, [System.Text.Encoding]::UTF8)
Write-Host "js\main.js fixed"

$html = [IO.File]::ReadAllText("$PWD\index.html", [System.Text.Encoding]::UTF8)

$evaluatorHtml = [MatchEvaluator]{
    param($match)
    $prefix = $match.Groups[1].Value
    $ahead = $match.Groups[2].Value
    
    $emoji = "✅"
    if ($ahead -match "提取") { $emoji = "✨" }
    return "$prefix$emoji $ahead"
}

$newHtml = [Regex]::Replace($html, "(>)\s*(?:\?\?|\?)\s+([^<]{1,20})", $evaluatorHtml)
[IO.File]::WriteAllText("$PWD\index.html", $newHtml, [System.Text.Encoding]::UTF8)
Write-Host "index.html fixed"
