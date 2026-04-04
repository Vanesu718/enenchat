$file = 'c:\Users\Administrator\Desktop\111\index.html'
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

Write-Output ("Total lines: " + $lines.Length)

# Find the thoughts and mood lines by index
$thoughtsIdx = -1
$moodIdx = -1
for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match 'bc-status-item thoughts' -and $lines[$i] -match 'statusData') {
        $thoughtsIdx = $i
    }
    if ($lines[$i] -match 'bc-status-item"' -and $lines[$i] -match 'statusData' -and $lines[$i] -notmatch 'thoughts' -and $lines[$i] -notmatch 'favor' -and $lines[$i] -notmatch 'location') {
        $moodIdx = $i
    }
}

Write-Output ("thoughtsIdx=" + $thoughtsIdx + " moodIdx=" + $moodIdx)

if ($thoughtsIdx -ge 0) {
    $line = $lines[$thoughtsIdx]
    Write-Output ("thoughts line (first 120): " + $line.Substring(0, [Math]::Min(120, $line.Length)))
    
    # Use simple string IndexOf/Replace to avoid regex issues
    # Find the pattern: ${statusData?.thoughts || 'X'}
    # and replace with: ${(statusData?.thoughts || 'X').substring(0,10)}
    $searchStr = 'statusData?.thoughts ||'
    $pos = $line.IndexOf($searchStr)
    if ($pos -ge 0) {
        # Find the closing } after this
        $dollarPos = $line.LastIndexOf('${', $pos)
        $closePos = $line.IndexOf('}', $pos)
        Write-Output ("dollarPos=" + $dollarPos + " closePos=" + $closePos)
        if ($dollarPos -ge 0 -and $closePos -ge 0) {
            $before = $line.Substring(0, $dollarPos)
            $inner = $line.Substring($dollarPos + 2, $closePos - $dollarPos - 2)  # content between ${ and }
            $after = $line.Substring($closePos + 1)
            $newLine = $before + '${(' + $inner + ').substring(0,10)}' + $after
            Write-Output ("new thoughts line (first 120): " + $newLine.Substring(0, [Math]::Min(120, $newLine.Length)))
            $lines[$thoughtsIdx] = $newLine
        }
    }
}

if ($moodIdx -ge 0) {
    $line = $lines[$moodIdx]
    Write-Output ("mood line (first 120): " + $line.Substring(0, [Math]::Min(120, $line.Length)))
    
    $searchStr = 'statusData?.mood ||'
    $pos = $line.IndexOf($searchStr)
    if ($pos -ge 0) {
        $dollarPos = $line.LastIndexOf('${', $pos)
        $closePos = $line.IndexOf('}', $pos)
        Write-Output ("dollarPos=" + $dollarPos + " closePos=" + $closePos)
        if ($dollarPos -ge 0 -and $closePos -ge 0) {
            $before = $line.Substring(0, $dollarPos)
            $inner = $line.Substring($dollarPos + 2, $closePos - $dollarPos - 2)
            $after = $line.Substring($closePos + 1)
            $newLine = $before + '${(' + $inner + ').substring(0,10)}' + $after
            Write-Output ("new mood line (first 120): " + $newLine.Substring(0, [Math]::Min(120, $newLine.Length)))
            $lines[$moodIdx] = $newLine
        }
    }
}

[System.IO.File]::WriteAllLines($file, $lines, (New-Object System.Text.UTF8Encoding $false))
Write-Output "File saved!"
