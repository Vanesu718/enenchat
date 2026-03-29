$file = 'c:\Users\Administrator\Desktop\111\index.html'
$content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

# ==========================================
# 1. Swap 心声 and 心情 positions, add 10-char limit
# ==========================================
# Original: 地点, 心情, 心声, 好感度
# New:      地点, 心声, 心情, 好感度

$oldStatus = '          <div class="bc-status-item"><div class="bc-label">?? ' + [char]0x5730 + [char]0x70b9 + '</div><div class="bc-val">${statusData?.location || ' + "'" + [char]0x672a + [char]0x77e5 + "'" + '}</div></div>
          <div class="bc-status-item"><div class="bc-label">?? ' + [char]0x5fc3 + [char]0x60c5 + '</div><div class="bc-val">${statusData?.mood || ' + "'" + [char]0x5e73 + [char]0x9759 + "'" + '}</div></div>
          <div class="bc-status-item thoughts"><div class="bc-label">?? ' + [char]0x5fc3 + [char]0x58f0 + '</div><div class="bc-val">${statusData?.thoughts || ' + "'" + [char]0x6ca1 + [char]0x6709 + [char]0x60f3 + [char]0x6cd5 + "'" + '}</div></div>
          <div class="bc-status-item favor"><div class="bc-label">?? ' + [char]0x597d + [char]0x611f + [char]0x5ea6 + '</div><div class="bc-val">${statusData?.favor || 0}%</div></div>'

Write-Host "Searching for old status block..."
if ($content.Contains($oldStatus)) {
    Write-Host "Found! Replacing..."
    
    $newStatus = '          <div class="bc-status-item"><div class="bc-label">?? ' + [char]0x5730 + [char]0x70b9 + '</div><div class="bc-val">${statusData?.location || ' + "'" + [char]0x672a + [char]0x77e5 + "'" + '}</div></div>
          <div class="bc-status-item thoughts"><div class="bc-label">?? ' + [char]0x5fc3 + [char]0x58f0 + '</div><div class="bc-val">${(statusData?.thoughts || ' + "'" + [char]0x6ca1 + [char]0x6709 + [char]0x60f3 + [char]0x6cd5 + "'" + ').substring(0,10)}</div></div>
          <div class="bc-status-item"><div class="bc-label">?? ' + [char]0x5fc3 + [char]0x60c5 + '</div><div class="bc-val">${(statusData?.mood || ' + "'" + [char]0x5e73 + [char]0x9759 + "'" + ').substring(0,10)}</div></div>
          <div class="bc-status-item favor"><div class="bc-label">?? ' + [char]0x597d + [char]0x611f + [char]0x5ea6 + '</div><div class="bc-val">${statusData?.favor || 0}%</div></div>'
    
    $content = $content.Replace($oldStatus, $newStatus)
    Write-Host "Status block replaced."
} else {
    Write-Host "NOT found. Trying line-based search..."
    $lines = $content -split "`n"
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i] -match 'bc-status-item') {
            Write-Host "Line $i`: $($lines[$i])"
        }
    }
}

# ==========================================
# 2. CSS: Widen avatar (64px -> 80px) and reduce gap (12px -> 6px)
# ==========================================
$oldAvatarCss = '  .blue-card-avatar {
    width: 64px;
    border-radius: 10px;
    overflow: hidden;
    flex-shrink: 0;
    border: 2px solid var(--main-pink);
    display: flex;
  }'

$newAvatarCss = '  .blue-card-avatar {
    width: 80px;
    border-radius: 10px;
    overflow: hidden;
    flex-shrink: 0;
    border: 2px solid var(--main-pink);
    display: flex;
    margin-left: -3px;
  }'

if ($content.Contains($oldAvatarCss)) {
    $content = $content.Replace($oldAvatarCss, $newAvatarCss)
    Write-Host "Avatar CSS updated."
} else {
    Write-Host "Avatar CSS NOT found."
}

# ==========================================
# 3. CSS: Reduce gap in blue-card-top to push status closer to right edge
# ==========================================
$oldTopCss = '  .blue-card-top {
    display: flex;
    gap: 12px;
  }'

$newTopCss = '  .blue-card-top {
    display: flex;
    gap: 6px;
  }'

if ($content.Contains($oldTopCss)) {
    $content = $content.Replace($oldTopCss, $newTopCss)
    Write-Host "Top gap CSS updated."
} else {
    Write-Host "Top gap CSS NOT found."
}

# ==========================================
# 4. CSS: Adjust blue-card-status to add right padding push
# ==========================================
$oldStatusCss = '  .blue-card-status {
    flex: 1;
    display: grid;
    grid-template-columns: 7fr 4fr;
    gap: 6px;
  }'

$newStatusCss = '  .blue-card-status {
    flex: 1;
    display: grid;
    grid-template-columns: 7fr 4fr;
    gap: 6px;
    padding-right: 4px;
  }'

if ($content.Contains($oldStatusCss)) {
    $content = $content.Replace($oldStatusCss, $newStatusCss)
    Write-Host "Status CSS updated."
} else {
    Write-Host "Status CSS NOT found."
}

# Save the file
[System.IO.File]::WriteAllText($file, $content, [System.Text.Encoding]::UTF8)
Write-Host "File saved successfully!"
