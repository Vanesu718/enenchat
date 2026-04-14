$lines = Get-Content -Path js/main.js -Encoding UTF8
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'stm.roundCount = \(stm.roundCount \|\| 0\) \+ 1;') {
        Write-Output "Line $($i + 1):"
        $start = [Math]::Max(0, $i - 5)
        $end = [Math]::Min($lines.Count - 1, $i + 5)
        for ($j = $start; $j -le $end; $j++) {
            Write-Output $lines[$j]
        }
        Write-Output "---"
    }
}