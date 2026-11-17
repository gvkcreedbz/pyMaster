# Run a pytest file once per track (python, java). Usage (from the project root):
#   powershell -File _dev_tools\test_tracks.ps1 _dev_tools/test_ex_progress.py
# Summary goes to %TEMP%\tracks_<name>.txt (last line "DONE"); full logs to %TEMP%\tracks_<name>_<track>.log
param([Parameter(Mandatory = $true)][string]$TestFile)
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
$py = Join-Path $root ".tools\py\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
$env:PYTHONUTF8 = "1"
$name = [IO.Path]::GetFileNameWithoutExtension($TestFile)
$sum = "$env:TEMP\tracks_$name.txt"; Remove-Item $sum -ErrorAction SilentlyContinue
foreach ($tr in 'python', 'java') {
    $env:PORTAL_TRACK = $tr
    $log = "$env:TEMP\tracks_${name}_$tr.log"
    & $py -m pytest $TestFile -q -p no:cacheprovider > $log 2>&1
    Add-Content $sum "== $tr exit $LASTEXITCODE"
    ([IO.File]::ReadAllText($log) -split "`n" | Where-Object { $_ -match 'passed|failed|error|FAILED|ERROR' } | Select-Object -Last 12) | ForEach-Object { Add-Content $sum "   $_" }
}
Add-Content $sum "DONE"
