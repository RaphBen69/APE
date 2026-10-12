"""Mirror dist/ to the OVH hosting over SFTP: delete stale remote files, upload new or changed ones.

Usage: python scripts/deploy.py [--dry-run]
Password: APE_SFTP_PASSWORD, else the "APE" site saved in FileZilla, else prompt.
"""
import argparse
import base64
import getpass
import hashlib
import json
import os
import posixpath
import stat
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import paramiko
except ImportError:
    sys.exit("paramiko is missing: pip install paramiko")

HOST = "ftp.cluster029.hosting.ovh.net"
PORT = 22
USER = "apested"
REMOTE_ROOT = "/home/apested/www/APE"
MANIFEST = ".deploy-manifest.json"
DIST = Path(__file__).resolve().parent.parent / "dist"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
    args = parser.parse_args()

    local = local_files()
    sftp, transport = connect()
    try:
        remote_files, remote_dirs = remote_tree(sftp)
        manifest = read_manifest(sftp)

        to_delete = sorted(p for p in remote_files if p not in local and not is_hidden(p))
        to_upload = sorted(p for p, h in local.items() if p not in remote_files or manifest.get(p) != h)
        dirs_to_delete = sorted(
            (d for d in remote_dirs if not any(p.startswith(d + "/") for p in local) and not is_hidden(d)),
            key=lambda d: -d.count("/"),
        )

        upload_size = sum((DIST / p).stat().st_size for p in to_upload)
        print(f"Local: {len(local)} files | remote: {len(remote_files)} files")
        print(f"Delete: {len(to_delete)} files, {len(dirs_to_delete)} folders")
        print(f"Upload: {len(to_upload)} files ({upload_size / 1e6:.1f} MB)")
        if args.dry_run:
            for p in to_delete:
                print("  - " + p)
            for p in to_upload:
                print("  + " + p)
            return

        # Delete first so the upload fits in the quota.
        for p in to_delete:
            sftp.remove(remote(p))
            print("  - " + p)
        for d in dirs_to_delete:
            sftp.rmdir(remote(d))
        made = set(remote_dirs) - set(dirs_to_delete)
        for p in to_upload:
            ensure_dir(sftp, posixpath.dirname(p), made)
            sftp.put(str(DIST / p), remote(p))
            print("  + " + p)
        write_manifest(sftp, local)
        print("Deploy done: https://apesteanne.fr/APE/")
    finally:
        sftp.close()
        transport.close()


def local_files():
    if not (DIST / "index.html").is_file():
        sys.exit(f"{DIST} has no index.html: run npm run build first")
    files = {}
    for path in DIST.rglob("*"):
        if path.is_file():
            files[path.relative_to(DIST).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def connect():
    transport = paramiko.Transport((HOST, PORT))
    transport.start_client()
    check_host_key(transport.get_remote_server_key())
    transport.auth_password(USER, password())
    return paramiko.SFTPClient.from_transport(transport), transport


def password():
    if os.environ.get("APE_SFTP_PASSWORD"):
        return os.environ["APE_SFTP_PASSWORD"]
    site_file = Path(os.environ.get("APPDATA", "")) / "FileZilla" / "sitemanager.xml"
    if site_file.is_file():
        for server in ET.parse(site_file).iter("Server"):
            pw = server.find("Pass")
            if server.findtext("Host") == HOST and server.findtext("User") == USER and pw is not None:
                return base64.b64decode(pw.text).decode() if pw.get("encoding") == "base64" else pw.text
    return getpass.getpass(f"SFTP password for {USER}@{HOST}: ")


def check_host_key(key):
    # Trust on first use, then refuse a changed key.
    known_path = Path.home() / ".ssh" / "known_hosts"
    known = paramiko.HostKeys()
    if known_path.is_file():
        known.load(str(known_path))
    entry = f"[{HOST}]:{PORT}" if PORT != 22 else HOST
    saved = known.lookup(entry)
    if saved and key.get_name() in saved:
        if saved[key.get_name()] != key:
            sys.exit(f"Host key for {HOST} changed: refusing to deploy")
        return
    print(f"New host key for {HOST}: {key.get_name()} {key.get_fingerprint().hex()}")
    known.add(entry, key.get_name(), key)
    known_path.parent.mkdir(exist_ok=True)
    known.save(str(known_path))


def remote_tree(sftp):
    files, dirs = set(), set()
    pending = [""]
    while pending:
        rel = pending.pop()
        for attr in sftp.listdir_attr(remote(rel)):
            child = posixpath.join(rel, attr.filename) if rel else attr.filename
            if stat.S_ISDIR(attr.st_mode):
                dirs.add(child)
                pending.append(child)
            else:
                files.add(child)
    files.discard(MANIFEST)
    return files, dirs


def read_manifest(sftp):
    try:
        with sftp.open(remote(MANIFEST)) as f:
            return json.loads(f.read())
    except (IOError, ValueError):
        return {}


def write_manifest(sftp, local):
    with sftp.open(remote(MANIFEST), "w") as f:
        f.write(json.dumps(local))


def ensure_dir(sftp, rel, made):
    if not rel or rel in made:
        return
    ensure_dir(sftp, posixpath.dirname(rel), made)
    sftp.mkdir(remote(rel))
    made.add(rel)


def is_hidden(rel):
    # Keep server config like .htaccess or .ovhconfig.
    return any(part.startswith(".") for part in rel.split("/"))


def remote(rel):
    return posixpath.join(REMOTE_ROOT, rel) if rel else REMOTE_ROOT


if __name__ == "__main__":
    main()
