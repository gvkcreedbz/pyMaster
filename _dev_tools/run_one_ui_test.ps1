# Run ONE browser test against ONE throw-away server and keep the full output.
#   powershell -File _dev_tools\run_one_ui_test.ps1 -Script ui_practice_test.py -Track python [-Port 8780]
# Output: %LOCALAPPDATA%\Temp\one_ui.txt
param([Parameter(Mandatory = $true)][string]$Script, [string]$Track = "python", [int]$Port = 8780)
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$py = Join-Path $root ".tools\py\python.exe"; $env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$tmp = "$env:LOCALAPPDATA\Temp"; $out = "$tmp\one_ui.txt"; Remove-Item $out -ErrorAction SilentlyContinue
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq $Port } | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
$env:PORTAL_TRACK = $Track; $env:PORTAL_PORT = "$Port"; $env:PORTAL_DATA = "$tmp\one_ui_data"
if (Test-Path $env:PORTAL_DATA) { Remove-Item -Recurse -Force $env:PORTAL_DATA }
$srv = Start-Process -FilePath $py -ArgumentList '-X', 'utf8', '-W', 'ignore', 'portal\run.py', '--no-browser' -PassThru -WindowStyle Hidden -RedirectStandardError "$tmp\one_ui_srv.err"
$up = $false; for ($i = 0; $i -lt 90 -and -not $up; $i++) { try { Invoke-WebRequest "http://127.0.0.1:$Port/api/overview" -UseBasicParsing -TimeoutSec 5 | Out-Null; $up = $true } catch { Start-Sleep 1 } }
& $py -W ignore "_dev_tools\$Script" "http://127.0.0.1:$Port" $Track > $out 2>&1
Add-Content $out "exit $LASTEXITCODE"
Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
Add-Content $out "DONE"
