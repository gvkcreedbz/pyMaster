# Maintainer helper: create (or repair) the project-local portable Python in .tools\py (git-ignored).
# Use it when this machine has no Python installed. Everything the portal, the tests and the course tools need goes in.
#   powershell -ExecutionPolicy Bypass -File _dev_tools\setup_dev_python.ps1
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = "SilentlyContinue"
$root = Split-Path -Parent $PSScriptRoot
$d = Join-Path $root ".tools\py"
$ver = "3.13.9"
if (-not (Test-Path "$d\python.exe")) {
    New-Item -ItemType Directory -Force $d | Out-Null
    Invoke-WebRequest "https://www.python.org/ftp/python/$ver/python-$ver-embed-amd64.zip" -OutFile "$d\py.zip" -UseBasicParsing
    Expand-Archive "$d\py.zip" -DestinationPath $d -Force; Remove-Item "$d\py.zip"
    $pth = Get-ChildItem $d -Filter "python*._pth" | Select-Object -First 1
    [IO.File]::WriteAllText($pth.FullName, [IO.File]::ReadAllText($pth.FullName).Replace("#import site", "import site"))
    Invoke-WebRequest "https://bootstrap.pypa.io/get-pip.py" -OutFile "$d\get-pip.py" -UseBasicParsing
    & "$d\python.exe" "$d\get-pip.py" --no-warn-script-location
}
& "$d\python.exe" -m pip install --no-warn-script-location -r "$root\requirements-portal.txt" -r "$root\requirements-week4.txt" pytest ruff websockets openpyxl pyyaml
Write-Host "Ready: $d\python.exe"
