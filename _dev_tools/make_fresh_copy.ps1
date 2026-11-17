# Copies the TRACKED files (what a git clone gives a new machine) plus start_app.bat into a clean folder, with none of
# the locally installed Python / JDK / jars / databases. Use it to test start_app.bat as a brand-new user would.
#   powershell -File _dev_tools\make_fresh_copy.ps1 [-Dest <folder>]
param([string]$Dest = "$env:TEMP\fresh_machine")
$root = Split-Path -Parent $PSScriptRoot; Set-Location $root
if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
New-Item -ItemType Directory -Force $Dest | Out-Null
$n = 0
foreach ($f in (git ls-files)) {
    $s = Join-Path $root $f
    if (Test-Path $s -PathType Leaf) {
        $d = Join-Path $Dest $f
        New-Item -ItemType Directory -Force (Split-Path $d) | Out-Null
        Copy-Item $s $d -Force; $n++
    }
}
Copy-Item (Join-Path $root "start_app.bat") $Dest -Force
Write-Output "copied $n tracked files + start_app.bat into $Dest"
Write-Output ("python:{0} jdk:{1} jars:{2} venv:{3}" -f (Test-Path "$Dest\.tools\py\python.exe"), (Test-Path "$Dest\.tools\jdk21"), (Test-Path "$Dest\java\lib\sqlite-jdbc-3.46.1.0.jar"), (Test-Path "$Dest\.venv-portal"))
