$file = 'c:\Users\Administrator\Desktop\111\index.html'
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

Write-Output ("Total lines: " + $lines.Length)

# Find lines with mood and thoughts
$moodIdx = -1
$thoughtsIdx = -1
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match 'bc-status-item' -and $lines[$i] -match 'statusData\?\.mood') {
        $moodIdx = $i
        Write-Output ("Found mood at index: " + $i)
    }
    if ($lines[$i] -match 'bc-status-item thoughts' -and $lines[$i] -match 'statusData\?\.thoughts') {
        $thoughtsIdx = $i
        Write-Output ("Found thoughts at index: " + $i)
    }
}

if ($moodIdx -ge 0 -and $thoughtsIdx -ge 0) {
    Write-Output ("Swapping lines " + $moodIdx + " and " + $thoughtsIdx)
    
    $moodLine = $lines[$moodIdx]
    $thoughtsLine = $lines[$thoughtsIdx]
    
    # Swap
    $lines[$moodIdx] = $thoughtsLine
    $lines[$thoughtsIdx] = $moodLine
    
    Write-Output ("After swap - line " + $moodIdx + ": " + $lines[$moodIdx].Substring(0, [Math]::Min(80, $lines[$moodIdx].Length)))
    Write-Output ("After swap - line " + $thoughtsIdx + ": " + $lines[$thoughtsIdx].Substring(0, [Math]::Min(80, $lines[$thoughtsIdx].Length)))
    
    [System.IO.File]::WriteAllLines($file, $lines, (New-Object System.Text.UTF8Encoding $false))
    Write-Output "Swap done and saved!"
} else {
    Write-Output ("moodIdx=" + $moodIdx + " thoughtsIdx=" + $thoughtsIdx + " - not found!")
}
