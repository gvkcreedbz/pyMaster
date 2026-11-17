# Run one browser test script against throw-away servers of both tracks (port 8780). Summary: %LOCALAPPDATA%\Temp\uitest_<name>.txt
#   powershell -File _dev_tools\ui_test_both.ps1 -Script ui_practice_test.py
param([Parameter(Mandatory = $true)][string]$Script)
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$py = Join-Path $root ".tools\py\python.exe"; $env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$name = [IO.Path]::GetFileNameWithoutExtension($Script)
$tmp = "$env:LOCALAPPDATA\Temp"
$sum = "$tmp\uitest_$name.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
foreach ($track in 'python', 'java') {
    $env:PORTAL_TRACK = $track; $env:PORTAL_PORT = "8780"; $env:PORTAL_DATA = "$tmp\uitest_data_${name}_$track"
    if (Test-Path $env:PORTAL_DATA) { Remove-Item -Recurse -Force $env:PORTAL_DATA }
    $srv = Start-Process -FilePath $py -ArgumentList '-X', 'utf8', '-W', 'ignore', 'portal\run.py', '--no-browser' -PassThru -WindowStyle Hidden
    $up = $false; for ($i = 0; $i -lt 90 -and -not $up; $i++) { try { Invoke-WebRequest "http://127.0.0.1:8780/api/overview" -UseBasicParsing -TimeoutSec 5 | Out-Null; $up = $true } catch { Start-Sleep 1 } }
    $log = "$tmp\uitest_${name}_$track.log"
    & $py -W ignore "_dev_tools\$Script" http://127.0.0.1:8780 $track > $log 2>&1
    Add-Content $sum "== $track exit $LASTEXITCODE"
    ([IO.File]::ReadAllText($log) -split "`n" | Where-Object { $_ -match 'FAIL|checks,|Traceback|Error' } | Select-Object -First 30) | ForEach-Object { Add-Content $sum "   $_" }
    Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}
Add-Content $sum "DONE"
