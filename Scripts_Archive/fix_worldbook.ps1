$content = [System.IO.File]::ReadAllText("c:\Users\Administrator\Desktop\111\index.html", [System.Text.Encoding]::UTF8)

# 1. Fix worldbook tabs - replace 语言规范 with 世界观 and add 其他
$oldTabs = @'
        <div class="wb-tab" onclick="filterWorldBook('语言规范')" data-category="语言规范" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">语言规范</div>
        <div class="wb-tab" onclick="filterWorldBook('html')" data-category="html" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">html</div>
'@

$newTabs = @'
        <div class="wb-tab" onclick="filterWorldBook('世界观')" data-category="世界观" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">世界观</div>
        <div class="wb-tab" onclick="filterWorldBook('其他')" data-category="其他" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">其他</div>
        <div class="wb-tab" onclick="filterWorldBook('html')" data-category="html" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">html</div>
'@

if ($content.Contains("filterWorldBook('语言规范')")) {
    $content = $content.Replace($oldTabs, $newTabs)
    Write-Host "Tab replacement done"
} else {
    Write-Host "Tab not found"
}

# 2. Fix worldbook-category select options
$oldCat = @'
            <option value="记忆总结">记忆总结</option>
            <option value="语言规范">语言规范</option>
            <option value="html">html</option>
'@

$newCat = @'
            <option value="记忆总结">记忆总结</option>
            <option value="世界观">世界观</option>
            <option value="其他">其他</option>
            <option value="html">html</option>
'@

if ($content.Contains('<option value="语言规范">语言规范</option>')) {
    $content = $content.Replace($oldCat, $newCat)
    Write-Host "Category select done"
} else {
    Write-Host "Category select not found"
}

# 3. Add 文风设置 to contacts menu
$oldMenu = @'
        <div class="menu-item" onclick="openSub('world-win')">世界书管理</div>
        <div class="menu-item" onclick="openSub('user-mask-setting')">用户面具设置</div>
'@

$newMenu = @'
        <div class="menu-item" onclick="openSub('world-win')">世界书管理</div>
        <div class="menu-item" onclick="openSub('writing-style-win')">文风设置</div>
        <div class="menu-item" onclick="openSub('user-mask-setting')">用户面具设置</div>
'@

if ($content.Contains("openSub('world-win')")) {
    $content = $content.Replace($oldMenu, $newMenu)
    Write-Host "Menu done"
} else {
    Write-Host "Menu not found"
}

[System.IO.File]::WriteAllText("c:\Users\Administrator\Desktop\111\index.html", $content, [System.Text.Encoding]::UTF8)
Write-Host "File written successfully"
