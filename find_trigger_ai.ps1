$lines = Get-Content -Path js/main.js -Encoding UTF8
$start = [Math]::Max(0, 2877 - 60)
$end = [Math]::Min($lines.Count - 1, 2877 + 20)
for ($j = $start; $j -le $end; $j++) {
    Write-Output "Line $($j + 1): $($lines[$j])"
}