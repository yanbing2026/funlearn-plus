#!/usr/bin/env python3
"""Deploy Supabase Edge Functions via Management API (multipart/form-data).

Usage:
    python3 deploy_functions.py [slug ...]
Deploys all functions under supabase/functions/ when no slug is given.
"""
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (  # noqa: E402
    add_surrogate_to_request,
    read_json_response,
    read_response_body,
)

REF = "sjqhcpbdgaeapljbllhp"
BASE = "https://api.supabase.com"
ALLOWED = ["api.supabase.com"]
HERE = os.path.dirname(os.path.abspath(__file__))
FUNCS_DIR = os.path.join(HERE, "functions")

# slug -> verify_jwt
VERIFY_JWT = {
    "create-checkout": True,
    "customer-portal": True,
    "stripe-webhook": False,
}

BOUNDARY = "----hatchfnboundary9f8e7d6c"


def build_multipart(slug: str, files):
    body = b""

    def part(headers: dict, data: bytes):
        nonlocal body
        body += ("--" + BOUNDARY + "\r\n").encode()
        for k, v in headers.items():
            body += f"{k}: {v}\r\n".encode()
        body += b"\r\n" + data + b"\r\n"

    metadata = json.dumps(
        {"entrypoint_path": "index.ts", "name": slug,
         "verify_jwt": VERIFY_JWT.get(slug, True)}
    )
    part(
        {"Content-Disposition": 'form-data; name="metadata"',
         "Content-Type": "application/json"},
        metadata.encode(),
    )
    for filename, path in files:
        with open(path, "rb") as fh:
            data = fh.read()
        ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        part(
            {"Content-Disposition": f'form-data; name="file"; filename="{filename}"',
             "Content-Type": ctype},
            data,
        )
    body += ("--" + BOUNDARY + "--\r\n").encode()
    return body


def collect_files(func_dir: str):
    out = []
    for root, _dirs, names in os.walk(func_dir):
        for n in names:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, func_dir).replace(os.sep, "/")
            out.append((rel, full))
    return out


def deploy(slug: str):
    func_dir = os.path.join(FUNCS_DIR, slug)
    if not os.path.isdir(func_dir):
        print(f"skip {slug}: no directory")
        return False
    files = collect_files(func_dir)
    body = build_multipart(slug, files)
    url = f"{BASE}/v1/projects/{REF}/functions/deploy?slug={slug}"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={BOUNDARY}")
    req.add_header("User-Agent", "muse-supabase-skill")
    add_surrogate_to_request(req, "custom.supabase", allowed_hosts=ALLOWED)
    try:
        with urllib.request.urlopen(req) as resp:
            payload = read_json_response(resp)
        print(f"[{slug}] deployed: id={payload.get('id')} status={payload.get('status')}")
        return True
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(read_response_body(exc).decode("utf-8"))
        except Exception:  # noqa: BLE001
            payload = {"message": f"HTTP {exc.code}"}
        print(f"[{slug}] FAILED: {json.dumps(payload)[:800]}")
        return False


def main():
    slugs = sys.argv[1:] or sorted(
        d for d in os.listdir(FUNCS_DIR)
        if os.path.isdir(os.path.join(FUNCS_DIR, d))
    )
    ok = True
    for slug in slugs:
        ok = deploy(slug) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
