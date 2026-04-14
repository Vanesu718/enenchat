$filePath = 'c:\Users\Administrator\Desktop\111\index.html'
$bytes = [System.IO.File]::ReadAllBytes($filePath)
$content = [System.Text.Encoding]::UTF8.GetString($bytes)

# The bug: style has both display:none AND display:flex - the latter overrides the former
# Fix: remove the second display:flex, keep only flex-direction:column
$old = 'id="emojiPickerPanel" style="display:none; position:absolute; bottom:60px; left:0; width:100%; background:var(--bg-cream); border-top-left-radius:16px; border-top-right-radius:16px; box-shadow:0 -4px 16px rgba(0,0,0,0.1); z-index:999; display:flex; flex-direction:column; height:300px; transition:transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); transform:translateY(100%);"'
$new = 'id="emojiPickerPanel" style="display:none; position:absolute; bottom:60px; left:0; width:100%; background:var(--bg-cream); border-top-left-radius:16px; border-top-right-radius:16px; box-shadow:0 -4px 16px rgba(0,0,0,0.1); z-index:999; flex-direction:column; height:300px; transition:transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); transform:translateY(100%);"'

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    $outBytes = [System.Text.Encoding]::UTF8.GetBytes($content)
    [System.IO.File]::WriteAllBytes($filePath, $outBytes)
    Write-Host "SUCCESS: Fixed emojiPickerPanel display conflict"
} else {
    Write-Host "ERROR: Target string not found"
}
