# Tests start_app.bat from a folder name with spaces and parentheses (a classic batch-file trap).
# Reuses the Python / JDK already installed by the fresh-machine test (%TEMP%\fresh_machine) to save downloads.
# Summary: %LOCALAPPDATA%\Temp\awkward.txt
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$out = "$env:LOCALAPPDATA\Temp\awkward.txt"; Remove-Item $out -ErrorAction SilentlyContinue
function Note($s) { Add-Content $out $s }
$dst = "$env:TEMP\my py (copy) 2"
& powershell -NoProfile -ExecutionPolicy Bypass -File "$root\_dev_tools\make_fresh_copy.ps1" -Dest $dst | ForEach-Object { Note $_ }
robocopy "$env:TEMP\fresh_machine\.tools" "$dst\.tools" /E /NFL /NDL /NJH /NJS /NP /MT:8 | Out-Null
robocopy "$env:TEMP\fresh_machine\java\lib" "$dst\java\lib" /E /NFL /NDL /NJH /NJS /NP | Out-Null
Note ("python:{0} jdk:{1} jars:{2}" -f (Test-Path "$dst\.tools\py\python.exe"), (Test-Path "$dst\.tools\jdk21\bin\javac.exe"), (Get-ChildItem "$dst\java\lib" -Filter *.jar -ErrorAction SilentlyContinue | Measure-Object).Count)
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in 8765, 8766 } | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
$log = "$env:LOCALAPPDATA\Temp\awkward_run.log"; Remove-Item $log -ErrorAction SilentlyContinue
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = "cmd.exe /c `"`"$dst\start_app.bat`" both --no-browser > `"$log`" 2>&1`""; CurrentDirectory = $dst }
Note "started rc=$($r.ReturnValue)"
$t0 = Get-Date; $up = @{}
while (((Get-Date) - $t0).TotalSeconds -lt 120 -and $up.Count -lt 2) {
    foreach ($p in 8765, 8766) { if (-not $up[$p]) { try { $up[$p] = ((Invoke-WebRequest "http://127.0.0.1:$p/api/track" -UseBasicParsing -TimeoutSec 3).Content | ConvertFrom-Json).name; Note ("{0} up after {1:N0}s: {2}" -f $p, ((Get-Date) - $t0).TotalSeconds, $up[$p]) } catch { } } }
    Start-Sleep 3
}
foreach ($p in 8765, 8766) { if (-not $up[$p]) { Note "$p DID NOT START" } }
Note "--- launcher output"
if (Test-Path $log) { Get-Content $log -Tail 10 | ForEach-Object { Note "  $_" } }
Note "DONE"
