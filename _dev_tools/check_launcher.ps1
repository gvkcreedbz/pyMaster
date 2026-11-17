# Checks the CI workflow file, the CI lint step, and `python -m portal` (starts a throw-away server on port 8791).
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$py = ".tools\py\python.exe"; $env:PYTHONUTF8 = "1"
$out = "$env:TEMP\launcher_check.txt"; Remove-Item $out -ErrorAction SilentlyContinue
function Note($s) { Add-Content $out $s }
& $py -c "import yaml,sys; d=yaml.safe_load(open('.github/workflows/ci.yml',encoding='utf-8')); j=d['jobs']['checks']; print('yaml ok, steps:', len(j['steps']), 'matrix:', j['strategy']['matrix']['os'])" 2>&1 | ForEach-Object { Note $_ }
& $py -m ruff check portal _dev_tools --select E9,F 2>&1 | Select-Object -Last 15 | ForEach-Object { Note "ruff: $_" }; Note "ruff exit $LASTEXITCODE"
& $py -m portal --help 2>&1 | Select-Object -First 6 | ForEach-Object { Note "help: $_" }
$env:PORTAL_DATA = "$env:TEMP\launcher_data"; Remove-Item -Recurse -Force $env:PORTAL_DATA -ErrorAction SilentlyContinue
foreach ($case in @(@('python', 8791), @('java', 8792))) {
    $p = Start-Process -FilePath $py -ArgumentList '-X', 'utf8', '-W', 'ignore', '-m', 'portal', '--track', $case[0], '--port', $case[1], '--no-browser' -PassThru -WindowStyle Hidden
    Start-Sleep 9
    try { $t = (Invoke-WebRequest "http://127.0.0.1:$($case[1])/api/track" -UseBasicParsing -TimeoutSec 15).Content | ConvertFrom-Json; Note "-m portal --track $($case[0]) --port $($case[1]) -> $($t.name) port=$($t.port)" } catch { Note "-m portal --track $($case[0]) FAILED: $($_.Exception.Message)" }
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
}
Note "DONE"
