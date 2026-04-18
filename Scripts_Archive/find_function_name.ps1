$lines = Get-Content -Path js/main.js -Encoding UTF8
for ($i = 2818; $i -ge 2000; $i--) {
    if ($lines[$i] -match 'function[ \w]*\(' -or $lines[$i] -match '=>') {
        Write-Output "Line $($i + 1): $($lines[$i].Trim())"
        if ($lines[$i] -match 'function') { break }
    }
}