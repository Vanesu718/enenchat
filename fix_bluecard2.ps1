$file = 'c:\Users\Administrator\Desktop\111\index.html'
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

Write-Host "Total lines: $($lines.Length)"

# Lines are 0-indexed, so line 4361 = index 4360
# Line 4361 (0-indexed 4360): 地点
# Line 4362 (0-indexed 4361): 心情  <-- swap with line 4363
# Line 4363 (0-indexed 4362): 心声  <-- swap with line 4362
# Line 4364 (0-indexed 4363): 好感度

$line4360 = $lines[4360]
$line4361 = $lines[4361]  # 心情
$line4362 = $lines[4362]  # 心声 (thoughts)
$line4363 = $lines[4363]  # 好感度

Write-Host "Line 4361 (0-idx 4360): $line4360"
Write-Host "Line 4362 (0-idx 4361): $line4361"
Write-Host "Line 4363 (0-idx 4362): $line4362"
Write-Host "Line 4364 (0-idx 4363): $line4363"

# Check if line 4362 contains 'thoughts' (心声) and line 4361 contains 'mood' (心情)
if ($line4362 -match 'thoughts' -and $line4361 -notmatch 'thoughts' -and $line4361 -match 'mood') {
    Write-Host "Confirmed: line 4362 is thoughts (心声), line 4361 is mood (心情). Swapping..."
    
    # Swap lines 4361 and 4362 (0-indexed)
    $lines[4361] = $line4362  # put thoughts (心声) where mood (心情) was
    $lines[4362] = $line4361  # put mood (心情) where thoughts (心声) was
    
    # Now add substring(0,10) limit to the new line positions
    # Line 4361 now has thoughts - add 10 char limit
    $lines[4361] = $lines[4361] -replace "\`${statusData\?\.thoughts \|\| '([^']+)'}", '${(statusData?.thoughts || ' + "'" + '$1' + "'" + ').substring(0,10)}'
    # Line 4362 now has mood - add 10 char limit
    $lines[4362] = $lines[4362] -replace "\`${statusData\?\.mood \|\| '([^']+)'}", '${(statusData?.mood || ' + "'" + '$1' + "'" + ').substring(0,10)}'
    
    Write-Host "After swap:"
    Write-Host "Line 4362 (0-idx 4361): $($lines[4361])"
    Write-Host "Line 4363 (0-idx 4362): $($lines[4362])"
    
    [System.IO.File]::WriteAllLines($file, $lines, [System.Text.Encoding]::UTF8)
    Write-Host "File saved!"
} else {
    Write-Host "Lines don't match expected pattern. Checking what's there..."
    Write-Host "Line 4361 contains 'thoughts': $($line4361 -match 'thoughts')"
    Write-Host "Line 4362 contains 'thoughts': $($line4362 -match 'thoughts')"
    Write-Host "Line 4361 contains 'mood': $($line4361 -match 'mood')"
    Write-Host "Line 4362 contains 'mood': $($line4362 -match 'mood')"
}
