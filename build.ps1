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

# Output
$distDir = Join-Path $scriptDir "dist"
$outputExe = Join-Path $distDir "UpdateRootCertificates.exe"

# -- Clean ---------------------------------------------------------------------
Remove-Item $distDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

# -- Install deps --------------------------------------------------------------
& $py "-m" "pip" "install" "pip==20.3.4"
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }

& $py "-m" "pip" "install" "pyinstaller==3.4"
if ($LASTEXITCODE -ne 0) { throw "pyinstaller install failed" }

# -- Build EXE -----------------------------------------------------------------
$spec = Join-Path $scriptDir "UpdateRootCertificatesApp.spec"
& $py "-m" "PyInstaller" "--clean" $spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

if (-not (Test-Path $outputExe)) {
    throw "EXE not found after build: $outputExe"
}

Write-Output "Done: $outputExe"