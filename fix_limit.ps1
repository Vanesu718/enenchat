$file = 'c:\Users\Administrator\Desktop\111\index.html'
$lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)

Write-Output ("Total lines: " + $lines.Length)

# Find and modify the thoughts and mood lines
for ($i = 0; $i -lt $lines.Length; $i++) {
    $line = $lines[$i]
    
    # thoughts line (心声) - add substring limit
    if ($line -match 'bc-status-item thoughts' -and $line -match 'statusData\?\.thoughts') {
        Write-Output ("Found thoughts at line " + $i + ": " + $line.Substring(0, [Math]::Min(100, $line.Length)))
        # Replace: ${statusData?.thoughts || 'xxx'} with ${(statusData?.thoughts || 'xxx').substring(0,10)}
        $newLine = $line -replace '(\$\{statusData\?\.thoughts \|\| [^}]+\})', '${(statusData?.thoughts || ' + [char]39 + [char]0x6ca1 + [char]0x6709 + [char]0x60f3 + [char]0x6cd5 + [char]39 + ').substring(0,10)}'
        Write-Output ("New thoughts line: " + $newLine.Substring(0, [Math]::Min(100, $newLine.Length)))
        $lines[$i] = $newLine
    }
    
    # mood line (心情) - add substring limit (the one NOT in thoughts class)
    if ($line -match 'bc-status-item"' -and $line -notmatch 'thoughts' -and $line -notmatch 'favor' -and $line -notmatch 'location' -and $line -match 'statusData\?\.mood') {
        Write-Output ("Found mood at line " + $i + ": " + $line.Substring(0, [Math]::Min(100, $line.Length)))
        $newLine = $line -replace '(\$\{statusData\?\.mood \|\| [^}]+\})', '${(statusData?.mood || ' + [char]39 + [char]0x5e73 + [char]0x9759 + [char]39 + ').substring(0,10)}'
        Write-Output ("New mood line: " + $newLine.Substring(0, [Math]::Min(100, $newLine.Length)))
        $lines[$i] = $newLine
    }
}

[System.IO.File]::WriteAllLines($file, $lines, (New-Object System.Text.UTF8Encoding $false))
Write-Output "File saved!"
