# Tests start_app.bat the way a user would run it: detached, with output captured, then probes the ports.
#   powershell -File _dev_tools\test_start_app.ps1 -Dir <project folder> -Mode py|java|both [-Wait 90]
# Summary: %TEMP%\start_app_test.txt  (last line DONE)
param([string]$Dir = (Split-Path -Parent $PSScriptRoot), [string]$Mode = "py", [int]$Wait = 90)
$sum = "$env:TEMP\start_app_test.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
function Note($s) { Add-Content $sum $s }
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in 8765, 8766 } |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep 2
$log = "$env:TEMP\start_app_run.log"; Remove-Item $log -ErrorAction SilentlyContinue
$t0 = Get-Date
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = "cmd.exe /c `"`"$Dir\start_app.bat`" $Mode --no-browser > `"$log`" 2>&1`""; CurrentDirectory = $Dir }
Note "started pid $($r.ProcessId) rc=$($r.ReturnValue) mode=$Mode dir=$Dir"
$want = switch ($Mode) { "py" { 8765 } "java" { 8766 } default { 8765, 8766 } }
$up = @{}
while (((Get-Date) - $t0).TotalSeconds -lt $Wait) {
    foreach ($p in $want) {
        if (-not $up[$p]) { try { $t = (Invoke-WebRequest "http://127.0.0.1:$p/api/track" -UseBasicParsing -TimeoutSec 3).Content | ConvertFrom-Json; $up[$p] = $t.name; Note ("{0} answered after {1:N0}s: {2}" -f $p, ((Get-Date) - $t0).TotalSeconds, $t.name) } catch { } }
    }
    if (($want | Where-Object { -not $up[$_] }).Count -eq 0) { break }
    Start-Sleep 3
}
foreach ($p in $want) { if (-not $up[$p]) { Note "$p DID NOT START within ${Wait}s" } }
Note "--- launcher output (tail)"
if (Test-Path $log) { Get-Content $log -Tail 14 | ForEach-Object { Note "  $_" } }
Note "DONE"
