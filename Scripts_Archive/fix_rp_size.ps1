$enc = New-Object System.Text.UTF8Encoding($false) 
$f = 'c:\Users\Administrator\Desktop\111\js\main.js'  
$js = [System.IO.File]::ReadAllText($f, $enc) 
$js = $js -replace 'width:180px;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 8px rgba\(0,0,0,0\.18\);cursor:pointer;user-select:none;', 'width:140px;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 8px rgba(0,0,0,0.18);cursor:pointer;user-select:none;' 
$js = $js -replace 'position:relative;width:100%;height:240px;background:', 'position:relative;width:100%;height:150px;background:'  
$js = $js -replace 'justify-content:flex-end;padding-bottom:30px;', 'justify-content:flex-end;padding-bottom:20px;'  
$js = $js -replace 'width:52px;height:52px;border-radius:50%;', 'width:40px;height:40px;border-radius:50%;'  
$js = $js -replace 'justify-content:center;font-size:22px;font-weight:bold;color:#8b4513;', 'justify-content:center;font-size:18px;font-weight:bold;color:#8b4513;' 
$js = $js -replace "box\.onclick = \(e\) =^> \{ e\.stopPropagation\(\); openRedPacket\(box, rpAmt, rpMsg, coverUrl\); \};", "if (side === 'left') { box.onclick = (e) =^> { e.stopPropagation(); openRedPacket(box, rpAmt, rpMsg, coverUrl); }; } else { box.style.cursor = 'default'; }"  
[System.IO.File]::WriteAllText($f, $js, $enc)  
'DONE' | Out-File 'c:\Users\Administrator\Desktop\111\rp_check.txt' 
