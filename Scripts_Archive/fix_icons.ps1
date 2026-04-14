$file = 'c:\Users\Administrator\Desktop\111\index.html'
$f = Get-Content $file -Raw -Encoding UTF8

# 1. Writing style page: replace emoji icons before "一键提取" 
$f = $f -replace '(onclick="manualAiCompress\(\)">).*?(</span>)', '$1<img src="ICON/AI提炼图标.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> 一键提取$2'
Write-Output "1. Writing style button replaced"

# 2. addContact page: replace emoji before "AI 一键提取"
$f = $f -replace "(generatePersonaMemo\('contactMemo', 'contactPersona'\)"">).*?(</button>)", '$1<img src="ICON/AI提炼图标.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> AI 一键提取$2'
Write-Output "2. addContact AI button replaced"

# 3. Chat settings page: replace emoji before "AI 提取"
$f = $f -replace "(generatePersonaMemo\('chatContactMemo', 'contactMaskTextarea'\)"">).*?(</button>)", '$1<img src="ICON/AI提炼图标.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> AI 提取$2'
Write-Output "3. Chat settings AI button replaced"

# 4. Forum board page: replace emoji before "AI 生成"
$f = $f -replace '(onclick="generateBoardAI\(\)">).*?(</button>)', '$1<img src="ICON/AI提炼图标.png" style="width:14px;height:14px;vertical-align:middle;margin-right:2px;"> AI 生成$2'
Write-Output "4. Forum board AI button replaced"

# Save file
[System.IO.File]::WriteAllText($file, $f, [System.Text.Encoding]::UTF8)
Write-Output "File saved successfully!"

# Verify
$check = Get-Content $file -Raw -Encoding UTF8
$count = ([regex]::Matches($check, 'AI提炼图标\.png')).Count
Write-Output "Total AI提炼图标.png references found: $count"
