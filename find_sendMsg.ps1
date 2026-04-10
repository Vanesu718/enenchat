$lines = Get-Content -Path js/main.js -Encoding UTF8
$start = 0
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'function sendMsg\(' -or $lines[$i] -match 'async function sendMsg\(') {
        $start = $i
        break
    }
}
$end = [Math]::Min($lines.Count - 1, $start + 150)
for ($j = $start; $j -le $end; $j++) {
    Write-Output "Line $($j + 1): $($lines[$j])"
}