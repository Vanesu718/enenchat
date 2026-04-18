$content = Get-Content -Path "js/main.js" -Raw -Encoding UTF8
$startIndex = $content.IndexOf("async function triggerAIReply")
if ($startIndex -ge 0) {
    $length = [math]::Min(15000, $content.Length - ($startIndex + 15000))
    $extracted = $content.Substring($startIndex + 15000, $length)
    Set-Content -Path "temp_extract_2.txt" -Value $extracted -Encoding UTF8
}
