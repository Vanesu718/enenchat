$lines = Get-Content -Path js/main.js -Encoding UTF8
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'roundCount') {
        Write-Output "Line $($i + 1): $($lines[$i].Trim())"
    }
}