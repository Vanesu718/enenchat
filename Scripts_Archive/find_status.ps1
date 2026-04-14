$content = Get-Content 'js/main.js' -Raw
$lines = $content -split "`r`n|`n"
$target = "const status = { location: '未知', mood: '平静', thoughts: '暂无数据', favor: 0 };"

for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match "\[escape target manually maybe\]" -or $lines[$i].Contains($target)) {
        Write-Host "`n--- Match at line $($i+1) ---"
        $start = [Math]::Max(0, $i - 15)
        $end = [Math]::Min($lines.Length - 1, $i + 15)
        for ($j = $start; $j -le $end; $j++) {
            Write-Host "$($j+1): $($lines[$j])"
        }
    }
}
