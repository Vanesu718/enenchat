$lines = Get-Content -Path js/main.js -Encoding UTF8
$start = [Math]::Max(0, 10145 - 20)
$end = [Math]::Min($lines.Count - 1, 10145 + 10)
for ($j = $start; $j -le $end; $j++) {
    Write-Output "Line $($j + 1): $($lines[$j])"
}