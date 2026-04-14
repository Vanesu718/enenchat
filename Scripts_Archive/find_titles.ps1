Get-Content js/main.js -Encoding UTF8 | Select-String -Pattern "title=" | Select-Object -First 30
