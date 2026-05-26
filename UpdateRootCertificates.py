# UpdateRootCertificates
# Created by asheroto
# https://github.com/asheroto/UpdateRootCertificates
# Version 5.1.0
#
# Rebuilds the Windows root certificate trust store using current data from
# Microsoft. Downloads authrootstl.cab and disallowedcertstl.cab, parses the
# certificate trust lists, and writes the results directly to the registry.
# Compatible with Windows XP through Windows 11.
#
# --download-only [DIR]  Download certs to DIR on a machine with internet
#                        access; no registry changes, no admin required.
#                        Default DIR: RootCertificates (current folder).
# --source <DIR>         Apply certs from DIR (flash drive, UNC path, etc.)
#                        instead of downloading from Microsoft CDN.

import os
import sys
import shutil
import argparse
import subprocess
import tempfile
import traceback
import ctypes
import struct
import binascii
import threading

try:
    import winreg
except ImportError:
    import _winreg as winreg

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

try:
    from multiprocessing.dummy import Pool as ThreadPool
except ImportError:
    ThreadPool = None

LOG_FILE  = os.path.join(os.environ.get("TEMP", "C:\\"), "UpdateRootCertificates.log")
_log_lock = threading.Lock()

AUTHROOT_CAB_URL = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/authrootstl.cab"
CERT_CDN_URL     = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/%s.crt"

ROOT_REG_PATH = r"SOFTWARE\Microsoft\SystemCertificates\ROOT\Certificates"

THREAD_COUNT = 16
VERBOSE      = False
DEBUG        = False


# -- Logging -------------------------------------------------------------------

def log(msg):
    with _log_lock:
        try:
            with open(LOG_FILE, "a") as f:
                f.write(msg + "\n")
        except Exception:
            pass


def status(msg):
    """Always print to console and log to file."""
    print(msg)
    log(msg)


def verbose(msg):
    """Print to console only in verbose mode; always log to file."""
    if VERBOSE:
        print(msg)
    log(msg)


def debug(msg):
    """Print to console only in debug mode; always log to file."""
    if DEBUG:
        print(msg)
    log(msg)


# -- Download ------------------------------------------------------------------

def download_file(url, dest):
    verbose("  Downloading: %s" % url)
    try:
        urlretrieve(url, dest)
    except Exception as e:
        raise Exception(
            "Could not download %s: %s\n\n"
            "If this keeps failing, try disabling TCP Checksum Offload on your "
            "network adapter in Device Manager, then restart the computer." % (url, str(e))
        )
    if not os.path.exists(dest) or os.path.getsize(dest) == 0:
        raise Exception(
            "Download was empty: %s\n\n"
            "If this keeps failing, try disabling TCP Checksum Offload on your "
            "network adapter in Device Manager, then restart the computer." % url
        )
    verbose("  Downloaded %d bytes to %s" % (os.path.getsize(dest), dest))


def download_bytes(url, timeout=30):
    """Thread-safe download; returns raw bytes or None on error."""
    try:
        resp = urlopen(url, timeout=timeout)
        return resp.read()
    except Exception:
        return None


# -- CAB extraction ------------------------------------------------------------

def extract_cab(cab_path, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    verbose("  Extracting: %s" % cab_path)
    if VERBOSE:
        ret = subprocess.call(["expand.exe", cab_path, "-F:*", dest_dir])
    else:
        with open(os.devnull, "w") as devnull:
            ret = subprocess.call(
                ["expand.exe", cab_path, "-F:*", dest_dir],
                stdout=devnull, stderr=devnull
            )
    if ret != 0:
        raise Exception("expand.exe failed (code %d)" % ret)
    files = os.listdir(dest_dir)
    if not files:
        raise Exception("No files extracted from %s" % cab_path)
    extracted = os.path.join(dest_dir, files[0])
    if not extracted.lower().endswith(".stl"):
        renamed = os.path.splitext(extracted)[0] + ".stl"
        os.rename(extracted, renamed)
        extracted = renamed
    return extracted


# -- DER / CTL parsing ---------------------------------------------------------

def der_read(data, offset):
    """Read one DER TLV. Returns (tag, value_bytearray, next_offset)."""
    tag = data[offset]
    offset += 1
    b = data[offset]
    offset += 1
    if b & 0x80:
        n = b & 0x7F
        length = 0
        for _ in range(n):
            length = (length << 8) | data[offset]
            offset += 1
    else:
        length = b
    return tag, data[offset:offset + length], offset + length


def extract_ctl_bytes(pkcs7_data):
    """Strip PKCS#7 SignedData envelope. Returns raw CTL bytes."""
    data = bytearray(pkcs7_data)

    # ContentInfo SEQUENCE
    tag, val, _ = der_read(data, 0)
    if tag != 0x30:
        raise Exception("Expected ContentInfo SEQUENCE, got 0x%02X" % tag)
    data = bytearray(val)

    # contentType OID -- skip
    tag, _, offset = der_read(data, 0)
    if tag != 0x06:
        raise Exception("Expected OID, got 0x%02X" % tag)

    # [0] EXPLICIT content
    tag, val, _ = der_read(data, offset)
    if tag != 0xA0:
        raise Exception("Expected [0] content, got 0x%02X" % tag)
    data = bytearray(val)

    # SignedData SEQUENCE
    tag, val, _ = der_read(data, 0)
    if tag != 0x30:
        raise Exception("Expected SignedData SEQUENCE, got 0x%02X" % tag)
    data = bytearray(val)

    # version INTEGER -- skip
    tag, _, offset = der_read(data, 0)

    # digestAlgorithms SET -- skip
    tag, _, offset = der_read(data, offset)

    # encapContentInfo SEQUENCE
    tag, val, _ = der_read(data, offset)
    if tag != 0x30:
        raise Exception("Expected encapContentInfo SEQUENCE, got 0x%02X" % tag)
    data = bytearray(val)

    # eContentType OID -- skip
    tag, _, offset = der_read(data, 0)

    # [0] EXPLICIT eContent
    tag, val, _ = der_read(data, offset)
    if tag != 0xA0:
        raise Exception("Expected [0] eContent, got 0x%02X" % tag)
    data = bytearray(val)

    # eContent: OCTET STRING wrapping CTL (PKCS#7 / RFC 2315)
    # or CTL SEQUENCE directly (CMS / RFC 5652)
    tag, val, _ = der_read(data, 0)
    if tag == 0x04:
        return bytes(val)
    return bytes(data)


def parse_ctl_thumbprints(ctl_bytes):
    """
    Walk the CTL SEQUENCE to locate the trustedSubjects SEQUENCE, then
    extract the 20-byte SHA-1 thumbprint from each TrustedSubject entry.

    CTL structure (abridged):
      SEQUENCE {                       -- CertificateTrustList
        SEQUENCE { OID }               -- subjectUsage
        OCTET STRING                   -- listIdentifier (optional)
        INTEGER                        -- sequenceNumber (optional)
        UTCTime / GeneralizedTime      -- thisUpdate
        UTCTime / GeneralizedTime      -- nextUpdate (optional)
        SEQUENCE { OID }               -- subjectAlgorithm (SHA-1)
        SEQUENCE {                     -- trustedSubjects  <-- we want this
          SEQUENCE {
            OCTET STRING (20 bytes)    -- SHA-1 thumbprint
            SET { ... }                -- attributes
          }
          ...
        }
        [0] { ... }                    -- extensions (optional)
      }

    We identify trustedSubjects by scanning for a SEQUENCE whose first
    child is a SEQUENCE whose first child is a 20-byte OCTET STRING.
    """
    data = bytearray(ctl_bytes)

    tag, val, _ = der_read(data, 0)
    if tag != 0x30:
        raise Exception("Expected CTL SEQUENCE, got 0x%02X" % tag)
    data = bytearray(val)

    thumbprints = []
    offset = 0
    seq_index = 0
    while offset < len(data):
        prev_offset = offset
        tag, val, offset = der_read(data, offset)
        if tag != 0x30 or not val:
            debug("  [debug] seq[%d] offset=%d tag=0x%02X len=%d -- skipped (not SEQUENCE or empty)" % (seq_index, prev_offset, tag, len(val) if val else 0))
            seq_index += 1
            continue

        # Peek at first child of this SEQUENCE
        inner = bytearray(val)
        try:
            c1tag, c1val, _ = der_read(inner, 0)
        except Exception:
            debug("  [debug] seq[%d] offset=%d len=%d -- skipped (could not read first child)" % (seq_index, prev_offset, len(val)))
            seq_index += 1
            continue

        # trustedSubjects: first child is a SEQUENCE (TrustedSubject)
        if c1tag != 0x30 or not c1val:
            debug("  [debug] seq[%d] offset=%d len=%d -- skipped (first child tag=0x%02X, not SEQUENCE)" % (seq_index, prev_offset, len(val), c1tag))
            seq_index += 1
            continue

        # TrustedSubject: first child is a 20-byte OCTET STRING (thumbprint)
        inner2 = bytearray(c1val)
        try:
            t2, v2, _ = der_read(inner2, 0)
        except Exception:
            debug("  [debug] seq[%d] offset=%d len=%d -- skipped (could not read grandchild)" % (seq_index, prev_offset, len(val)))
            seq_index += 1
            continue

        if t2 != 0x04 or not (16 <= len(v2) <= 64):
            debug("  [debug] seq[%d] offset=%d len=%d -- skipped (grandchild tag=0x%02X len=%d, not 16-64 byte OCTET STRING)" % (seq_index, prev_offset, len(val), t2, len(v2)))
            seq_index += 1
            continue

        # Found trustedSubjects -- extract all thumbprints
        debug("  [debug] seq[%d] offset=%d len=%d -- MATCHED as trustedSubjects (first OCTET STRING is %d bytes)" % (seq_index, prev_offset, len(val), len(v2)))
        ioffset = 0
        while ioffset < len(inner):
            stag, sval, ioffset = der_read(inner, ioffset)
            if stag != 0x30 or not sval:
                continue
            try:
                ttag, tval, _ = der_read(bytearray(sval), 0)
                if ttag == 0x04 and 16 <= len(tval) <= 64:
                    hex_val = binascii.hexlify(bytes(tval)).decode("ascii")
                    debug("  [debug] thumbprint %d bytes: %s" % (len(tval), hex_val.upper()))
                    thumbprints.append(hex_val)
                elif DEBUG:
                    debug("  [debug] skipped entry: tag=0x%02X len=%d" % (ttag, len(tval)))
            except Exception:
                pass
        break

    return thumbprints


# -- Registry import -----------------------------------------------------------

def make_cert_blob(der_bytes):
    """
    Build the registry Blob value for a certificate entry.
    Format: [DWORD propId][DWORD flags][DWORD size][BYTE... data]
    propId 32 (0x20) = CERT_CERT_PROP_ID (the raw DER certificate)
    """
    header = struct.pack("<III", 32, 1, len(der_bytes))
    return header + der_bytes


def write_cert_to_registry(reg_path, thumbprint_upper, der_bytes):
    key_path = reg_path + "\\" + thumbprint_upper
    blob = make_cert_blob(der_bytes)
    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
    try:
        winreg.SetValueEx(key, "Blob", 0, winreg.REG_BINARY, blob)
    finally:
        winreg.CloseKey(key)


# -- Store processing ----------------------------------------------------------

def process_authroot(cab_url, cert_cdn_url, reg_path, work_dir):
    """
    Full pipeline for the trusted root store:
      1. Download CAB and extract STL
      2. Parse CTL to get SHA-1 thumbprints
      3. Download each cert in parallel from Microsoft CDN
      4. Write each cert directly to the registry certificate store
    """
    cab_path = os.path.join(work_dir, "authroot.cab")
    stl_dir  = os.path.join(work_dir, "authroot")

    status("  Downloading trust list...")
    download_file(cab_url, cab_path)
    stl_path = extract_cab(cab_path, stl_dir)

    with open(stl_path, "rb") as f:
        raw = f.read()

    ctl_bytes = extract_ctl_bytes(raw)
    verbose("  CTL: %d bytes" % len(ctl_bytes))

    thumbprints = parse_ctl_thumbprints(ctl_bytes)
    if not thumbprints:
        status("  No certificates found in trust list -- skipping")
        return
    status("  Found %d certificates" % len(thumbprints))
    for t in sorted(thumbprints):
        verbose("    %s" % t.upper())

    # -- Parallel cert download ------------------------------------------------
    total = len(thumbprints)
    status("  Downloading certificates...")
    results = {}
    results_lock = threading.Lock()
    completed = [0]

    def fetch(thumb):
        data = download_bytes(cert_cdn_url % thumb)
        with results_lock:
            results[thumb] = data
            completed[0] += 1
            sys.stdout.write("\r  %d/%d downloaded" % (completed[0], total))
            sys.stdout.flush()

    if ThreadPool:
        pool = ThreadPool(THREAD_COUNT)
        pool.map(fetch, thumbprints)
        pool.close()
        pool.join()
    else:
        for t in thumbprints:
            fetch(t)

    sys.stdout.write("\n")
    sys.stdout.flush()

    ok   = sum(1 for v in results.values() if v)
    miss = len(thumbprints) - ok
    verbose("  Downloaded %d, unavailable on CDN: %d" % (ok, miss))

    # -- Write to registry -----------------------------------------------------
    status("  Writing to registry...")
    added  = 0
    failed = 0
    for thumb in thumbprints:
        der = results.get(thumb)
        if not der:
            continue
        try:
            write_cert_to_registry(reg_path, thumb.upper(), der)
            added += 1
        except Exception as e:
            verbose("  Registry write failed for %s: %s" % (thumb, str(e)))
            failed += 1

    parts = ["%d added" % added]
    if failed:
        parts.append("%d failed" % failed)
    if miss:
        parts.append("%d unavailable on CDN" % miss)
    status("  Done: %s" % ", ".join(parts))


# -- Download-only mode --------------------------------------------------------

def run_download_only(cab_url, cert_cdn_url, dest_dir):
    """
    Download the CAB, STL, and all .crt files to dest_dir.
    Does not require admin rights and does not touch the registry.
    Run on a machine with internet access, then transfer dest_dir to the
    target machine and apply with --source.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    work_dir = os.path.join(tempfile.gettempdir(), "UpdateRootCertificates_tmp")
    rmtree(work_dir)
    os.makedirs(work_dir)

    try:
        cab_path = os.path.join(work_dir, "authroot.cab")
        stl_dir  = os.path.join(work_dir, "authroot")

        status("  Downloading trust list...")
        download_file(cab_url, cab_path)
        stl_path = extract_cab(cab_path, stl_dir)

        shutil.copy2(cab_path, os.path.join(dest_dir, "authroot.cab"))
        shutil.copy2(stl_path, os.path.join(dest_dir, "authroot.stl"))
        verbose("  Saved authroot.cab and authroot.stl to %s" % dest_dir)

        with open(stl_path, "rb") as f:
            raw = f.read()

        ctl_bytes   = extract_ctl_bytes(raw)
        thumbprints = parse_ctl_thumbprints(ctl_bytes)

        if not thumbprints:
            status("  No certificates found in trust list")
            return

        status("  Found %d certificates" % len(thumbprints))
        status("  Downloading certificates...")

        total        = len(thumbprints)
        completed    = [0]
        saved        = [0]
        results_lock = threading.Lock()

        def fetch_and_save(thumb):
            data = download_bytes(cert_cdn_url % thumb)
            with results_lock:
                completed[0] += 1
                if data:
                    crt_path = os.path.join(dest_dir, thumb.upper() + ".crt")
                    with open(crt_path, "wb") as fh:
                        fh.write(data)
                    saved[0] += 1
                sys.stdout.write("\r  %d/%d downloaded" % (completed[0], total))
                sys.stdout.flush()

        if ThreadPool:
            pool = ThreadPool(THREAD_COUNT)
            pool.map(fetch_and_save, thumbprints)
            pool.close()
            pool.join()
        else:
            for t in thumbprints:
                fetch_and_save(t)

        sys.stdout.write("\n")
        sys.stdout.flush()

        miss = len(thumbprints) - saved[0]
        status("  Saved %d certificates to: %s" % (saved[0], dest_dir))
        if miss:
            status("  %d certificates unavailable on CDN (skipped)" % miss)

    finally:
        rmtree(work_dir)


# -- Offline source mode -------------------------------------------------------

def run_from_source(source_dir, reg_path):
    """
    Apply trusted root certificates from a local directory produced by
    --download-only.  source_dir must contain authroot.stl (or authroot.cab)
    and <THUMBPRINT>.crt files.
    """
    work_dir = os.path.join(tempfile.gettempdir(), "UpdateRootCertificates_tmp")
    rmtree(work_dir)
    os.makedirs(work_dir)

    try:
        stl_src = os.path.join(source_dir, "authroot.stl")
        cab_src = os.path.join(source_dir, "authroot.cab")

        if os.path.exists(stl_src):
            stl_path = stl_src
            verbose("  Using STL: %s" % stl_path)
        elif os.path.exists(cab_src):
            stl_dir  = os.path.join(work_dir, "authroot")
            stl_path = extract_cab(cab_src, stl_dir)
            verbose("  Extracted STL from: %s" % cab_src)
        else:
            raise Exception(
                "Source directory does not contain authroot.stl or authroot.cab.\n"
                "Run with --download-only on a machine with internet access first.\n"
                "Source: %s" % source_dir
            )

        with open(stl_path, "rb") as f:
            raw = f.read()

        ctl_bytes   = extract_ctl_bytes(raw)
        thumbprints = parse_ctl_thumbprints(ctl_bytes)

        if not thumbprints:
            status("  No certificates found in trust list -- skipping")
            return

        status("  Found %d certificates in trust list" % len(thumbprints))
        status("  Applying certificates from source...")

        added   = 0
        failed  = 0
        missing = 0

        for thumb in thumbprints:
            crt_path = os.path.join(source_dir, thumb.upper() + ".crt")
            if not os.path.exists(crt_path):
                verbose("  Missing: %s.crt" % thumb.upper())
                missing += 1
                continue
            try:
                with open(crt_path, "rb") as fh:
                    der = fh.read()
                write_cert_to_registry(reg_path, thumb.upper(), der)
                added += 1
            except Exception as e:
                verbose("  Registry write failed for %s: %s" % (thumb.upper(), str(e)))
                failed += 1

        parts = ["%d added" % added]
        if failed:
            parts.append("%d failed" % failed)
        if missing:
            parts.append("%d missing from source" % missing)
        status("  Done: %s" % ", ".join(parts))

    finally:
        rmtree(work_dir)


# -- Cleanup -------------------------------------------------------------------

def rmtree(path):
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except Exception:
                    pass
        try:
            os.rmdir(path)
        except Exception:
            pass


# -- Console helpers -----------------------------------------------------------

def interactive():
    """True if stdout is connected to a terminal (interactive use)."""
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def pause():
    print("")
    try:
        raw_input("Press Enter to close...")
    except NameError:
        input("Press Enter to close...")


# -- Entry point ---------------------------------------------------------------

def main():
    log("=== START ===")

    WORK_DIR = os.path.join(tempfile.gettempdir(), "UpdateRootCertificates_tmp")
    rmtree(WORK_DIR)
    os.makedirs(WORK_DIR)
    verbose("  Work dir: %s" % WORK_DIR)

    try:
        print("")
        status("[AuthRoot]")
        process_authroot(AUTHROOT_CAB_URL, CERT_CDN_URL, ROOT_REG_PATH, WORK_DIR)
    finally:
        rmtree(WORK_DIR)
        log("Work dir removed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rebuilds the Windows root certificate trust store using current data from Microsoft."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed output including thumbprints and per-certificate results"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print low-level DER parsing diagnostics (implies --verbose)"
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version="UpdateRootCertificates v5.1.0 by asheroto"
    )
    parser.add_argument(
        "--download-only",
        nargs="?",
        const="RootCertificates",
        metavar="DIR",
        help=(
            "Download certificates to DIR without applying them to the registry. "
            "No admin rights required. Run on a machine with internet access, then "
            "transfer DIR to the target machine and use --source to apply. "
            "Saves authroot.cab, authroot.stl, and all .crt files. "
            "Default DIR: RootCertificates (in the current folder)"
        )
    )
    parser.add_argument(
        "--source",
        metavar="DIR",
        help=(
            "Apply certificates from DIR instead of downloading from Microsoft CDN. "
            "Supports local folders, UNC paths, and flash drives. "
            "DIR must contain authroot.stl (or authroot.cab) and the .crt files "
            "produced by --download-only."
        )
    )
    args = parser.parse_args()
    DEBUG   = args.debug
    VERBOSE = args.verbose or args.debug

    print("UpdateRootCertificates v5.1.0 by asheroto")
    print("https://github.com/asheroto/UpdateRootCertificates")

    try:
        log("Launching...")

        if args.download_only is not None:
            dest = os.path.abspath(args.download_only)
            print("")
            status("[AuthRoot] Download-only mode")
            status("  Destination: %s" % dest)
            run_download_only(AUTHROOT_CAB_URL, CERT_CDN_URL, dest)
            log("DONE")
            print("")
            print("Download complete.")
            print("Transfer this folder to the target machine, then run:")
            print('  UpdateRootCertificates.py --source "%s"' % dest)
            print("")
            print("Log: %s" % LOG_FILE)

        elif args.source:
            src = os.path.abspath(args.source)
            if not os.path.isdir(src):
                raise Exception("Source directory not found: %s" % src)
            print("")
            status("[AuthRoot] Offline source mode")
            status("  Source: %s" % src)
            run_from_source(src, ROOT_REG_PATH)
            log("DONE")
            print("")
            print("Complete.")
            print("A reboot is required for changes to take full effect.")
            print("")
            print("Log: %s" % LOG_FILE)

        else:
            main()
            log("DONE")
            print("")
            print("Complete.")
            print("A reboot is required for changes to take full effect.")
            print("")
            print("Log: %s" % LOG_FILE)

    except KeyboardInterrupt:
        log("Cancelled by user")
        print("")
        print("Cancelled.")
        sys.exit(1)
    except Exception as e:
        log("FATAL: %s" % str(e))
        log(traceback.format_exc())
        print("")
        print("ERROR: %s" % str(e))
        print("")
        print("Log: %s" % LOG_FILE)
        try:
            msg = u"Update failed: %s\n\nSee log: %s" % (str(e), LOG_FILE)
            ctypes.windll.user32.MessageBoxW(0, msg, u"UpdateRootCertificates", 0x10)
        except Exception:
            pass
        if interactive():
            pause()
        sys.exit(1)

    if interactive():
        pause()
