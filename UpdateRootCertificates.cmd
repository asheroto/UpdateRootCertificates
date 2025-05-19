:: Author: asheroto
:: Project: https://github.com/asheroto/UpdateRootCertificates
:: Version 3.1.0
:: This program updates the trusted and disallowed root certificates on your system
:: by downloading and installing the latest versions directly from Microsoft.
:: These certificates are used by Windows to determine whether to trust or block
:: websites, software, and other secure communications. By installing them manually,
:: this tool ensures your system has the latest root certificates without relying on Windows Update.

@echo off
title Update Root Certificates

echo This script is compatible with Windows XP, Vista, 7, 8. It will not work on Windows 10 or newer.

echo Opening certificate download links in your browser...
start "" "http://www.download.windowsupdate.com/msdownload/update/v3/static/trustedr/en/authroots.sst"
start "" "http://www.download.windowsupdate.com/msdownload/update/v3/static/trustedr/en/delroots.sst"
start "" "http://www.download.windowsupdate.com/msdownload/update/v3/static/trustedr/en/disallowedcert.sst"
start "" "http://www.download.windowsupdate.com/msdownload/update/v3/static/trustedr/en/roots.sst"
start "" "http://www.download.windowsupdate.com/msdownload/update/v3/static/trustedr/en/updroots.sst"

echo.
echo Download all .sst files into the same folder as this script.
echo Press any key once all files are downloaded, or press Ctrl+C to cancel.
pause >nul

echo Updating root certificates...

updroots authroots.sst
updroots updroots.sst
updroots -l roots.sst
updroots -d delroots.sst
updroots -l -u disallowedcert.sst

echo.
echo Update complete. A reboot is recommended for changes to take effect.
pause