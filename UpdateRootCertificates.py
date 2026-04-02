import os
import subprocess
import tempfile
import traceback
import ctypes

try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

LOG_FILE = os.path.join(os.environ.get("TEMP", "C:\\"), "UpdateRootCertificates.log")

AUTHROOT_CAB_URL   = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/authrootstl.cab"
DISALLOWED_CAB_URL = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/disallowedcertstl.cab"

# CryptoAPI constants
X509_ASN_ENCODING            = 0x00000001
PKCS_7_ASN_ENCODING          = 0x00010000
CERT_STORE_PROV_FILENAME_W   = 8
CERT_STORE_OPEN_EXISTING_FLAG = 0x00004000
CERT_STORE_READONLY_FLAG     = 0x00008000
CERT_STORE_ADD_REPLACE_EXISTING = 3


def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def download_file(url, dest):
    log("Downloading: %s" % url)
    urlretrieve(url, dest)
    if not os.path.exists(dest) or os.path.getsize(dest) == 0:
        raise Exception("Download failed or empty: %s" % url)
    log("Downloaded %d bytes" % os.path.getsize(dest))


def extract_cab(cab_path, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    log("Extracting: %s" % cab_path)
    ret = subprocess.call(["expand.exe", "-F:*", cab_path, dest_dir])
    if ret != 0:
        raise Exception("expand.exe failed (code %d)" % ret)
    stl_files = [f for f in os.listdir(dest_dir) if f.lower().endswith(".stl")]
    if not stl_files:
        raise Exception("No .stl file found after extracting %s" % cab_path)
    return os.path.join(dest_dir, stl_files[0])


def add_ctl_to_store(stl_path, store_name):
    crypt32 = ctypes.windll.crypt32

    if isinstance(stl_path, bytes):
        stl_path = stl_path.decode("mbcs")

    hSrcStore = crypt32.CertOpenStore(
        CERT_STORE_PROV_FILENAME_W,
        X509_ASN_ENCODING | PKCS_7_ASN_ENCODING,
        None,
        CERT_STORE_OPEN_EXISTING_FLAG | CERT_STORE_READONLY_FLAG,
        stl_path
    )
    if not hSrcStore:
        raise Exception("CertOpenStore failed for %s: %d" % (stl_path, ctypes.GetLastError()))

    hDstStore = crypt32.CertOpenSystemStoreW(None, store_name)
    if not hDstStore:
        crypt32.CertCloseStore(hSrcStore, 0)
        raise Exception("CertOpenSystemStoreW(%s) failed: %d" % (store_name, ctypes.GetLastError()))

    added = 0
    try:
        pCtl = crypt32.CertEnumCTLsInStore(hSrcStore, None)
        while pCtl:
            result = crypt32.CertAddCTLContextToStore(
                hDstStore,
                pCtl,
                CERT_STORE_ADD_REPLACE_EXISTING,
                None
            )
            if result:
                added += 1
            else:
                log("CertAddCTLContextToStore failed: %d" % ctypes.GetLastError())
            pCtl = crypt32.CertEnumCTLsInStore(hSrcStore, pCtl)
    finally:
        crypt32.CertCloseStore(hDstStore, 0)
        crypt32.CertCloseStore(hSrcStore, 0)

    log("Added %d CTL(s) to %s" % (added, store_name))
    return added


def main():
    log("=== START ===")

    WORK_DIR = tempfile.gettempdir()

    # -- Trusted roots
    authroot_cab = os.path.join(WORK_DIR, "authrootstl.cab")
    authroot_dir = os.path.join(WORK_DIR, "authroot")
    download_file(AUTHROOT_CAB_URL, authroot_cab)
    authroot_stl = extract_cab(authroot_cab, authroot_dir)
    add_ctl_to_store(authroot_stl, u"AuthRoot")

    # -- Disallowed certs
    disallowed_cab = os.path.join(WORK_DIR, "disallowedcertstl.cab")
    disallowed_dir = os.path.join(WORK_DIR, "disallowed")
    download_file(DISALLOWED_CAB_URL, disallowed_cab)
    disallowed_stl = extract_cab(disallowed_cab, disallowed_dir)
    add_ctl_to_store(disallowed_stl, u"Disallowed")


if __name__ == "__main__":
    try:
        log("Launching...")
        main()
        log("DONE")
    except Exception as e:
        log("FATAL: %s" % str(e))
        log(traceback.format_exc())
        print("ERROR: %s" % str(e))
        raw_input("Press Enter to exit...")
