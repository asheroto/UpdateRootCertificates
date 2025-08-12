[![Release](https://img.shields.io/github/v/release/asheroto/Root-Certificate-Updater)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/asheroto/Root-Certificate-Updater)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Downloads - All Releases](https://img.shields.io/github/downloads/asheroto/Root-Certificate-Updater/total)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Sponsor](https://img.shields.io/github/sponsors/asheroto?label=Sponsor&logo=GitHub)](https://github.com/sponsors/asheroto?frequency=one-time&sponsor=asheroto)
<a href="https://ko-fi.com/asheroto"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Ko-Fi Button" height="20px"></a>
<a href="https://www.buymeacoffee.com/asheroto"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=Root-Certificate-Updater&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)" height="40px"></a>

# UpdateRootCertificates (Root Certificate Updater)

Update root and disallowed certificates on Windows. No system settings are changed, and Windows Update is **not** required.

**The PowerShell and CMD versions are now deprecated** due to compatibility and dependency issues on some systems. The recommended method going forward is the standalone EXE.

## Features

* Updates trusted and disallowed root certificates
* Does **not** require Windows Update
* Does **not** alter any Windows settings
* Works on Windows XP through 11
* No installation required

## Prerequisites
This tool requires the .NET Framework.

For Windows XP/7, install [.NET Framework 4.0](https://www.microsoft.com/en-us/download/details.aspx?id=17718&msockid=29520b892cd865e332cb1eae2d0e64c0) if it is not already installed.

While .NET Framework 4.8 is preferred, it requires a trusted root certificate, so version 4.0 is generally the most compatible choice.

## Download

The EXE version is the easiest and most compatible method.

[Download the latest version (ZIP)](https://github.com/asheroto/UpdateRootCertificates/releases/latest/download/UpdateRootCertificates.zip)

**ZIP Password:** `password` (used to avoid false positives from antivirus software)

### Screenshot
![UpdateRootCertificates.exe](https://github.com/user-attachments/assets/62538129-a827-4665-9735-87c8398f7e7f)

---

## Version Support Table

| Version                      | Supported OS    | Notes                                |
| ---------------------------- | --------------- | ------------------------------------ |
| `RootCertificateUpdater.exe` | Windows XP – 11 | Recommended method                   |
| `UpdateRootCertificates.ps1` | Windows 7 – 11  | Deprecated; requires PowerShell 5.1+ |
| `UpdateRootCertificates.cmd` | Windows XP – 8  | Deprecated; requires `updroots.exe`  |

---

## Deprecated: PowerShell and CMD Versions

These options are still available for legacy use but are no longer maintained.

### PowerShell Script (`UpdateRootCertificates.ps1`)

> ⚠️ Deprecated. Use the EXE version instead.

Still available on [PowerShell Gallery](https://www.powershellgallery.com/packages/UpdateRootCertificates).

#### Usage

```powershell
Install-Script UpdateRootCertificates -Force
UpdateRootCertificates -CheckForUpdate
```

| Command                  | Description                     |
| ------------------------ | ------------------------------- |
| `UpdateRootCertificates` | Normal execution                |
| `-Force`                 | Skips wait time before running  |
| `-Verbose`               | Shows detailed log output       |
| `-CheckForUpdate`        | Checks for a newer version      |
| `-UpdateSelf`            | Updates the script from Gallery |
| `-Version`               | Shows current script version    |
| `-Help`                  | Shows usage info                |

### Batch Script (`UpdateRootCertificates.cmd`)

> ⚠️ Deprecated. Use only on Windows XP–8 where `updroots.exe` is available.

* Opens certificate download links in browser
* Requires manual interaction
* Supports cert removal (`updroots -d`)
