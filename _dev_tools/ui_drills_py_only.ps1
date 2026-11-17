$root = "C:\Users\C8T9C7\Desktop\desk\TESTING-AI\PY"; Set-Location $root
$py = Join-Path $root ".tools\py\python.exe"; $env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$sum = "$env:LOCALAPPDATA\Temp\ui_drills_py.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
$env:PORTAL_TRACK = "python"; $env:PORTAL_PORT = "8778"; $env:PORTAL_DATA = "$env:LOCALAPPDATA\Temp\ui_drills_data_py2"
if (Test-Path $env:PORTAL_DATA) { Remove-Item -Recurse -Force $env:PORTAL_DATA }
$srv = Start-Process -FilePath $py -ArgumentList '-X','utf8','-W','ignore','portal\run.py','--no-browser' -PassThru -WindowStyle Hidden
Start-Sleep 8
& $py -W ignore _dev_tools\ui_drills_test.py http://127.0.0.1:8778 python > "$env:LOCALAPPDATA\Temp\ui_drills_py.log" 2>&1
Add-Content $sum "exit $LASTEXITCODE"
([IO.File]::ReadAllText("$env:LOCALAPPDATA\Temp\ui_drills_py.log") -split "`n" | Where-Object { $_ -match 'FAIL|checks,|Traceback' } | Select-Object -First 30) | ForEach-Object { Add-Content $sum $_ }
Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
Add-Content $sum "DONE"