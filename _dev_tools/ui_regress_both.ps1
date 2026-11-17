# Browser regression for both tracks against throw-away servers (port 8777), one after the other.
# Summary: %TEMP%\ui_both.txt
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$py = Join-Path (Split-Path -Parent $PSScriptRoot) ".tools\py\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
$sum = "$env:TEMP\ui_both.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
foreach ($track in 'python', 'java') {
    $env:PORTAL_TRACK = $track; $env:PORTAL_PORT = "8777"; $env:PORTAL_DATA = "$env:TEMP\ui_data_$track"
    if (Test-Path $env:PORTAL_DATA) { Remove-Item -Recurse -Force $env:PORTAL_DATA }
    $srv = Start-Process -FilePath $py -ArgumentList '-W', 'ignore', 'portal\run.py', '--no-browser' -PassThru -WindowStyle Hidden
    Start-Sleep 8
    $log = "$env:TEMP\ui_$track.log"
    & $py -W ignore _dev_tools\ui_regress.py http://127.0.0.1:8777 > $log 2>&1
    Add-Content $sum "== $track exit $LASTEXITCODE"
    ([IO.File]::ReadAllText($log) -split "`n" | Where-Object { $_ -match 'FAIL|checks,|PROBLEMS|Traceback' } | Select-Object -First 15) | ForEach-Object { Add-Content $sum "   $_" }
    Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}
Add-Content $sum "DONE"
