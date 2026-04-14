$filePath = 'c:\Users\Administrator\Desktop\111\index.html'
$bytes = [System.IO.File]::ReadAllBytes($filePath)
$content = [System.Text.Encoding]::UTF8.GetString($bytes)

# Line 1137 (index 1136) contains emojiPickerPanel with the double display bug
# Strategy: find the emojiPickerPanel div and fix it by replacing the duplicate display property
# The problematic pattern: "z-index:999; display:flex; flex-direction:column"
# Should be: "z-index:999; flex-direction:column"

$old = 'z-index:999; display:flex; flex-direction:column'
$new = 'z-index:999; flex-direction:column'

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    $outBytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    [System.IO.File]::WriteAllBytes($filePath, $outBytes)
    Write-Host "SUCCESS"
} else {
    Write-Host "NOT_FOUND"
    # Try to find and show what's around emojiPickerPanel
    $idx = $content.IndexOf('emojiPickerPanel')
    if ($idx -ge 0) {
        Write-Host "emojiPickerPanel found at $idx"
    }
}
