# Full local regression (run from the project root):  powershell -File _dev_tools\regress_all.ps1
# Writes a summary to %TEMP%\reg_all.txt. Uses throw-away data dirs, so your progress is untouched.
$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"
$py = "$env:TEMP\pyverify\py\python.exe"; if (-not (Test-Path $py)) { $py = "python" }
$out = "$env:TEMP\reg_all.txt"; Remove-Item $out -ErrorAction SilentlyContinue
function Note($s) { Add-Content -Path $out -Value $s }
foreach ($t in 'portal_smoke', 'portal_smoke_java', 'visual_smoke', 'jviz_smoke') {
    $env:PORTAL_DATA = "$env:TEMP\reg_$t"
    $log = "$env:TEMP\reg_$t.log"
    & $py -W ignore "_dev_tools\$t.py" > $log 2>&1
    Note "$t exit $LASTEXITCODE"
    ([IO.File]::ReadAllText($log) -split "`n" | Where-Object { $_ -match '^\[FAIL\]|FAIL:|PROBLEMS|Traceback' } | Select-Object -First 6) | ForEach-Object { Note "    $_" }
}
Remove-Item Env:PORTAL_DATA -ErrorAction SilentlyContinue
$log = "$env:TEMP\reg_pytest.log"
& $py -m pytest _dev_tools/test_java_assist.py _dev_tools/test_blueprints.py _dev_tools/test_blueprints_java.py -q -p no:cacheprovider > $log 2>&1
Note "pytest exit $LASTEXITCODE"
([IO.File]::ReadAllText($log) -split "`n" | Select-Object -Last 3) | ForEach-Object { Note "    $_" }
& $py -W ignore _dev_tools\verify_java.py > "$env:TEMP\reg_vj.log" 2>&1; Note "verify_java exit $LASTEXITCODE"
& $py -W ignore _dev_tools\verify.py > "$env:TEMP\reg_vp.log" 2>&1; Note "verify (python) exit $LASTEXITCODE"
Note "DONE"
