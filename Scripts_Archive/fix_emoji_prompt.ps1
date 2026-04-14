$filePath = 'c:\Users\Administrator\Desktop\111\js\main.js'
$bytes = [System.IO.File]::ReadAllBytes($filePath)
$content = [System.Text.Encoding]::UTF8.GetString($bytes)

# We need to inject after systemPrompt is fully built, before messages array
# Target: the line "    const messages = [{ role: 'system', content: systemPrompt }];"
$old = '    const messages = [{ role: ''system'', content: systemPrompt }];'
$new = '    // Inject AI Emoji prompt addon if enabled
    if (typeof getAiEmojiPromptAddon === ''function'') {
        systemPrompt += getAiEmojiPromptAddon();
    }
    const messages = [{ role: ''system'', content: systemPrompt }];'

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    $outBytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    [System.IO.File]::WriteAllBytes($filePath, $outBytes)
    Write-Host "SUCCESS: AI Emoji prompt addon injected into main.js"
} else {
    Write-Host "ERROR: Could not find target in main.js"
    $idx = $content.IndexOf('role: ''system''')
    if ($idx -ge 0) {
        Write-Host "Found 'role: system' at index $idx"
        Write-Host $content.Substring([Math]::Max(0, $idx-50), 100)
    }
}
