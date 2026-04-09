$content = Get-Content -Path 'js/main.js' -Raw
$lines = $content -split "`r`n"
if ($lines.Count -eq 1) { $lines = $content -split "`n" }

for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match 'function editCurrentContact' -or $lines[$i] -match 'function showContactDetail' -or $lines[$i] -match 'function editContact') {
        Write-Host "Found: $($lines[$i])"
        for ($j = $i; $j -lt $i+30; $j++) {
            Write-Host $lines[$j]
        }
        Write-Host "------"
    }
}
