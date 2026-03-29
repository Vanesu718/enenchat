$file = 'c:\Users\Administrator\Desktop\111\index.html'
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

Write-Output ("Total lines: " + $lines.Length)
Write-Output ("Line 4363: " + $lines[4363])
Write-Output ("Line 4364: '" + $lines[4364] + "'")
Write-Output ("Line 4365: '" + $lines[4365] + "'")
Write-Output ("Line 4366: " + $lines[4366])

# Lines 4364 and 4365 are empty - restore them with correct content (swapped + 10 char limit)
# The correct order after swap should be:
# 4363: 地点 (location) - already correct
# 4364: 心声 (thoughts) - was emptied, needs to be restored
# 4365: 心情 (mood) - was emptied, needs to be restored  
# 4366: 好感度 (favor) - already correct

# Build the thoughts line (心声) with 10-char limit
# 💭 心声
$thoughtsLine = '          <div class="bc-status-item thoughts"><div class="bc-label">' + [char]0x1F4AD + ' ' + [char]0x5FC3 + [char]0x58F0 + '</div><div class="bc-val">${(statusData?.thoughts || ' + [char]39 + [char]0x6CA1 + [char]0x6709 + [char]0x60F3 + [char]0x6CD5 + [char]39 + ').substring(0,10)}</div></div>'

# Build the mood line (心情) with 10-char limit
# 😊 心情
$moodLine = '          <div class="bc-status-item"><div class="bc-label">' + [char]0x1F60A + ' ' + [char]0x5FC3 + [char]0x60C5 + '</div><div class="bc-val">${(statusData?.mood || ' + [char]39 + [char]0x5E73 + [char]0x9759 + [char]39 + ').substring(0,10)}</div></div>'

Write-Output ("New thoughts line: " + $thoughtsLine.Substring(0, [Math]::Min(100, $thoughtsLine.Length)))
Write-Output ("New mood line: " + $moodLine.Substring(0, [Math]::Min(100, $moodLine.Length)))

$lines[4364] = $thoughtsLine
$lines[4365] = $moodLine

[System.IO.File]::WriteAllLines($file, $lines, (New-Object System.Text.UTF8Encoding $false))
Write-Output "File saved!"

# Verify
$verifyLines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)
Write-Output ("Verify 4364: " + $verifyLines[4364].Substring(0, [Math]::Min(100, $verifyLines[4364].Length)))
Write-Output ("Verify 4365: " + $verifyLines[4365].Substring(0, [Math]::Min(100, $verifyLines[4365].Length)))
