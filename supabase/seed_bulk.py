#!/usr/bin/env python3
"""批量生成 35 个 PDF -> 上传 member-files -> upsert 全部文章/下载 (free 20, member 106)。
service_role key 仅内存使用，不打印不落盘。"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/funlearn-plus/supabase")
sys.path.insert(0, "/home/hatch/workspace/funlearn-plus/supabase/bulk")
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
sys.path.insert(0, "/home/hatch/workspace/skills/supabase/bin")
from dynamic_credentials import add_surrogate_to_request, read_response_body
from render import article_md, download_md
from free import FREE
from member1 import MEMBER_1
from member2 import MEMBER_2
from member3 import MEMBER_3
from downloads import DOWNLOADS
import bulk_pdfs

REF = "sjqhcpbdgaeapljbllhp"
MGMT = "https://api.supabase.com"
PROJECT = f"https://{REF}.supabase.co"
OUTDIR = "/tmp/worksheets2"


def mgmt(method, path, data=None):
    req = urllib.request.Request(MGMT + path, method=method)
    add_surrogate_to_request(req, "custom.supabase", allowed_hosts=["api.supabase.com"])
    if data is not None:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as r:
        return json.loads(read_response_body(r).decode())


def service_role_key():
    keys = mgmt("GET", f"/v1/projects/{REF}/api-keys")
    return next(k["api_key"] for k in keys if k.get("name") == "service_role")


def db_query(sql):
    return mgmt("POST", f"/v1/projects/{REF}/database/query", {"query": sql})


def upload_pdf(sr_key, local, remote):
    url = f"{PROJECT}/storage/v1/object/member-files/{remote}"
    with open(local, "rb") as fh:
        data = fh.read()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("apikey", sr_key)
    req.add_header("Authorization", f"Bearer {sr_key}")
    req.add_header("Content-Type", "application/pdf")
    req.add_header("x-upsert", "true")
    with urllib.request.urlopen(req) as r:
        return json.loads(read_response_body(r).decode())


def esc(s):
    return s.replace("%", "%%").replace("'", "''")


def main():
    print("building pdfs...")
    bulk_pdfs.build_all(OUTDIR)

    sr = service_role_key()
    print("uploading pdfs...")
    for d in DOWNLOADS:
        local = os.path.join(OUTDIR, os.path.basename(d["file"]))
        upload_pdf(sr, local, d["file"])
    print(" uploaded", len(DOWNLOADS), "pdfs")

    items = []
    for a in FREE:
        items.append((a["slug"], a["title"], a["excerpt"], article_md(a), "free", "article", None, a["emoji"], a["sort"]))
    for a in MEMBER_1 + MEMBER_2 + MEMBER_3:
        items.append((a["slug"], a["title"], a["excerpt"], article_md(a), "member", "article", None, a["emoji"], a["sort"]))
    for d in DOWNLOADS:
        items.append((d["slug"], d["title"], d["excerpt"], download_md(d), "member", "download", d["file"], d["emoji"], d["sort"]))

    vals = []
    for slug, title, excerpt, body, tier, kind, fpath, emoji, sort in items:
        vals.append(
            "('%s','%s','%s','%s','%s','%s',%s,'%s',%d,true)"
            % (esc(slug), esc(title), esc(excerpt), esc(body), tier, kind,
               ("'" + esc(fpath) + "'" if fpath else "NULL"), esc(emoji), sort)
        )
    sql = (
        "insert into public.content_items "
        "(slug,title,excerpt,body_markdown,tier,kind,file_path,cover_emoji,sort_order,published) values "
        + ",".join(vals)
        + " on conflict (slug) do update set title=excluded.title, excerpt=excluded.excerpt,"
        + " body_markdown=excluded.body_markdown, tier=excluded.tier, kind=excluded.kind,"
        + " file_path=excluded.file_path, cover_emoji=excluded.cover_emoji,"
        + " sort_order=excluded.sort_order, published=true;"
    )
    db_query(sql)
    counts = db_query(
        "select tier, count(*) c from public.content_items where published=true group by tier;"
    )
    dl = db_query(
        "select count(*) c from public.content_items where kind='download' and published=true;"
    )
    print("counts:", counts, "downloads:", dl)


if __name__ == "__main__":
    main()
