param([string[]]$Suites = @('portal_smoke','test_java_assist','test_blueprints','jviz_smoke','visual_smoke'))
$py = "$env:TEMP\pyverify\py\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
if (-not $env:PORTAL_DATA) { $env:PORTAL_DATA = "$env:TEMP\ptest_py" }
$logs = "$env:TEMP\tlogs"; New-Item -ItemType Directory -Force $logs | Out-Null
foreach ($t in $Suites) {
    $log = Join-Path $logs "$t.log"
    $p = Start-Process -FilePath $py -ArgumentList @('-W', 'ignore', "_dev_tools\$t.py") -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $log -RedirectStandardError "$log.err"
    $txt = (Get-Content $log -Raw -ErrorAction SilentlyContinue) + (Get-Content "$log.err" -Raw -ErrorAction SilentlyContinue)
    $fails = ($txt -split "`n" | Where-Object { $_ -match 'FAIL|Traceback|Error' }) | Select-Object -First 8
    "== {0}: exit {1}, {2} FAIL/Error lines" -f $t, $p.ExitCode, @($fails).Count
    $fails
    ($txt -split "`n" | Select-Object -Last 3) -join "`n"
}
