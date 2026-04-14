$indexContent = Get-Content "index.html" -Raw -Encoding UTF8
$indexContent = $indexContent -replace '🔄 刷新', '<img src="ICON/刷新.png" style="width:18px;height:18px;vertical-align:middle;"> 刷新'
Set-Content "index.html" -Value $indexContent -Encoding UTF8

$mainContent = Get-Content "js/main.js" -Raw -Encoding UTF8
$mainContent = $mainContent -replace 'ICON/点赞前\.png', 'ICON/点赞.png'
$mainContent = $mainContent -replace 'ICON/更多\.png', 'ICON/删除.png'
Set-Content "js/main.js" -Value $mainContent -Encoding UTF8
