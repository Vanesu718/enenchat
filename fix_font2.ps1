$f = 'c:\Users\Administrator\Desktop\111\index.html'
$c = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)

# 替换1：在 styleEl.innerHTML 前插入 fetch+blob 逻辑
# 旧：直接 styleEl.innerHTML = `...src: url('${fontUrl}')...`
# 新：先fetch获取blob URL，再赋值

$old1 = "  styleEl.innerHTML = ``"
$old1_full = "  styleEl.innerHTML = ``
    @font-face {
      font-family: 'MyCustomFont';
      src: url('`${fontUrl}');
    }"

# 用更精确的前后文本定位
$searchStr = "src: url('`${fontUrl}');"
$idx = $c.IndexOf($searchStr)

if ($idx -lt 0) {
    Write-Host "ERROR: Cannot find target string"
    exit 1
}

# 替换 src: url('${fontUrl}'); 为 src: ${fontSrc};
$step1 = $c.Replace($searchStr, "src: `${fontSrc};")
Write-Host "Step1: replaced src url"

# 现在找 styleEl.innerHTML 行（在函数体内），在其前面插入 fetch 逻辑
# 定位注释行 "const fontSize"
$insertAfter = "  const fontSize = document.getElementById('customFontSize')?.value || '14';"

$fetchCode = @"

  // PC端Chrome对@font-face外部字体有严格CORS限制
  // 先用fetch下载字体转为blob URL（同源绕过跨域），失败则回退直接链接
  let fontSrc = `"url('`${fontUrl}')`";
  try {
    const resp = await fetch(fontUrl, { mode: 'cors' });
    if (resp.ok) {
      const blob = await resp.blob();
      fontSrc = `"url('`${URL.createObjectURL(blob)}')`";
    }
  } catch(e) {
    console.warn('[字体] CORS加载失败，回退直接链接:', e.message);
  }
"@

$step2 = $step1.Replace($insertAfter, $insertAfter + $fetchCode)
Write-Host "Step2: inserted fetch+blob code"

# 验证两处修改都生效
if ($step2.Contains("await fetch(fontUrl") -and $step2.Contains("src: `${fontSrc};")) {
    [System.IO.File]::WriteAllText($f, $step2, [System.Text.Encoding]::UTF8)
    Write-Host "SUCCESS: 字体CORS修复完成！PC端字体现在可以正常加载了。"
} else {
    Write-Host "WARN: 验证失败，检查替换结果..."
    Write-Host ("Contains fetch: " + $step2.Contains("await fetch(fontUrl"))
    Write-Host ("Contains fontSrc: " + $step2.Contains("src: `${fontSrc};"))
}
