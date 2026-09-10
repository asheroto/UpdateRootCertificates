## v5.1.1

### Bug fixes

**Fixed `LookupError: unknown encoding: cp65001` when running with `-v` / `--verbose`**

Running the executable with `-v` crashed on consoles set to UTF-8 (`chcp 65001`), such as Windows Terminal or systems with the "Use Unicode UTF-8 for worldwide language support" option enabled. Double-clicking the executable was unaffected, as was every run without `-v`.

Thumbprints parsed from the trust list were being produced as Unicode strings. Verbose mode is the only place they get printed, and Python 2 resolves the console codec lazily at that moment - on a codepage 65001 console it looks up `cp65001`, which Python 2 does not provide, and the run aborted right after `Found N certificates`.

Thumbprints are now kept as plain ASCII byte strings. The values themselves are unchanged, so certificate downloads and registry writes behave exactly as before.

Fixes [#20](https://github.com/asheroto/UpdateRootCertificates/issues/20).

---

## v5.1.0

### New features

**Offline / air-gapped deployment workflow**

Two new flags enable a two-step workflow for machines that cannot reach the internet.

`--download-only [DIR]` - Download all certificates to a local folder without touching the registry. No admin rights required. Run this on any machine with internet access.

```
UpdateRootCertificates.exe --download-only
UpdateRootCertificates.exe --download-only D:\MyFolder
UpdateRootCertificates.exe --download-only "\\server\share\certs"
```

Omitting `DIR` saves to a `RootCertificates` subfolder in the current directory. Saves `authroot.cab`, `authroot.stl`, and all `.crt` files. Transfer the folder to the target machine via USB drive, network share, UNC path, or any other method.

`--source <DIR>` - Apply certificates from a folder produced by `--download-only` instead of downloading from Microsoft. Useful for offline, restricted, or air-gapped environments. Admin rights required.

```
UpdateRootCertificates.exe --source C:\path\to\folder
UpdateRootCertificates.exe --source D:\MyFolder
UpdateRootCertificates.exe --source "\\server\share\certs"
```

`DIR` must contain `authroot.stl` (or `authroot.cab`) and the `.crt` files produced by `--download-only`.

---

## v5.0.2

- Added `-V` as a shorthand flag for `--version`

---

## v5.0.1

- Removed disallowed certificate store processing

  Microsoft's disallowed CTL (`disallowedcertstl.cab`) uses MD5 and SHA-384 subject identifiers rather than SHA-1 thumbprints. The Windows Disallowed registry store is keyed by SHA-1, so the CTL identifiers cannot be mapped to registry entries without the raw certificate DER bytes, which Microsoft does not publish on the CDN. The disallowed list also contains intermediate and end-entity certificates rather than root CAs, so they would not appear in the root store regardless. Disallowed certificate processing is skipped entirely and the limitation is documented in the README.

---

## v5.0.0

Complete rewrite in Python. No longer relies on .NET Framework dependencies or pre-packaged certificate trust lists. Dynamically fetches the latest trust lists from Microsoft and downloads and installs the current certificates at runtime.