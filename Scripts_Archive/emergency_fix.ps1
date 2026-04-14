$mainJsPath = "js/main.js"
$chatCssPath = "css/chat.css"

# 1. Fix js/main.js
if (Test-Path $mainJsPath) {
    $content = Get-Content $mainJsPath -Raw -Encoding UTF8
    
    # Use regex to find and replace the garbled text inside the msg-menu-item.
    # We replace any non-tag text inside the reply div with "回复"
    $pattern1 = '(<div class="msg-menu-item" onclick="replyToMsg\([^>]+\)[^>]*>)[^<]+(<\/div>)'
    $content = [regex]::Replace($content, $pattern1, '${1}回复$2')
    
    $pattern2 = '(data-reply-text="\$\{replyText\}">)[^<]+(<\/div>)'
    $content = [regex]::Replace($content, $pattern2, '${1}回复$2')

    Set-Content -Path $mainJsPath -Value $content -Encoding UTF8
    Write-Host "Fixed js/main.js"
}

# 2. Fix css/chat.css
if (Test-Path $chatCssPath) {
    $cssContent = Get-Content $chatCssPath -Raw -Encoding UTF8
    if (-not $cssContent.Contains("/* 移动端防误触 */")) {
        $cssContent += @"

/* 移动端防误触 */
@media (hover: none) and (pointer: coarse) {
  .msg-menu {
    display: none !important;
  }
  .msg-row {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
  }
  .msg-content {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
  }
}
"@
        Set-Content -Path $chatCssPath -Value $cssContent -Encoding UTF8
        Write-Host "Fixed css/chat.css"
    }
}
