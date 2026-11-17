# Proves a RUNNING portal can really execute learner code (not just serve pages). Usage: -Port 8766 -Track java
param([int]$Port = 8766, [string]$Track = "java")
$base = "http://127.0.0.1:$Port"; $h = @{ "x-portal" = "1" }
function Run($body) { Invoke-RestMethod "$base/api/run" -Method Post -Headers $h -ContentType "application/json" -Body ($body | ConvertTo-Json -Depth 5) -TimeoutSec 120 }
$sid = (Invoke-RestMethod "$base/api/session/start" -Method Post -Headers $h).session_id
if ($Track -eq "java") {
    $r = Run @{ kind = "playground"; code = "class Play { public static void main(String[] a) { System.out.println(`"java ok: `" + (6 * 7)); } }"; session_id = $sid }
    Write-Output ("playground : ok={0} output=[{1}]" -f $r.ok, $r.output)
    $d28 = Invoke-RestMethod "$base/api/day/28"
    $r = Run @{ kind = "practice"; day_no = 28; code = $d28.practice_starter; session_id = $sid }
    Write-Output ("day 28 JDBC practice: ran={0} score line=[{1}]" -f ($r.output -notmatch "ClassNotFound|No suitable driver"), (($r.output -split "`n" | Where-Object { $_ -match "Score" }) -join ""))
    $d24 = Invoke-RestMethod "$base/api/day/24"
    $r = Run @{ kind = "practice"; day_no = 24; code = $d24.practice_starter; session_id = $sid }
    Write-Output ("day 24 JUnit practice: score line=[{0}]" -f (($r.output -split "`n" | Where-Object { $_ -match "Score" }) -join ""))
} else {
    $r = Run @{ kind = "playground"; code = "print('python ok:', 6 * 7)"; session_id = $sid }
    Write-Output ("playground : ok={0} output=[{1}]" -f $r.ok, $r.output)
    $d25 = Invoke-RestMethod "$base/api/day/25"
    $r = Run @{ kind = "practice"; day_no = 25; code = $d25.practice_starter; session_id = $sid }
    Write-Output ("day 25 pandas practice: score line=[{0}]  importError={1}" -f (($r.output -split "`n" | Where-Object { $_ -match "Score" }) -join ""), ($r.output -match "ModuleNotFoundError"))
}
