$filePath = 'c:\Users\Administrator\Desktop\111\index.html'
$bytes = [System.IO.File]::ReadAllBytes($filePath)
$content = [System.Text.Encoding]::UTF8.GetString($bytes)

$old = '  <script src="js/main.js"></script>'
$new = '  <script src="js/main.js"></script>' + "`n" + '  <script src="js/chat-features.js"></script>'

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    $outBytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    [System.IO.File]::WriteAllBytes($filePath, $outBytes)
    Write-Host "SUCCESS: chat-features.js has been added to index.html"
} else {
    Write-Host "ERROR: Could not find target string"
    # Debug: find where main.js reference is
    $idx = $content.IndexOf('main.js')
    if ($idx -ge 0) {
        Write-Host "main.js found at index $idx"
        Write-Host "Context: " + $content.Substring([Math]::Max(0, $idx-15), 60)
    }
}
