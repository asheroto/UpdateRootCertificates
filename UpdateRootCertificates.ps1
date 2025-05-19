<#PSScriptInfo

.VERSION 3.1.1

.GUID 05c58731-6a7a-4a18-9903-03530b7ec896

.AUTHOR asherto

.COMPANYNAME asheroto

.TAGS PowerShell Windows root certificates certificate update updater lists list certutil certutil.exe sst cab microsoft windows

.PROJECTURI https://github.com/asheroto/UpdateRootCertificates

.RELEASENOTES
[Version 1.11.0] - Initial PowerShell Gallery release.
[Version 1.11.1] - Fix URL to GUI counterpart.
[Version 2.0.0] - Refactored & signed code.
[Version 3.0.0] - Major rewrite.  Switched from Certificate Trusts Lists to Certificates.
[Version 3.1.0] - Added CheckForUpdate, UpdateSelf, Version, and Help parameters. Added test for admin privileges. Improved output formatting.

#>

<#
.SYNOPSIS
    Force update the root certificate lists on your computer.
.DESCRIPTION
	Downloads the latest root certificate lists from Microsoft and installs them on your computer.

	Optionally you can specify the -Force parameter to skip the 10 second wait before continuing execution.

	This program updates the trusted and disallowed root certificates on your system by downloading and installing the latest versions directly from Microsoft. These certificates are used by Windows to determine whether to trust or block websites, software, and other secure communications. By installing them manually, this tool ensures your system has the latest root certificates without relying on Windows Update.

	Its GUI counterpart is available at https://github.com/asheroto/UpdateRootCertificates
.EXAMPLE
	Update root certificate lists normally: UpdateRootCertificates.ps1
.EXAMPLE
	Update root certificate lists without waiting 10 seconds to continue execution: UpdateRootCertificates.ps1 -Force
.PARAMETER Force
    Skips the 10-second delay before certificate installation begins.
.PARAMETER Verbose
    Displays detailed output during certificate download and installation.
.PARAMETER UpdateSelf
    Automatically installs the latest version of this script from PowerShell Gallery.
.PARAMETER CheckForUpdate
    Checks for a newer version of the script and displays the release date and version info.
.PARAMETER Version
    Displays the current version of the script and exits.
.PARAMETER Help
    Displays full help documentation for this script.
.NOTES
    Version      : 3.1.0
    Created by   : asheroto
.LINK
    Project Site: https://github.com/asheroto/UpdateRootCertificates
#>

# Ensure script running as Administrator
#Requires -RunAsAdministrator

# Skip 10 second wait before continuing execution
[CmdletBinding()]
param (
	[switch]$Force,
	[switch]$CheckForUpdate,
	[switch]$UpdateSelf,
	[switch]$Version,
	[switch]$Help
)

# Script information
$CurrentVersion = '3.1.0'
$RepoOwner = 'asheroto'
$RepoName = 'UpdateRootCertificates'
$PowerShellGalleryName = 'UpdateRootCertificates'

# Preferences
$ProgressPreference = 'SilentlyContinue' # Suppress progress bar (makes downloading super fast)
$ConfirmPreference = 'None' # Suppress confirmation prompts

# Display version if -Version is specified
if ($Version.IsPresent) {
	$CurrentVersion
	exit 0
}

# Display full help if -Help is specified
if ($Help) {
	Get-Help -Name $MyInvocation.MyCommand.Source -Full
	exit 0
}
function Get-GitHubRelease {
	<#
        .SYNOPSIS
        Fetches the latest release information of a GitHub repository.

        .DESCRIPTION
        This function uses the GitHub API to get information about the latest release of a specified repository, including its version and the date it was published.

        .PARAMETER Owner
        The GitHub username of the repository owner.

        .PARAMETER Repo
        The name of the repository.

        .EXAMPLE
        Get-GitHubRelease -Owner "asheroto" -Repo "UpdateRootCertificates"
        This command retrieves the latest release version and published datetime of the UpdateRootCertificates" repository owned by asheroto.
    #>
	[CmdletBinding()]
	param (
		[string]$Owner,
		[string]$Repo
	)
	try {
		$url = "https://api.github.com/repos/$Owner/$Repo/releases/latest"
		$response = Invoke-RestMethod -Uri $url -ErrorAction Stop

		$latestVersion = $response.tag_name
		$publishedAt = $response.published_at

		# Convert UTC time string to local time
		$UtcDateTime = [DateTime]::Parse($publishedAt, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind)
		$PublishedLocalDateTime = $UtcDateTime.ToLocalTime()

		[PSCustomObject]@{
			LatestVersion     = $latestVersion
			PublishedDateTime = $PublishedLocalDateTime
		}
	} catch {
		Write-Error "Unable to check for updates.`nError: $_"
		exit 1
	}
}

function CheckForUpdate {
	param (
		[string]$RepoOwner,
		[string]$RepoName,
		[version]$CurrentVersion,
		[string]$PowerShellGalleryName
	)

	$Data = Get-GitHubRelease -Owner $RepoOwner -Repo $RepoName

	Write-Output ""
	Write-Output ("Repository:       {0,-40}" -f "https://github.com/$RepoOwner/$RepoName")
	Write-Output ("Current Version:  {0,-40}" -f $CurrentVersion)
	Write-Output ("Latest Version:   {0,-40}" -f $Data.LatestVersion)
	Write-Output ("Published at:     {0,-40}" -f $Data.PublishedDateTime)

	if ($Data.LatestVersion -gt $CurrentVersion) {
		Write-Output ("Status:           {0,-40}" -f "A new version is available.")
		Write-Output "`nOptions to update:"
		Write-Output "- Download latest release: https://github.com/$RepoOwner/$RepoName/releases"
		if ($PowerShellGalleryName) {
			Write-Output "- Run: $RepoName -UpdateSelf"
			Write-Output "- Run: Install-Script $PowerShellGalleryName -Force"
		}
	} else {
		Write-Output ("Status:           {0,-40}" -f "Up to date.")
	}
	exit 0
}

function UpdateSelf {
	try {
		# Get PSGallery version of script
		$psGalleryScriptVersion = (Find-Script -Name $PowerShellGalleryName).Version

		# If the current version is less than the PSGallery version, update the script
		if ($CurrentVersion -lt $psGalleryScriptVersion) {
			Write-Output "Updating script to version $psGalleryScriptVersion..."

			# Check if running in PowerShell 7 or greater
			Write-Debug "Checking if NuGet PackageProvider is already installed..."
			Install-NuGetIfRequired

			# Trust the PSGallery if not already trusted
			$psRepoInstallationPolicy = (Get-PSRepository -Name 'PSGallery').InstallationPolicy
			if ($psRepoInstallationPolicy -ne 'Trusted') {
				Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted | Out-Null
			}

			# Update the script
			Install-Script $PowerShellGalleryName -Force

			# If PSGallery was not trusted, reset it to its original state
			if ($psRepoInstallationPolicy -ne 'Trusted') {
				Set-PSRepository -Name 'PSGallery' -InstallationPolicy $psRepoInstallationPolicy | Out-Null
			}

			Write-Output "Script updated to version $psGalleryScriptVersion."
			exit 0
		} else {
			Write-Output "Script is already up to date."
			exit 0
		}
	} catch {
		Write-Output "An error occurred: $_"
		exit 1
	}
}

function Test-AdminPrivileges {
	<#
    .SYNOPSIS
        Checks if the script is running with Administrator privileges. Returns $true if running with Administrator privileges, $false otherwise.

    .DESCRIPTION
        This function checks if the current PowerShell session is running with Administrator privileges by examining the role of the current user. It returns $true if the current user is an Administrator, $false otherwise.

    .EXAMPLE
        Test-AdminPrivileges

    .NOTES
        This function is particularly useful for scripts that require elevated permissions to run correctly.
    #>
	if (([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
		return $true
	}
	return $false
}

function Write-Section($text) {
	<#
        .SYNOPSIS
        Prints a text block surrounded by a section divider for enhanced output readability.

        .DESCRIPTION
        This function takes a string input and prints it to the console, surrounded by a section divider made of hash characters.
        It is designed to enhance the readability of console output.

        .PARAMETER text
        The text to be printed within the section divider.

        .EXAMPLE
        Write-Section "Downloading Files..."
        This command prints the text "Downloading Files..." surrounded by a section divider.
    #>
	Write-Output ""
	Write-Output ("#" * ($text.Length + 4))
	Write-Output "# $text #"
	Write-Output ("#" * ($text.Length + 4))
	Write-Output ""
}

function Fail {
	param([string]$Message)
	Write-Warning $Message
	Write-Warning "The process failed. Make sure you're connected to the internet, running PowerShell as Administrator, and have the latest version installed."
	Write-Output ""
	Write-Output "For help, visit: https://github.com/asheroto/UpdateRootCertificates under the 'Issues' tab."
	Pop-Location
	Break
}

Clear-Host

# First heading
Write-Output "UpdateRootCertificates $CurrentVersion"

# Check for updates if -CheckForUpdate is specified
if ($CheckForUpdate) { CheckForUpdate -RepoOwner $RepoOwner -RepoName $RepoName -CurrentVersion $CurrentVersion -PowerShellGalleryName $PowerShellGalleryName }

# Update the script if -UpdateSelf is specified
if ($UpdateSelf) { UpdateSelf }

# Heading
Write-Output "To check for updates, run UpdateRootCertificates -CheckForUpdate"

# Check if the current user is an administrator
if (-not (Test-AdminPrivileges)) {
	Write-Warning "UpdateRootCertificates requires Administrator privileges to install. Please run the script as an Administrator and try again."
	ExitWithDelay 1
}

Write-Output ""
Write-Output "This script downloads and installs updated root and disallowed certificates from Microsoft."
Write-Output ""
Write-Output "These are used by Windows to determine whether to trust or reject connections, software, and other services."
Write-Output ""
Write-Output "Reference: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-trust"
Write-Output ""
Write-Output ("-" * 50)

if (-not $Force) {
	Write-Output "Updated root and disallowed certificates will be installed in 10 seconds. Press CTRL+C to cancel."
	Start-Sleep -Seconds 10
	Write-Output ("-" * 50)
}

Write-Section "Windows Update Certificate Settings"

Write-Output "Checking if Windows Update is allowed to install trusted root certificates..."
$ShowAUMessage = $true
$val = Get-ItemProperty -Path 'HKLM:\Software\Policies\Microsoft\SystemCertificates\AuthRoot' -Name 'DisableRootAutoUpdate' -ErrorAction Ignore
if ($val.DisableRootAutoUpdate -eq 1) {
	Write-Warning "Your system is configured to block automatic updates of trusted root certificates."
	Write-Output "To change this setting, check: HKLM\Software\Policies\Microsoft\SystemCertificates\AuthRoot\DisableRootAutoUpdate"
	$ShowAUMessage = $false
}
if ($ShowAUMessage) {
	Write-Output "Trusted root certificates are allowed to be updated automatically by Windows Update."
}

Write-Output ""
Write-Output "Checking if Windows Update is allowed to install disallowed certificates..."
$ShowAUMessageD = $true
$val = Get-ItemProperty -Path 'HKLM:\Software\Policies\Microsoft\SystemCertificates\AuthRoot' -Name 'EnableDisallowedCertAutoUpdate' -ErrorAction Ignore
if ($val.EnableDisallowedCertAutoUpdate -eq 0) {
	Write-Warning "Your system is configured to block automatic updates of disallowed certificates."
	Write-Output "To change this setting, check: HKLM\Software\Policies\Microsoft\SystemCertificates\AuthRoot\EnableDisallowedCertAutoUpdate"
	$ShowAUMessageD = $false
}
if ($ShowAUMessageD) {
	Write-Output "Disallowed certificates are allowed to be updated automatically by Windows Update."
}
Write-Output ("-" * 50)

Push-Location $pwd
$TempDir = [System.IO.Path]::GetTempPath()
Set-Location $TempDir

Write-Section "Downloading Certificates"

$ProgressPreference = "SilentlyContinue"
$baseUrl = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/"
$trustedFiles = @("authroots.sst", "updroots.sst", "roots.sst")
$disallowedFile = "disallowedcert.sst"

foreach ($file in $trustedFiles + $disallowedFile) {
	Invoke-WebRequest -Uri ($baseUrl + $file) -OutFile $file
	if (-not (Test-Path $file)) {
		Fail -Message "$file was not downloaded. Check your Internet connection and try again."
	}
	Write-Output "$file downloaded."
}

Write-Section "Installing Certificates"

foreach ($file in $trustedFiles) {
	if ($PSCmdlet.MyInvocation.BoundParameters["Verbose"]) {
		certutil -f -addstore root $file
	} else {
		certutil -f -addstore root $file > $null 2>&1
	}
	Write-Output "$file installed to Root store."
}

if ($PSCmdlet.MyInvocation.BoundParameters["Verbose"]) {
	certutil -f -addstore disallowed $disallowedFile
} else {
	certutil -f -addstore disallowed $disallowedFile > $null 2>&1
}
Write-Output "$disallowedFile installed to Disallowed store."

Write-Section "Cleanup"

Remove-Item authroots.sst, updroots.sst, roots.sst, disallowedcert.sst
Write-Output "Temporary files removed."

Write-Section "Completed"

Write-Output "Certificates were successfully downloaded and installed."
Write-Output "Please restart the computer for changes to fully take effect."

Pop-Location