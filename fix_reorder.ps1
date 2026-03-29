$file = 'c:\Users\Administrator\Desktop\111\index.html'
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

# Current order (0-indexed):
# 4363: 地点 (location)
# 4364: 心声 (thoughts)  
# 4365: 心情 (mood)
# 4366: 好感度 (favor)

# Target order:
# 4363: 心声 (thoughts)   <- move from 4364
# 4364: 地点 (location)   <- move from 4363
# 4365: 心情 (mood)       <- stays
# 4366: 好感度 (favor)    <- stays

Write-Output ("Before:")
Write-Output ("4363: " + $lines[4363].Substring(0, [Math]::Min(80, $lines[4363].Length)))
Write-Output ("4364: " + $lines[4364].Substring(0, [Math]::Min(80, $lines[4364].Length)))

$locationLine = $lines[4363]
$thoughtsLine = $lines[4364]

# Swap location and thoughts
$lines[4363] = $thoughtsLine
$lines[4364] = $locationLine

Write-Output ("After:")
Write-Output ("4363: " + $lines[4363].Substring(0, [Math]::Min(80, $lines[4363].Length)))
Write-Output ("4364: " + $lines[4364].Substring(0, [Math]::Min(80, $lines[4364].Length)))

[System.IO.File]::WriteAllLines($file, $lines, (New-Object System.Text.UTF8Encoding $false))
Write-Output "Saved!"
