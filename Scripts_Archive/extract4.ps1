$content = Get-Content -Path "js/main.js" -Raw -Encoding UTF8
$startIndex = $content.IndexOf("function createMsgElement")
if ($startIndex -ge 0) {
    $length = [math]::Min(15000, $content.Length - $startIndex)
    $extracted = $content.Substring($startIndex, $length)
    Set-Content -Path "temp_extract_4.txt" -Value $extracted -Encoding UTF8
}
