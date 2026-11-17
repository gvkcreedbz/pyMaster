# Every browser test, one after another, on both tracks. Summary: %LOCALAPPDATA%\Temp\full_ui.txt (last line DONE).
#   powershell -File _dev_tools\full_ui_check.ps1
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$tmp = "$env:LOCALAPPDATA\Temp"; $sum = "$tmp\full_ui.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
function Run($title, $file, $args2) {
    Add-Content $sum "##### $title  ($(Get-Date -Format HH:mm:ss))"
    & powershell -NoProfile -ExecutionPolicy Bypass -File "$root\_dev_tools\$file" @args2 *> "$tmp\full_ui_step.txt"
}
Run "main sweep (every page, 3 widths)" "ui_regress_both.ps1" @()
Get-Content "$tmp\ui_both.txt" | ForEach-Object { Add-Content $sum $_ }
Run "drills: solve all 300 through the UI" "ui_drills_both.ps1" @()
Get-Content "$tmp\ui_drills.txt" | ForEach-Object { Add-Content $sum $_ }
foreach ($s in "ui_practice_test.py", "ui_predict_test.py") {
    Add-Content $sum "##### $s  ($(Get-Date -Format HH:mm:ss))"
    foreach ($tr in "python", "java") {
        & powershell -NoProfile -ExecutionPolicy Bypass -File "$root\_dev_tools\run_one_ui_test.ps1" -Script $s -Track $tr *> "$tmp\full_ui_step.txt"
        Add-Content $sum "== $tr"
        ([IO.File]::ReadAllText("$tmp\one_ui.txt") -split "`n" | Where-Object { $_ -match '^\[FAIL\]|checks,|^exit' } | ForEach-Object { $_.Substring(0, [Math]::Min(300, $_.Length)) }) | ForEach-Object { Add-Content $sum "   $_" }
    }
}
Add-Content $sum "DONE"
