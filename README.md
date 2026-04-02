# UpdateRootCertificates

Rebuilds the Windows root certificate trust store using current data from Microsoft. Requires no external tools, no installation, and no Windows Update.

---

## Why this exists

Windows keeps its root certificate trust store current through Microsoft's automatic root update mechanism. On supported systems, root certificates are downloaded on demand, and Windows Update keeps trust data current.

That breaks down on older systems.

Legacy operating systems such as Windows XP, Vista, and Windows 7 no longer reliably receive certificate updates modern software expects. In restricted, offline, or locked-down environments, automatic updates may also fail entirely.

The result is a system with an outdated or incomplete trust store, which can cause:

- HTTPS and TLS connections to fail
- Certificate validation errors
- Installer and application trust warnings
- Software update failures
- General connectivity issues with modern services

This tool was created to rebuild the trust store directly using current Microsoft trust data, in a way that does not depend on Windows Update or on the OS successfully retrieving missing certificates on its own.

---

## What it does

UpdateRootCertificates downloads Microsoft's current trust list CAB files, extracts them, and applies them directly to the local certificate store using the Windows CryptoAPI. No third-party tools are required.

It handles the two trust lists published by Microsoft:

1. `authrootstl.cab` — trusted root certificates, applied to the `AuthRoot` store
2. `disallowedcertstl.cab` — revoked and explicitly disallowed certificates, applied to the `Disallowed` store

---

## Features

- No external dependencies
- Applies trust data using the Windows CryptoAPI directly
- No `updroots.exe`, no `certutil`, no OpenSSL
- Does not require Windows Update
- Does not require installation
- Works on Windows XP through Windows 11
- Useful for legacy, offline, restricted, and recovery scenarios
- Requires internet access to reach `ctldl.windowsupdate.com`

---

## Building

Build the release artifact (`dist\UpdateRootCertificates.exe`) with:

```powershell
.\build.ps1
```

### Prerequisites

**Python 2.7 (32-bit)**

Required to support Windows XP through Windows 11 with a single binary. PyInstaller packages it into a self-contained directory.

Expected at:
- `C:\Python27\python.exe`
- or `C:\Program Files (x86)\Python27\python.exe`

**PyInstaller 3.4**

Last version with reliable Windows XP compatibility. Installed automatically by the build script.

**WinRAR (32-bit, version 7.1.0.0)**

Used to produce the self-extracting archive. The SFX format creates a standalone `.exe` that extracts its contents and runs a launcher script. The 32-bit build covers both 32-bit and 64-bit systems.

Required files:
- `C:\Program Files\WinRAR\x86\Rar.exe`
- `C:\Program Files\WinRAR\x86\Default32.SFX`

The 32-bit SFX stub (`Default32.SFX`) is required for Windows XP compatibility. 64-bit or newer stubs will fail on XP.

**rcedit**

Used to embed the custom icon into the SFX stub before WinRAR appends the archive data. Modifying PE resources after the archive has been appended would corrupt it.

Available via Chocolatey:

```powershell
choco install rcedit
```

Expected at: `C:\ProgramData\chocolatey\bin\rcedit.exe`

**Microsoft VC++ 2008 Runtime (VC90, x86)**

Required by the Python 2.7 runtime on Windows XP. Copied automatically from `C:\Windows\WinSxS\x86_microsoft.vc90.crt_*` during the build.

### Output

`dist\UpdateRootCertificates.exe` — a self-extracting archive that extracts to `%TEMP%\UpdateRootCertificates` and runs automatically.
