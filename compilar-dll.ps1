# Compila los programas COBOL de src/main/resources/cobol en una sola DLL (dll/banco.dll) con GnuCOBOL.
# Requiere GnuCOBOL de MSYS2: pacman -S mingw-w64-x86_64-gnucobol
param([string]$Runtime = "C:\msys64\mingw64\bin")

$env:PATH = "$Runtime;$env:PATH"   # cobc necesita gcc y libcob en el PATH
$env:COB_CONFIG_DIR = (Resolve-Path "$Runtime\..\share\gnucobol\config").Path
New-Item -ItemType Directory -Force dll | Out-Null
$fuentes = (Get-ChildItem src/main/resources/cobol/*.cob).FullName
# -b: un solo modulo con todos los programas; cada PROGRAM-ID queda exportado como funcion
& "$Runtime\cobc.exe" -b -free -o dll/banco.dll $fuentes
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "dll/banco.dll generada con: $((Get-ChildItem src/main/resources/cobol/*.cob).BaseName -join ', ')"
