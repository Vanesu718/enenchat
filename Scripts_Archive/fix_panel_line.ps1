$filePath = 'c:\Users\Administrator\Desktop\111\index.html'
$bytes = [System.IO.File]::ReadAllBytes($filePath)
$content = [System.Text.Encoding]::UTF8.GetString($bytes)

# Split into lines
$lines = $content -split "`n"

# Find the line with emojiPickerPanel
$fixedCount = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'emojiPickerPanel' -and $lines[$i] -match 'display:flex') {
        # Fix the line: remove the second display:flex occurrence
        # Pattern: has display:none at start and display:flex later
        $original = $lines[$i]
        $fixed = $lines[$i] -replace 'z-index:999; display:flex; flex-direction:column', 'z-index:999; flex-direction:column'
        if ($fixed -ne $original) {
            $lines[$i] = $fixed
            $fixedCount++
            Write-Host "Fixed line $($i+1)"
        }
    }
}

if ($fixedCount -gt 0) {
    $newContent = $lines -join "`n"
    $outBytes = [System.Text.Encoding]::UTF8.GetBytes($newContent)
    [System.IO.File]::WriteAllBytes($filePath, $outBytes)
    Write-Host "SUCCESS: Fixed $fixedCount line(s)"
} else {
    Write-Host "NOT_FIXED - no matching lines found"
    # Debug: find lines with emojiPickerPanel
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match 'emojiPickerPanel') {
            Write-Host "Line $($i+1) has emojiPickerPanel"
            Write-Host $lines[$i].Substring(0, [Math]::Min(200, $lines[$i].Length))
        }
    }
}
