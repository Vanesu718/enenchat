Get-ChildItem -Path js -Filter *.js | ForEach-Object {
    $file = $_
    Get-Content $file.FullName -Encoding UTF8 | Select-String -Pattern "dblclick" | ForEach-Object {
        "[$($file.Name)] $($_.Line)"
    }
}
