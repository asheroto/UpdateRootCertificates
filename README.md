[![Release](https://img.shields.io/github/v/release/asheroto/Root-Certificate-Updater)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/asheroto/Root-Certificate-Updater)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Downloads - All Releases](https://img.shields.io/github/downloads/asheroto/Root-Certificate-Updater/total)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Sponsor](https://img.shields.io/github/sponsors/asheroto?label=Sponsor&logo=GitHub)](https://github.com/sponsors/asheroto?frequency=one-time&sponsor=asheroto)
<a href="https://ko-fi.com/asheroto"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Ko-Fi Button" height="20px"></a>
<a href="https://www.buymeacoffee.com/asheroto"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=Root-Certificate-Updater&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)" height="40px"></a>

> [!NOTE]
> UpdateRootCertificates has undergone a major transition. It no longer relies on .NET Framework dependencies or pre-packaged certificate trust lists. It is now fully Python-based and dynamically fetches the latest certificate trust lists directly from Microsoft, downloading and installing the current certificates at runtime. This approach is more reliable than relying on Windows' automatic certificate download mechanism, which is supposed to handle this but does not reliablywork on older systems.

# UpdateRootCertificates (Root Certificate Updater)

Rebuilds the Windows root certificate trust store using current data from Microsoft. No external tools, no dependencies, no installation, no Windows Update required.

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

## What it does

UpdateRootCertificates downloads Microsoft's current trust list CAB files, extracts them, and writes the certificates directly to the Windows registry certificate store. No third-party tools are required.

It handles the two trust lists published by Microsoft:

1. `authrootstl.cab` — trusted root certificates, written to `HKLM\SOFTWARE\Microsoft\SystemCertificates\ROOT\Certificates`
2. `disallowedcertstl.cab` — revoked and explicitly disallowed certificates

For the trusted root list, the tool:

1. Downloads and extracts the CAB file using `expand.exe`
2. Parses the CTL to extract the thumbprints of all trusted certificates
3. Downloads each individual `.crt` file in parallel from Microsoft's CDN
4. Writes each certificate directly to the registry

For the disallowed list, the tool downloads and parses the CTL in the same way, then removes any matching certificates from the trusted root store. Microsoft does not publish the raw bytes for disallowed certificates on their CDN, so the Disallowed store cannot be populated directly.

A log file is written to `%TEMP%\UpdateRootCertificates.log`.

## Limitations

This tool is not a perfect or complete solution.

- **It does not remove outdated trusted roots.** Certificates already in the trust store that are no longer in Microsoft's current list are left in place. If needed, these can be removed manually via `certmgr.msc` or the registry under `HKLM\SOFTWARE\Microsoft\SystemCertificates\ROOT\Certificates`.
- **Disallowed certs are handled by removal, not by populating the Disallowed store.** Microsoft does not publish the raw certificate bytes for blocked certs on their CDN, so the Disallowed store cannot be populated directly. Instead, any disallowed certificates found in the trusted root store are deleted. This provides equivalent protection for the common case.
- **A reboot is required for changes to take full effect.** Some applications and system components cache certificate store state and will not pick up changes until the system is restarted.

## Usage

Run the executable directly. No arguments are required.

```
UpdateRootCertificates.exe
```

Pass `-v` or `--verbose` to print detailed output including download URLs, byte counts, and per-certificate results:

```
UpdateRootCertificates.exe --verbose
```

When run interactively (double-clicked or from a terminal), the tool pauses at the end and waits for Enter before closing.

## Features

- No external dependencies
- Writes certificates directly to the Windows registry
- No `updroots.exe`, no `certutil`, no OpenSSL
- Does not require Windows Update
- Does not require installation
- Works on Windows XP through Windows 11
- Useful for legacy, offline, restricted, and recovery scenarios
- Requires internet access to reach `ctldl.windowsupdate.com`

## Building

Build the release artifact (`dist\UpdateRootCertificates.exe`) with:

```powershell
.\build.ps1
```

### Prerequisites

**Python 2.7 (32-bit)**

Required to support Windows XP through Windows 11 with a single binary. PyInstaller packages it into a self-contained executable.

Expected at:
- `C:\Python27\python.exe`
- or `C:\Program Files (x86)\Python27\python.exe`

**PyInstaller 3.4**

Last version with reliable Windows XP compatibility. Installed automatically by the build script.

**Microsoft VC++ 2008 Runtime (VC90, x86)**

Required by the Python 2.7 runtime on Windows XP. Bundled automatically by PyInstaller from `C:\Windows\WinSxS\x86_microsoft.vc90.crt_*` as a private assembly.

### Output

`dist\UpdateRootCertificates.exe` — a single self-contained executable. No installer, no extraction step, no external dependencies.