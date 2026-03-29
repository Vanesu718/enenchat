$f = 'c:\Users\Administrator\Desktop\111\index.html'
$c = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)

# 要替换的旧内容：从注释行到 styleEl.innerHTML 赋值结束
# 用能精确匹配的字符串片段
$oldPart = "  styleEl.innerHTML = `"``n    @font-face {``n      font-family: 'MyCustomFont';``n      src: url('`${fontUrl}');"

# 检查是否找到
$idx = $c.IndexOf("src: url('`${fontUrl}');")
Write-Host "src url line position: $idx"

if ($idx -ge 0) {
    # 找到包含 src: url 的那一行，往前找 styleEl.innerHTML 开始位置
    $startSearch = [Math]::Max(0, $idx - 200)
    $snippet = $c.Substring($startSearch, 300)
    Write-Host "Snippet around match:"
    Write-Host $snippet
} else {
    Write-Host "NOT FOUND - checking what's in file..."
    $funcIdx = $c.IndexOf('async function applyCustomFont')
    Write-Host "async func at: $funcIdx"
    if ($funcIdx -ge 0) {
        Write-Host $c.Substring($funcIdx, 600)
    }
}
