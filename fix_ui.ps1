$content = Get-Content -Path "js\main.js" -Encoding UTF8
$content = $content -replace "\?\? 已赞", "💖 已赞"
$content = $content -replace "\?\? 赞", "👍 赞"
$content = $content -replace "\?\? 评论", "💬 评论"
$content = $content -replace "\?\?\? 删除", "🗑️ 删除"
$content = $content -replace "\? 默认", "📁 默认"
$content = $content -replace "默认 \(\?\)", "默认"

Set-Content -Path "js\main.js" -Value $content -Encoding UTF8
Write-Host "Done replacing in main.js"
