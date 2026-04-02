$ErrorActionPreference = "Stop"

<#
UpdateRootCertificates build script

Dependencies (required on build machine)

Python
- Python 2.7 (32-bit)
  Path expected:
    C:\Python27\python.exe
    or
    C:\Program Files (x86)\Python27\python.exe

Python packages
- pip 20.3.4 (last version supporting Python 2.7)
- pyinstaller 3.4 (last reliable version for Windows XP compatibility)

Install via:
    python -m pip install pip==20.3.4 pyinstaller==3.4

WinRAR
- WinRAR x86 version 7.1.0.0
  Required files:
    Rar.exe
    Default32.SFX

  Default paths:
    C:\Program Files\WinRAR\x86\Rar.exe
    C:\Program Files\WinRAR\x86\Default32.SFX

  Notes:
  - Must use Default32.SFX (32-bit stub) for Windows XP compatibility
  - 64-bit or newer stubs will fail on XP ("not a valid Win32 application")

rcedit
- Used to set icon on SFX stub and final EXE
- Installed via Chocolatey or manually

  Default path:
    C:\ProgramData\chocolatey\bin\rcedit.exe

Notes
- OpenSSL is NOT required; certificate store updates use the Windows CryptoAPI directly

Microsoft VC++ Runtime (VC90)
- Visual C++ 2008 SP1 (x86) runtime files
- Automatically copied from:
    C:\Windows\WinSxS\x86_microsoft.vc90.crt_*

  Files included:
    msvcr90.dll
    msvcp90.dll
    msvcm90.dll
    Microsoft.VC90.CRT.manifest

Output
- Final distributable:
    dist\UpdateRootCertificates.exe

- This is a self-extracting archive (SFX)
- Extracts to:
    %TEMP%\UpdateRootCertificates
- Runs the embedded Python application
- No external dependencies required on target system (including XP)

Notes
- Built EXE targets Windows XP through Windows 11
- Uses PyInstaller onedir mode for reliability
- SFX wrapper provides single-file distribution
#>

# -- Paths ---------------------------------------------------------------------
$scriptDir = $PSScriptRoot

# Python
$py = "C:\Python27\python.exe"
if (-not (Test-Path $py)) {
    $py = "C:\Program Files (x86)\Python27\python.exe"
}
if (-not (Test-Path $py)) {
    throw "Python 2.7 not found"
}

$env:PYTHONHOME = Split-Path $py
$env:PYTHONPATH = ""

$pyBits = & $py -c "import struct; print(struct.calcsize('P') * 8)"
if ($pyBits -ne "32") {
    throw "Python at $py is $pyBits-bit. A 32-bit Python 2.7 is required to produce an XP-compatible binary."
}

# Tools
$winrar = "C:\Program Files\WinRAR\x86\Rar.exe"
$rcedit = "C:\ProgramData\chocolatey\bin\rcedit.exe"
$sfxStub = "C:\Program Files\WinRAR\x86\Default32.SFX"

# Files
$icon = Join-Path $scriptDir "icon.ico"
$script = Join-Path $scriptDir "UpdateRootCertificates.py"

# Output
$appName = "UpdateRootCertificatesApp"
$finalName = "UpdateRootCertificates"
$distDir = Join-Path $scriptDir "dist"
$appDir = Join-Path $distDir $appName
$exePath = Join-Path $appDir "$appName.exe"
$outputExe = Join-Path $distDir "$finalName.exe"

# Temp
$sfxCfg = Join-Path $distDir "sfx.cfg"
$launcher = Join-Path $distDir "launch.cmd"
$sfxStubTmp = Join-Path $distDir "stub.sfx"

# -- Clean ---------------------------------------------------------------------
Remove-Item "$scriptDir\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $distDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$scriptDir\*.spec" -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

# -- Install deps --------------------------------------------------------------
& $py "-m" "pip" "install" "pip==20.3.4"
& $py "-m" "pip" "install" "pyinstaller==3.4"

# -- Build EXE -----------------------------------------------------------------
& $py "-m" "PyInstaller" `
    "--onedir" `
    "--clean" `
    "--icon" $icon `
    "--name" $appName `
    $script

if (-not (Test-Path $exePath)) {
    throw "EXE not found after build: $exePath"
}

# -- Bundle VC90 CRT -----------------------------------------------------------
$crt = Get-ChildItem "C:\Windows\WinSxS" -Directory |
Where-Object { $_.Name -like "x86_microsoft.vc90.crt*" } |
Select-Object -First 1

if (-not $crt) {
    Write-Error "VC90 CRT not found in WinSxS"
}

Copy-Item (Join-Path $crt.FullName "*") $appDir -Force

# -- Launcher ------------------------------------------------------------------
@'
@echo off
cd /d "%~dp0"

set "Interactive=0"
echo %CMDCMDLINE% | find /i "cmd.exe" >nul && set "Interactive=1"

UpdateRootCertificatesApp.exe
set "ERR=%ERRORLEVEL%"

if "%Interactive%"=="0" (
    if not "%ERR%"=="0" (
        echo.
        echo Script failed with exit code %ERR%.
        pause
    )
)
'@ | Set-Content -Encoding ASCII $launcher

# -- SFX Config ----------------------------------------------------------------
@"
Path=%TEMP%\UpdateRootCertificates
Setup=launch.cmd
Silent=1
Overwrite=1
TempMode
"@ | Set-Content -Encoding ASCII $sfxCfg

# -- Stub ----------------------------------------------------------------------
Copy-Item $sfxStub $sfxStubTmp -Force
& $rcedit $sfxStubTmp --set-icon $icon

# -- Build SFX -----------------------------------------------------------------
Push-Location $distDir
$launcherName = Split-Path $launcher -Leaf
& $winrar a "-sfx$sfxStubTmp" "-z$sfxCfg" "-r" "-ep1" "-y" $outputExe "$appName\*" $launcherName
Pop-Location

Remove-Item $launcher, $sfxCfg, $sfxStubTmp -ErrorAction SilentlyContinue

Write-Output "Done: $outputExe"