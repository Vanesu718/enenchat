# Master implementation script for all 5 steps
$ErrorActionPreference = "Stop"
$mainPath = "c:\Users\Administrator\Desktop\111\js\main.js"
$indexPath = "c:\Users\Administrator\Desktop\111\index.html"

# Step 1: Backup
Write-Host "=== Step 1: Backup ===" -ForegroundColor Cyan
$backupDir = "c:\Users\Administrator\Desktop\111\backup_v3_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Copy-Item $mainPath "$backupDir\main.js"
Copy-Item $indexPath "$backupDir\index.html"
Copy-Item "c:\Users\Administrator\Desktop\111\css" "$backupDir\css" -Recurse
Write-Host "Backup done at: $backupDir" -ForegroundColor Green

# Read files
$mainContent = [System.IO.File]::ReadAllText($mainPath, [System.Text.Encoding]::UTF8)
$indexContent = [System.IO.File]::ReadAllText($indexPath, [System.Text.Encoding]::UTF8)

Write-Host "main.js size: $($mainContent.Length) chars" -ForegroundColor Yellow

# ============================================================
# Step 2: World Book - change 语言规范 to 世界观, add 其他
# ============================================================
Write-Host "=== Step 2: World Book UI changes ===" -ForegroundColor Cyan

# Replace 语言规范 with 世界观 in category arrays/strings
$mainContent = $mainContent -replace "'语言规范'", "'世界观'"
$mainContent = $mainContent -replace '"语言规范"', '"世界观"'
$mainContent = $mainContent -replace '>语言规范<', '>世界观<'

Write-Host "Step 2 语言规范->世界观 replacements done" -ForegroundColor Green

# ============================================================
# Step 3-5: Check what already exists
# ============================================================
Write-Host "=== Checking existing state ===" -ForegroundColor Cyan

$hasWritingStyle = $mainContent -match 'writingStyleEntries'
$hasStylePage = $mainContent -match 'writing-style-page'
$hasCompressedStyle = $mainContent -match 'compressedStyle'
$hasMemoryTrigger = $mainContent -match '记忆总结'

Write-Host "writingStyleEntries exists: $hasWritingStyle"
Write-Host "writing-style-page exists: $hasStylePage"
Write-Host "compressedStyle exists: $hasCompressedStyle"
Write-Host "记忆总结 exists: $hasMemoryTrigger"

# Find key locations in main.js
$worldbookCategoryMatch = [regex]::Match($mainContent, "'记忆总结'[^;]{0,200}")
if ($worldbookCategoryMatch.Success) {
    Write-Host "Found 记忆总结 context: $($worldbookCategoryMatch.Value.Substring(0, [Math]::Min(100, $worldbookCategoryMatch.Value.Length)))" -ForegroundColor Yellow
}

# Save main.js
[System.IO.File]::WriteAllText($mainPath, $mainContent, [System.Text.Encoding]::UTF8)
Write-Host "Saved main.js" -ForegroundColor Green

Write-Host "=== Analysis complete, ready for targeted edits ===" -ForegroundColor Cyan
