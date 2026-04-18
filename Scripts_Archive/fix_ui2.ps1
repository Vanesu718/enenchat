$path = "js/main.js"
$content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

$content = $content.Replace("?? 已赞", "💖 已赞")
$content = $content.Replace("?? 赞", "👍 赞")
$content = $content.Replace("?? 评论", "💬 评论")
$content = $content.Replace("??? 删除", "🗑️ 删除")
$content = $content.Replace("?? ' + moment.likes", "👍 ' + moment.likes")
$content = $content.Replace("emoji: '??'", "emoji: '🎪'")
$content = $content.Replace("emoji: '???'", "emoji: '🗣️'")
$content = $content.Replace("emoji: '??'", "emoji: '👻'")
$content = $content.Replace("<span>??</span>", "<span>🔥</span>")
$content = $content.Replace("?? '", "👍 '")
$content = $content.Replace("?? 默认", "📁 默认")
$content = $content.Replace("默认 (?)", "默认")
$content = $content.Replace("|| '??'", "|| '📁'")

$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
[System.IO.File]::WriteAllBytes($path, $bytes)
Write-Host "Replacement done."
