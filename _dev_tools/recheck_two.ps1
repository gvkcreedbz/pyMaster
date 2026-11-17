# Re-runs (1) the Java main sweep and (2) Java drills for day 13 only. Summary: %LOCALAPPDATA%\Temp\recheck.txt
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$tmp = "$env:LOCALAPPDATA\Temp"; $sum = "$tmp\recheck.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
$py = Join-Path $root ".tools\py\python.exe"; $env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
Add-Content $sum "##### drills day 13 (java), 3 runs"
foreach ($run in 1..3) {
    $env:PORTAL_TRACK = "java"; $env:PORTAL_PORT = "8781"; $env:PORTAL_DATA = "$tmp\recheck_data$run"
    if (Test-Path $env:PORTAL_DATA) { Remove-Item -Recurse -Force $env:PORTAL_DATA }
    $srv = Start-Process -FilePath $py -ArgumentList '-X', 'utf8', '-W', 'ignore', 'portal\run.py', '--no-browser' -PassThru -WindowStyle Hidden
    $up = $false; for ($i = 0; $i -lt 90 -and -not $up; $i++) { try { Invoke-WebRequest "http://127.0.0.1:8781/api/overview" -UseBasicParsing -TimeoutSec 5 | Out-Null; $up = $true } catch { Start-Sleep 1 } }
    & $py -W ignore _dev_tools\ui_drills_test.py http://127.0.0.1:8781 java 13 > "$tmp\recheck_run$run.log" 2>&1
    Add-Content $sum ("run {0}: {1}" -f $run, (([IO.File]::ReadAllText("$tmp\recheck_run$run.log") -split "`n" | Where-Object { $_ -match 'FAIL|checks,' } | ForEach-Object { $_.Substring(0, [Math]::Min(260, $_.Length)) }) -join " | "))
    Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue; Start-Sleep 2
}
Add-Content $sum "##### main sweep (both tracks)"
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\_dev_tools\ui_regress_both.ps1" *> "$tmp\recheck_step.txt"
Get-Content "$tmp\ui_both.txt" | ForEach-Object { Add-Content $sum $_ }
Add-Content $sum "DONE"
