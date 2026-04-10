$lines = Get-Content -Path js/main.js -Encoding UTF8
$start = [Math]::Max(0, 2877 - 10)
$end = [Math]::Min($lines.Count - 1, 2877 + 5)
for ($j = $start; $j -le $end; $j++) {
    Write-Output "Line $($j + 1): $($lines[$j])"
}