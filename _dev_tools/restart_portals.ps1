# Restart both portals (Py Master 8765, Java Master 8766) fully detached, using the project-local Python.
#   powershell -ExecutionPolicy Bypass -File _dev_tools\restart_portals.ps1
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$py = Join-Path $root ".tools\py\python.exe"; if (-not (Test-Path $py)) { Write-Host "Run _dev_tools\setup_dev_python.ps1 first"; exit 1 }
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in 8765, 8766 } |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep 2
foreach ($a in "", "--track java") {
    Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
        CommandLine = "`"$py`" -X utf8 -W ignore portal\run.py $a --no-browser"; CurrentDirectory = $root } | Out-Null
}
Start-Sleep 14
foreach ($p in 8765, 8766) {
    try { $t = (Invoke-WebRequest "http://127.0.0.1:$p/api/track" -UseBasicParsing -TimeoutSec 20).Content | ConvertFrom-Json; Write-Host "$p up: $($t.name)" }
    catch { Write-Host "$p DOWN" }
}
