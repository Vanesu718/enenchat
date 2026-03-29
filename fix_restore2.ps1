$file = 'c:\Users\Administrator\Desktop\111\index.html'
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

# Restore lines 4364 (thoughts/心声) and 4365 (mood/心情) with correct content
# Using surrogate pairs for emoji: 💭 = U+1F4AD, 😊 = U+1F60A

# 💭 surrogate pair: 0xD83D 0xDCAD
$thoughtsEmoji = [char]0xD83D + [char]0xDCAD
# 😊 surrogate pair: 0xD83D 0xDE0A  
$moodEmoji = [char]0xD83D + [char]0xDE0A

# Chinese chars
$xin = [char]0x5FC3   # 心
$sheng = [char]0x58F0 # 声
$qing = [char]0x60C5  # 情
$mei = [char]0x6CA1   # 没
$you = [char]0x6709   # 有
$xiang = [char]0x60F3 # 想
$fa = [char]0x6CD5    # 法
$ping = [char]0x5E73  # 平
$jing = [char]0x9759  # 静

$thoughtsLine = '          <div class="bc-status-item thoughts"><div class="bc-label">' + $thoughtsEmoji + ' ' + $xin + $sheng + '</div><div class="bc-val">${(statusData?.thoughts || ' + [char]39 + $mei + $you + $xiang + $fa + [char]39 + ').substring(0,10)}</div></div>'

$moodLine = '          <div class="bc-status-item"><div class="bc-label">' + $moodEmoji + ' ' + $xin + $qing + '</div><div class="bc-val">${(statusData?.mood || ' + [char]39 + $ping + $jing + [char]39 + ').substring(0,10)}</div></div>'

Write-Output ("thoughtsLine built, length: " + $thoughtsLine.Length)
Write-Output ("moodLine built, length: " + $moodLine.Length)

$lines[4364] = $thoughtsLine
$lines[4365] = $moodLine

[System.IO.File]::WriteAllLines($file, $lines, (New-Object System.Text.UTF8Encoding $false))
Write-Output "Saved!"

$v = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)
Write-Output ("4364 len: " + $v[4364].Length)
Write-Output ("4365 len: " + $v[4365].Length)
Write-Output ("4364 has thoughts: " + ($v[4364] -match 'thoughts'))
Write-Output ("4365 has mood: " + ($v[4365] -match 'mood'))
Write-Output ("4364 has substring: " + ($v[4364] -match 'substring'))
Write-Output ("4365 has substring: " + ($v[4365] -match 'substring'))
