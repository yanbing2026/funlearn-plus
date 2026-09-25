#!/usr/bin/env python3
"""上传示例 PDF 到 member-files bucket，并在 content_items 中 seed 6 篇内容。
service_role key 仅在内存中使用，不打印、不落盘。
"""
import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
sys.path.insert(0, "/home/hatch/workspace/skills/supabase/bin")
from dynamic_credentials import add_surrogate_to_request, read_response_body

REF = "sjqhcpbdgaeapljbllhp"
MGMT = "https://api.supabase.com"
PROJECT = f"https://{REF}.supabase.co"


def mgmt(method, path, data=None):
    req = urllib.request.Request(MGMT + path, method=method)
    add_surrogate_to_request(req, "custom.supabase", allowed_hosts=["api.supabase.com"])
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
        req.data = body
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


ITEMS = [
    {
        "slug": "daily-10-min-reading", "tier": "free", "kind": "article",
        "cover_emoji": "📖", "sort_order": 1,
        "title": "每天10分钟，陪娃爱上认字",
        "excerpt": "不用报班、不买一堆卡片，抓住三个生活场景，认字变成亲子游戏。",
        "body": """## 为什么是 10 分钟？

学龄前孩子的专注力一次只有 10–15 分钟。与其周末突击一小时，不如每天睡前 10 分钟，效果反而更好——**高频短时**是这个年龄段记忆的黄金法则。

## 三个随时可用的方法

### 1. 指读：把绘本变成认字课
读绘本时用手指着字读，读到关键词时停顿，让孩子说出那个字。不用全篇指读，每天挑 3–5 个词就够了。

### 2. 生活认字：把世界当识字卡
- 电梯里的数字、楼层
- 超市里的水果标签
- 红绿灯、路牌、店招

看到就读出来，孩子会觉得认字是"有用的本事"，而不是作业。

### 3. 游戏化：猜字、找字、贴字
把生字写在便签纸上贴在家里，玩"寻宝游戏"：说出一个字，全家一起找。找对了就撕下来，集满 10 张换一个小奖励。

## 三个坑别踩

- **别考孩子**："这个字念什么？"天天考，孩子很快就烦。改成"你来当小老师教我"。
- **别贪多**：一天 3–5 个新字足够，复习旧字更重要。
- **别比较**："隔壁小孩都认识 500 个了"——这句话对认字速度没有任何帮助。

> 记住：目标不是认多少字，而是让孩子觉得**字是好玩的**。兴趣在了，速度自然来。""",
    },
    {
        "slug": "blockquest-family-guide", "tier": "free", "kind": "article",
        "cover_emoji": "🎮", "sort_order": 2,
        "title": "BlockQuest 家庭玩法：把游戏时间变成学习时间",
        "excerpt": "孩子爱玩方块游戏？三招把它变成认字、数数和专注力训练。",
        "body": """## 先说结论

堵不如疏。孩子天生爱玩方块、搭建、探索类的游戏，关键是**家长怎么参与**。下面三招，今晚就能用。

## 第一招：任务卡玩法

别让孩子漫无目的地挖矿。提前写 3 张任务卡：

- ⛏️ 收集 10 个木块（数数）
- 🏠 盖一座有 2 扇窗户的房子（形状+计数）
- 🌻 种 5 朵花并给它们起名字（认字+表达）

完成一张就打勾。游戏还是那个游戏，但多了目标感和成就感。

## 第二招：家长当"记者"

在旁边别只说"别玩了"。试试当记者采访：

- "你盖的这是什么？能带我参观一下吗？"（表达）
- "这个桥有多长？你数数用了几块？"（数学）
- "如果下雨了，你的房子怎么办？"（解决问题）

孩子讲得越起劲，语言和思维锻炼得越多。

## 第三招：定好规则再开始

- **计时器**：用番茄钟，25 分钟一局，时间到就存档退出
- **先任务后自由**：完成任务卡才能自由建造
- **全家复盘**：结束时每人说一个今天最满意的作品

> 游戏时间不是学习的敌人，**无陪伴的游戏时间才是**。你参与的 25 分钟，胜过孩子独自玩的 2 小时。""",
    },
    {
        "slug": "math-roadmap-3-6", "tier": "member", "kind": "article",
        "cover_emoji": "🔢", "sort_order": 3,
        "title": "3–6岁数学思维路线图：从数数到加减法",
        "excerpt": "每个阶段练什么、怎么练、练到什么程度算达标，一张图讲清楚。",
        "body": """## 总览：四个阶段

- **3岁**：点数 1–10，一一对应
- **4岁**：10 以内唱数、倒数，理解"几个"
- **5岁**：10 以内加减，凑十法启蒙
- **6岁**：20 以内加减，简单应用题

超前不是目标，**扎实**才是。每个阶段的地基没打牢，后面都要返工。

## 3岁：点数与一一对应

核心能力：手口一致点数，知道"数到几就是几个"。

**玩法**：上楼梯数台阶、吃饭数勺子、散步数小狗。关键是**用手指一个一个点着数**，不要只动嘴。

**达标**：能点数 10 个以内的任意物品，说出总数。

## 4岁：数的顺序与大小

核心能力：正数倒数都流利，知道 7 比 5 大。

**玩法**：
- 玩扑克牌比大小（只用 1–10）
- 骰子游戏：掷到几走几步
- "我藏了几个"：手里藏几颗糖，让孩子猜，再验证

**达标**：能从任意数正数到 10、倒数到 1；能比较两组物品多少。

## 5岁：10 以内加减

核心能力：理解加是"合起来"、减是"拿走"。

**玩法**：
- 分糖果："你有 3 颗，我再给你 2 颗，现在几颗？"
- 玩具买卖：用积木当钱，买东西找零（只用 10 以内）
- 打印我们的《10以内加法练习卡》，每天 5 道题

**达标**：10 以内加减口算基本脱口而出，理解凑十（8+5 = 8+2+3）。

## 6岁：20 以内与应用题

核心能力：20 以内加减，生活中的简单应用题。

**玩法**：购物实战——给孩子 20 元预算买水果，让他自己算。真实场景的学习效果是练习册的 10 倍。

## 家长自查清单

- [ ] 孩子数数是"点着数"还是"背儿歌"？
- [ ] 孩子知道"5"代表 5 个东西吗？
- [ ] 加减法是靠掰手指还是已经内化？
- [ ] 孩子觉得数学好玩吗？

> 如果第四个答案是否定的，先停下来，回到游戏。**兴趣是 1，其他都是后面的 0。**""",
    },
    {
        "slug": "addition-worksheet", "tier": "member", "kind": "download",
        "cover_emoji": "➕", "sort_order": 4, "file_path": "worksheets/addition-to-10.pdf",
        "title": "10以内加法练习卡",
        "excerpt": "40 道 10 以内加法，A4 打印即用，适合 5–6 岁。",
        "body": """## 这份教具怎么用

- **打印**：A4 纸直接打印，建议用 120g 以上纸张，孩子写字不洇墨
- **节奏**：每天 1 页（20 道），5 分钟完成，不要一次刷完
- **批改**：当场批改，错题用红笔圈出来，第二天先重做错题

## 配套玩法：口算接龙

打印后剪成小卡片，全家玩接龙：大人出一张，孩子答对了就下一张，答错了放回牌堆。集满 10 张全对，兑换一个小心愿。

> 熟练标准：20 道题 5 分钟内全对，就可以进入 20 以内加减了。""",
    },
    {
        "slug": "counting-coloring", "tier": "member", "kind": "download",
        "cover_emoji": "🎨", "sort_order": 5, "file_path": "worksheets/counting-coloring.pdf",
        "title": "数数涂色卡",
        "excerpt": "数一数、写一写、涂一涂，3–4 岁点数启蒙必备。",
        "body": """## 这份教具怎么用

- **第一步数**：让孩子用手指一个一个点着数图形
- **第二步写**：在方框里写下数字（写不好没关系，描一遍也行）
- **第三步涂**：按自己的喜好涂色，涂完贴在冰箱上展示

## 家长注意

这个阶段**不要纠正握笔姿势以外的任何事**。数错了就笑着再数一遍，重点是"数"这个动作本身，不是答案。

> 完成后可以问："你涂的是什么颜色？为什么选这个颜色？"——把数学时间自然过渡到表达练习。""",
    },
    {
        "slug": "weekly-plan", "tier": "member", "kind": "article",
        "cover_emoji": "🗓️", "sort_order": 6,
        "title": "一周陪伴计划：职场爸妈的高效陪娃方案",
        "excerpt": "工作日每天 15 分钟，周末 1 小时，一周陪伴这样安排最省心。",
        "body": """## 核心理念

陪伴质量 = **专注度 × 规律性**，和时长关系不大。每天雷打不动的 15 分钟，胜过周末心血来潮的三小时。

## 工作日（每天 15 分钟）

- **周一 · 认字日**：睡前指读绘本，认 3 个新词
- **周二 · 数学日**：扑克牌比大小 / 骰子游戏
- **周三 · 表达日**："今天最开心的三件事"分享
- **周四 · 动手日**：剪纸、折纸、搭积木（二选一）
- **周五 · 电影夜**：一起看 20 分钟动画片，讨论剧情

固定在**睡前**进行，形成仪式感，孩子会主动期待。

## 周末（每天 1 小时）

- **周六上午**：户外探索（公园找落叶、数台阶、认路牌）
- **周日下午**：厨房小帮手（洗菜、摆碗筷、数人数拿筷子）

户外和家务都是天然的学习场景，不用额外准备教具。

## 执行小技巧

1. **打印出来贴冰箱**：看得见的计划才会被执行
2. **全家统一**：爸爸妈妈、爷爷奶奶用同一套，避免孩子钻空子
3. **打卡不苛责**：出差、加班断了就断了，第二天接着来，不用"补"
4. **每月复盘**：月底问孩子"这个月最喜欢哪一天的活动"，下个月多安排

> 最好的早教，是**可坚持的**早教。这份计划先执行两周，再根据孩子的反应微调。""",
    },
]


def esc(s):
    return s.replace("%", "%%").replace("'", "''")


def main():
    sr = service_role_key()
    print("uploading pdfs...")
    for local, remote in [
        ("/tmp/worksheets/addition-to-10.pdf", "worksheets/addition-to-10.pdf"),
        ("/tmp/worksheets/counting-coloring.pdf", "worksheets/counting-coloring.pdf"),
    ]:
        r = upload_pdf(sr, local, remote)
        print(" uploaded", remote, "->", r.get("Key") or r.get("key") or "ok")

    print("seeding content_items...")
    vals = []
    for it in ITEMS:
        vals.append(
            "('%s','%s','%s','%s','%s','%s',%s,'%s',%d,true)"
            % (
                esc(it["slug"]), esc(it["title"]), esc(it["excerpt"]),
                esc(it["body"]), it["tier"], it["kind"],
                ("'" + esc(it["file_path"]) + "'" if it.get("file_path") else "NULL"),
                esc(it["cover_emoji"]), it["sort_order"],
            )
        )
    sql = (
        "insert into public.content_items "
        "(slug,title,excerpt,body_markdown,tier,kind,file_path,cover_emoji,sort_order,published) values "
        + ",".join(vals)
        + " on conflict (slug) do update set title=excluded.title, excerpt=excluded.excerpt,"
        + " body_markdown=excluded.body_markdown, tier=excluded.tier, kind=excluded.kind,"
        + " file_path=excluded.file_path, cover_emoji=excluded.cover_emoji,"
        + " sort_order=excluded.sort_order, published=true;"
        + " select slug,tier,kind from public.content_items order by sort_order;"
    )
    rows = db_query(sql)
    for r in rows:
        print(" ", r["slug"], r["tier"], r["kind"])


if __name__ == "__main__":
    main()
