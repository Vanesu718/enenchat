$f = 'c:\Users\Administrator\Desktop\111\index.html'
$c = [System.IO.File]::ReadAllText($f, [System.Text.Encoding]::UTF8)

# Step1: replace src: url('${fontUrl}'); with src: ${fontSrc};
$q = [char]39
$d = [char]36
$target1 = "src: url(" + $q + $d + "{fontUrl}" + $q + ");"
$replace1 = "src: " + $d + "{fontSrc};"
Write-Host "Target1: $target1"
Write-Host "Found: $($c.Contains($target1))"

if (-not $c.Contains($target1)) {
    Write-Host "ERROR step1"
    exit 1
}
$c = $c.Replace($target1, $replace1)
Write-Host "Step1 OK"

# Step2: find anchor line and append fetch+blob code after it
$anchor = "  const fontSize = document.getElementById(" + $q + "customFontSize" + $q + ")?.value || " + $q + "14" + $q + ";"
Write-Host "Anchor found: $($c.Contains($anchor))"

if (-not $c.Contains($anchor)) {
    Write-Host "ERROR step2 anchor not found"
    exit 1
}

$fetchInsert = @'

  // CORS fix: fetch font as blob URL to bypass PC browser CORS restriction
  // Fallback to direct URL if fetch fails (mobile stays compatible)
  let fontSrc = `url('${fontUrl}')`;
  try {
    const resp = await fetch(fontUrl, { mode: 'cors' });
    if (resp.ok) {
      const blob = await resp.blob();
      fontSrc = `url('${URL.createObjectURL(blob)}')`;
    }
  } catch(e) {
    console.warn('[Font] CORS failed, using direct URL:', e.message);
  }
'@

$c = $c.Replace($anchor, $anchor + $fetchInsert)
Write-Host "Step2 OK"

[System.IO.File]::WriteAllText($f, $c, [System.Text.Encoding]::UTF8)
Write-Host "SUCCESS: Font CORS fix applied and saved!"
