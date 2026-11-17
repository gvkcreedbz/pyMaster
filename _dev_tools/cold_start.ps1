# Measures how long a cold portal takes to answer its first requests (throw-away data dir, port 8779).
param([string]$Track = "python", [int]$Runs = 3)
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$py = Join-Path $root ".tools\py\python.exe"; $env:PYTHONUTF8 = "1"
$env:PORTAL_TRACK = $Track; $env:PORTAL_PORT = "8779"
foreach ($i in 1..$Runs) {
    $env:PORTAL_DATA = "$env:TEMP\cold_$Track$i"; if (Test-Path $env:PORTAL_DATA) { Remove-Item -Recurse -Force $env:PORTAL_DATA }
    $t0 = Get-Date
    $srv = Start-Process -FilePath $py -ArgumentList '-X', 'utf8', '-W', 'ignore', 'portal\run.py', '--no-browser' -PassThru -WindowStyle Hidden
    $up = $null
    while (-not $up -and ((Get-Date) - $t0).TotalSeconds -lt 60) { try { Invoke-WebRequest "http://127.0.0.1:8779/api/track" -UseBasicParsing -TimeoutSec 2 | Out-Null; $up = (Get-Date) } catch { Start-Sleep -Milliseconds 100 } }
    $line = "run $i : server up after {0:N1}s" -f (($up - $t0).TotalSeconds)
    foreach ($path in "/api/overview", "/api/day/1", "/api/drills/summary") {
        $t1 = Get-Date
        try { Invoke-WebRequest "http://127.0.0.1:8779$path" -UseBasicParsing -TimeoutSec 30 | Out-Null } catch { }
        $line += ("  {0} {1:N2}s" -f $path, ((Get-Date) - $t1).TotalSeconds)
    }
    $t1 = Get-Date
    try { Invoke-WebRequest "http://127.0.0.1:8779/api/session/start" -Method Post -Headers @{ "x-portal" = "1" } -UseBasicParsing -TimeoutSec 30 | Out-Null } catch { }
    $line += ("  session/start {0:N2}s" -f ((Get-Date) - $t1).TotalSeconds)
    Write-Output $line
    Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue; Start-Sleep 2
}
