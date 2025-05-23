[![Release](https://img.shields.io/github/v/release/asheroto/Root-Certificate-Updater)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/asheroto/Root-Certificate-Updater)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Downloads - All Releases](https://img.shields.io/github/downloads/asheroto/Root-Certificate-Updater/total)](https://github.com/asheroto/Root-Certificate-Updater/releases)
[![GitHub Sponsor](https://img.shields.io/github/sponsors/asheroto?label=Sponsor&logo=GitHub)](https://github.com/sponsors/asheroto?frequency=one-time&sponsor=asheroto)
<a href="https://ko-fi.com/asheroto"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Ko-Fi Button" height="20px"></a>
<a href="https://www.buymeacoffee.com/asheroto"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=Root-Certificate-Updater&button_colour=FFDD00&font_colour=000000&font_family=Lato&outline_colour=000000&coffee_colour=ffffff)" height="40px"></a>

# UpdateRootCertificates (Root Certificate Updater)

> [!NOTE]
> We are in transition back to the EXE version. Please see release version 2.0 with the EXE version if you have issues with the CMD or PowerShell versions.

Update root certificates (and disallowed certificates) on Windows.

**No changes are made to any system settings**, and **Windows Update is NOT required** for this to work.

![screenshot](https://github.com/user-attachments/assets/7c7cdd5b-fe76-47e5-8895-33126dc33b3a)

## Version Differences

This project includes two versions. The PowerShell script is generally recommended, but the batch file version is included for compatibility with older systems 

- **PowerShell script (`UpdateRootCertificates.ps1`)**  
  - Runs silently (no interaction required)
  - Does not open a web browser  
  - Checks registry settings related to certificate auto-update  
  - Supports parameters like `-Verbose`, `-CheckForUpdate`, and `-UpdateSelf`  
  - Does **not** remove root certificates (PowerShell has no equivalent to `updroots -d`)  
    - This has minimal impact, because untrusted or revoked certificates are still applied via `disallowedcert.sst`, which adds entries to the Disallowed store and effectively blocks them
  - Compatible with Windows 7 through 11 (PowerShell 5.1 required; included by default in Windows 10 and 11)

- **Batch script (`UpdateRootCertificates.cmd`)**  
  - Opens certificate download links in the default browser  
  - User must manually save the `.sst` files into the script folder  
  - Prompts for user input and cannot run fully silently  
  - Supports removal of outdated root certs via `updroots -d`  
  - Compatible with Windows XP through 8 (requires `updroots.exe`, which is not available in Windows 10 or newer)

## Running the Script

You can run the script using either version, depending on your operating system:

- **PowerShell script (`UpdateRootCertificates.ps1`)**  
  Recommended for Windows 7 and newer. You can either:
  
  - Download the [latest code-signed release](https://github.com/asheroto/Root-Certificate-Updater/releases/latest/download/UpdateRootCertificates.ps1)

    **OR**

  - Install it from PowerShell Gallery using:
  
    ```powershell
    Install-Script UpdateRootCertificates -Force
    ```

  Published here: [PowerShell Gallery – UpdateRootCertificates](https://www.powershellgallery.com/packages/UpdateRootCertificates)

- **Batch script (`UpdateRootCertificates.cmd`)**  
  Use this version only on Windows XP through 8, where `updroots.exe` is available.  
  Just double-click the `.cmd` file and follow the on-screen instructions.

## PowerShell Version Usage

| Command                                  | Description                                                      |
| ---------------------------------------- | ---------------------------------------------------------------- |
| `UpdateRootCertificates`                 | Normal execution                                                 |
| `UpdateRootCertificates -Force`          | Skips the 10-second wait before running                          |
| `UpdateRootCertificates -Verbose`        | Shows detailed output during certificate installation            |
| `UpdateRootCertificates -CheckForUpdate` | Checks for the latest version of the script                      |
| `UpdateRootCertificates -UpdateSelf`     | Updates the script to the latest version from PowerShell Gallery |
| `UpdateRootCertificates -Version`        | Displays the current script version                              |
| `UpdateRootCertificates -Help`           | Displays full help documentation                                 |
