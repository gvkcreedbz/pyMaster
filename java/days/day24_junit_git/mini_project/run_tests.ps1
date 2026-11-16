# Compile the mini project and run its JUnit 5 tests with the console launcher (no Maven needed).
# Run from this folder:  .\run_tests.ps1
$jar = "..\..\..\lib\junit-platform-console-standalone-1.10.3.jar"
if (-not (Test-Path $jar)) { Write-Error "JUnit jar missing: run  python _dev_tools/fetch_java_libs.py"; exit 1 }
$java = if ($env:JAVA_HOME) { "$env:JAVA_HOME\bin" } elseif (Test-Path "..\..\..\..\.tools\jdk21\bin") { "..\..\..\..\.tools\jdk21\bin" } else { "" }
$javac = if ($java) { "$java\javac.exe" } else { "javac" }
$javaExe = if ($java) { "$java\java.exe" } else { "java" }
Remove-Item -Recurse -Force out -ErrorAction SilentlyContinue
& $javac -cp $jar -d out Shop.java Cart.java ShopTest.java
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $javaExe -jar $jar execute --class-path out --scan-class-path --disable-banner
exit $LASTEXITCODE
