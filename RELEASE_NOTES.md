## v5.1.0

### New features

**Offline / air-gapped deployment workflow**

Two new flags enable a two-step workflow for machines that cannot reach the internet.

`--download-only [DIR]` - Download all certificates to a local folder without touching the registry. No admin rights required. Run this on any machine with internet access.

```
UpdateRootCertificates.exe --download-only
```

Saves `authroot.cab`, `authroot.stl`, and all `.crt` files to `RootCertificates\` in the current directory (or a custom path if specified). Transfer the folder to the target machine via USB drive, network share, UNC path, or any other method.

`--source <DIR>` - Apply certificates from a folder produced by `--download-only` instead of downloading from Microsoft. Useful for offline, restricted, or air-gapped environments. Admin rights required.

```
UpdateRootCertificates.exe --source C:\path\to\folder
```

The source directory must contain `authroot.stl` (or `authroot.cab`) and the `.crt` files from the download step.

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
