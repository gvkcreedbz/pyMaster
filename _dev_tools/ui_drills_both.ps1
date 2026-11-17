# Browser test of the Drills tab on both tracks against throw-away servers (port 8778). Summary: %TEMP%\ui_drills.txt
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$py = Join-Path $root ".tools\py\python.exe"; $env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$sum = "$env:TEMP\ui_drills.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
foreach ($track in 'python', 'java') {
    $env:PORTAL_TRACK = $track; $env:PORTAL_PORT = "8778"; $env:PORTAL_DATA = "$env:TEMP\ui_drills_data_$track"
    if (Test-Path $env:PORTAL_DATA) { Remove-Item -Recurse -Force $env:PORTAL_DATA }
    $srv = Start-Process -FilePath $py -ArgumentList '-X', 'utf8', '-W', 'ignore', 'portal\run.py', '--no-browser' -PassThru -WindowStyle Hidden
    Start-Sleep 8
    $log = "$env:TEMP\ui_drills_$track.log"
    & $py -W ignore _dev_tools\ui_drills_test.py http://127.0.0.1:8778 $track > $log 2>&1
    Add-Content $sum "== $track exit $LASTEXITCODE"
    ([IO.File]::ReadAllText($log) -split "`n" | Where-Object { $_ -match 'FAIL|checks,|Traceback|Error' } | Select-Object -First 25) | ForEach-Object { Add-Content $sum "   $_" }
    Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}
Add-Content $sum "DONE"
