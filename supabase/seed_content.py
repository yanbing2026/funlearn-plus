#!/usr/bin/env python3
"""上传示例 PDF 到 member-files bucket，并在 content_items 中 seed 6 篇英文内容。
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
        "title": "The 10-Minute Rule: Helping Your Preschooler Fall in Love with Letters",
        "excerpt": "No classes, no stacks of flashcards — three everyday moments that turn letter learning into a game.",
        "body": """## Why 10 minutes?

A preschooler's focused attention lasts 10–15 minutes at a time. A calm 10 minutes every evening beats a forced one-hour weekend session — **short and frequent** is the golden rule for memory at this age.

## Three methods you can use tonight

### 1. Point-and-read: turn picture books into letter lessons
Point at the words as you read. Pause on key words and let your child say them. No need to point at everything — 3–5 words a day is plenty.

### 2. Real-world letters: the world is your flashcard
- Elevator numbers and floor signs
- Fruit labels at the grocery store
- Traffic lights, street signs, store names

Read them aloud when you see them. Kids learn fastest when letters feel **useful**, not like homework.

### 3. Make it a game: guess, find, stick
Write new words on sticky notes around the house and play treasure hunt: call out a word, everyone races to find it. Find all 10 and earn a small reward.

## Three traps to avoid

- **Don't quiz**: "What does this say?" every day kills the fun fast. Try "Can you be my teacher and teach me?" instead.
- **Don't overload**: 3–5 new words a day is enough. Reviewing old ones matters more.
- **Don't compare**: "The neighbor's kid knows 500 words already" has never sped up anyone's learning.

> Remember: the goal isn't word count — it's making your child feel that **letters are fun**. Interest first, speed follows.""",
    },
    {
        "slug": "blockquest-family-guide", "tier": "free", "kind": "article",
        "cover_emoji": "🎮", "sort_order": 2,
        "title": "BlockQuest Family Guide: Turn Game Time into Learning Time",
        "excerpt": "Your kid loves block games? Three moves that turn them into letter, counting, and focus practice.",
        "body": """## The short version

Blocking the game doesn't work — channeling it does. Kids are wired to love building and exploring. What matters is **how you join in**. Three moves, usable tonight.

## Move 1: Mission cards

Don't let them mine aimlessly. Write 3 mission cards in advance:

- ⛏️ Collect 10 wood blocks (counting)
- 🏠 Build a house with 2 windows (shapes + counting)
- 🌻 Plant 5 flowers and name each one (letters + expression)

Check one off when done. Same game — but now with goals and a sense of achievement.

## Move 2: Be the "reporter"

Instead of "stop playing," try interviewing:

- "What did you build? Can you give me a tour?" (expression)
- "How long is this bridge? Count the blocks you used." (math)
- "What happens to your house if it rains?" (problem solving)

The more they explain, the more language and thinking get exercised.

## Move 3: Set the rules before you start

- **Timer**: 25 minutes a round with a kitchen timer — save and stop when it rings
- **Missions first**: free building unlocks after mission cards are done
- **Family recap**: everyone shares their favorite build at the end

> Game time isn't the enemy of learning — **unsupervised** game time is. Your 25 engaged minutes beat two hours of solo play.""",
    },
    {
        "slug": "math-roadmap-3-6", "tier": "member", "kind": "article",
        "cover_emoji": "🔢", "sort_order": 3,
        "title": "Math Roadmap for Ages 3–6: From Counting to Addition",
        "excerpt": "What to practice at each stage, how to practice it, and what 'done' looks like — all on one page.",
        "body": """## Overview: four stages

- **Age 3**: count 1–10 with one-to-one correspondence
- **Age 4**: count forward and backward to 10, grasp "how many"
- **Age 5**: add and subtract within 10, intro to making-ten
- **Age 6**: add and subtract within 20, simple word problems

Getting ahead isn't the goal — **solid foundations** are. A shaky stage now means rework later.

## Age 3: counting with one-to-one correspondence

Core skill: touch each object once while counting, and know the last number is the total.

**Play**: count stairs, spoons at dinner, dogs on a walk. The key: **point with a finger**, don't just chant.

**Done when**: can count any set of up to 10 objects and say the total.

## Age 4: number order and size

Core skill: fluent forward and backward counting, knowing 7 is bigger than 5.

**Play**:
- Card game "War" with 1–10 only
- Dice games: roll and move that many steps
- "How many am I hiding?": hide candies in your hand, guess, then check

**Done when**: can count up to 10 and back down from any starting number; can compare two groups.

## Age 5: addition and subtraction within 10

Core skill: addition means "put together," subtraction means "take away."

**Play**:
- Sharing snacks: "You have 3, I give you 2 more — how many now?"
- Toy store: use blocks as money, practice paying and change (within 10)
- Print our *Addition Practice* pack — 5 problems a day

**Done when**: near-instant recall of sums within 10; understands making ten (8+5 = 8+2+3).

## Age 6: within 20 and word problems

Core skill: add/subtract within 20, solve simple real-life word problems.

**Play**: real grocery runs — give your child a $20 budget for fruit and let them do the math. Real contexts teach 10× better than worksheets.

## Parent self-check

- [ ] Does my child count by pointing, or just chant?
- [ ] Does my child know "5" means five things?
- [ ] Is addition finger-counting or internalized?
- [ ] Does my child think math is fun?

> If the last answer is no, pause and go back to games. **Interest is the 1; everything else is a 0 after it.**""",
    },
    {
        "slug": "addition-worksheet", "tier": "member", "kind": "download",
        "cover_emoji": "➕", "sort_order": 4, "file_path": "worksheets/addition-to-10.pdf",
        "title": "Addition Practice: Numbers to 10",
        "excerpt": "40 addition problems within 10. Print on A4 and go — ideal for ages 5–6.",
        "body": """## How to use this pack

- **Print**: A4, any home printer. Heavier paper (32 lb+) feels better for little hands.
- **Pace**: one page (20 problems) a day, about 5 minutes. Don't binge it.
- **Review**: check answers together right away. Circle mistakes in red and redo them first the next day.

## Bonus game: flashcard relay

Cut the page into cards and play as a family: you show a card, your child answers. Correct → next card; wrong → back in the pile. Ten in a row earns a small wish.

> Mastery bar: 20 problems, all correct, in under 5 minutes — then you're ready for addition within 20.""",
    },
    {
        "slug": "counting-coloring", "tier": "member", "kind": "download",
        "cover_emoji": "🎨", "sort_order": 5, "file_path": "worksheets/counting-coloring.pdf",
        "title": "Count & Color Worksheets",
        "excerpt": "Count, write, and color — the essential one-to-one correspondence starter for ages 3–4.",
        "body": """## How to use this pack

- **Step 1 — count**: have your child point at each shape and count, one by one
- **Step 2 — write**: write the number in the box (tracing is fine if writing is hard)
- **Step 3 — color**: color however they like, then put it on the fridge

## A note for parents

At this stage, **don't correct anything except pencil grip**. Counted wrong? Smile and count again together. The *act* of counting matters more than the answer.

> When done, ask: "What color did you choose? Why that one?" — a natural bridge from math time into expression practice.""",
    },
    {
        "slug": "weekly-plan", "tier": "member", "kind": "article",
        "cover_emoji": "🗓️", "sort_order": 6,
        "title": "The Working Parent's Weekly Plan: 15 Minutes a Day",
        "excerpt": "15 minutes on weekdays, one hour on weekends — a no-stress rhythm that actually sticks.",
        "body": """## The core idea

Quality of time together = **focus × consistency**. Fifteen unmissable minutes a day beats an ambitious three-hour weekend session.

## Weekdays (15 minutes each)

- **Mon · Letters**: point-and-read at bedtime, 3 new words
- **Tue · Math**: card game War / dice games
- **Wed · Expression**: share "three favorite moments of the day"
- **Thu · Hands-on**: paper cutting, origami, or building blocks (pick one)
- **Fri · Movie night**: watch 20 minutes together, talk about the story

Anchor it to **bedtime** — rituals create anticipation, and kids will start asking for it.

## Weekends (one hour each)

- **Saturday morning**: outdoor exploring (find leaves, count steps, read signs)
- **Sunday afternoon**: kitchen helper (wash veggies, set the table, count chopsticks)

The outdoors and the kitchen are natural classrooms — no prep needed.

## Tips that make it stick

1. **Print it and stick it on the fridge**: a visible plan gets followed
2. **One plan for the whole family**: parents and grandparents on the same page
3. **Don't "make up" missed days**: travel or overtime happens — just pick up tomorrow
4. **Monthly retro**: ask your child which day they liked best, and do more of that

> The best early education is the **sustainable** kind. Run this plan for two weeks, then tune it to your child's reactions.""",
    },
    {
        "slug": "car-counting-games", "tier": "free", "kind": "article",
        "cover_emoji": "🚗", "sort_order": 7,
        "title": "3 No-Prep Counting Games for the Car",
        "excerpt": "Stuck in traffic? Turn the ride into math practice — no materials needed.",
        "body": """## Why the car works

Kids are strapped in, bored, and looking at the world — the perfect setup for noticing numbers. These games need zero prep and work for ages 3–6.

## Game 1: Color count

Pick a color. Everyone counts how many cars of that color pass in 2 minutes. Whoever's closest to the real count wins. Practices counting, comparing, and estimating.

## Game 2: License plate math

Read the numbers on a license plate and add them up. For younger kids, just read the digits out loud. For ages 5–6, race to add them first.

## Game 3: I spy numbers

"I spy the number 7!" — first to spot a 7 on a sign, plate, or building wins a point. First to 5 points picks the next song.

## The rule that makes it last

Rotate the games so they stay fresh, and let your child **be the game master** sometimes. Kids who run the game practice twice as hard without noticing.""",
    },
    {
        "slug": "reading-roadmap-3-6", "tier": "member", "kind": "article",
        "cover_emoji": "🔤", "sort_order": 8,
        "title": "Reading Roadmap for Ages 3–6: From ABCs to First Books",
        "excerpt": "The four stages of early reading, what to do at each one, and how to know when to move on.",
        "body": """## Stage 1: Letter awareness (age 3)

**Goal**: recognize uppercase letters and know they carry meaning.
**Play**: alphabet puzzles, letter magnets on the fridge, "find the first letter of your name" everywhere.
**Move on when**: names most letters on sight, no particular order needed.

## Stage 2: Letter sounds (age 4)

**Goal**: connect letters to sounds — "B says buh."
**Play**: "I spy something that starts with mmm." Sing the alphabet slowly and pause — let your child fill in the missing letter.
**Move on when**: knows most letter sounds and can tell you the first sound of simple words.

## Stage 3: Blending (age 5)

**Goal**: push sounds together — "c-a-t … cat!"
**Play**: start with word families: cat, hat, mat, sat. Same ending, one letter changes. Our *Sight Words Flashcards* pack makes daily practice painless.
**Move on when**: can sound out simple 3-letter words without help.

## Stage 4: First books (age 6)

**Goal**: read simple sentences with growing confidence.
**Play**: predictable books with repeating patterns ("Brown Bear, Brown Bear"). Take turns reading pages. Never correct mid-sentence — wait for the page to end.
**Done when**: reads a full early-reader book and can tell you what happened.

## The golden rules

1. **Read aloud daily** — 15 minutes of you reading to them does more than any app.
2. **Let them choose** — a "too easy" book they love beats a "just right" book they hate.
3. **Never test during story time** — asking "what does that word say?" every page turns joy into a quiz.

> Reading grows like a plant: you can't pull it taller. You can only water it every day.""",
    },
    {
        "slug": "sight-words-starter", "tier": "member", "kind": "article",
        "cover_emoji": "👁️", "sort_order": 9,
        "title": "Sight Words Starter: The First 25 Words",
        "excerpt": "Why some words must be memorized, the 25 to start with, and a 5-minute daily routine.",
        "body": """## What are sight words?

Words like *the*, *said*, *was* that can't be sounded out easily — kids just have to recognize them instantly. They make up about 75% of early-reader text, so memorizing them unlocks real reading fast.

## The first 25

the · and · a · to · said · in · he · I · of · it · was · you · they · on · she · is · for · at · his · but · that · with · all · we · can

(Print our *Sight Words Flashcards* pack to practice these.)

## The 5-minute daily routine

1. **Show** 5 cards, read each together (1 min)
2. **Shuffle**, hold each up for 2 seconds — correct = keep, wrong = back in the pile (2 min)
3. **Use one in a sentence** — "Can you say *they* in a sentence?" (2 min)

Add 5 new words each week. Review all old ones every day — the pile only grows when the old ones are instant.

## Three mistakes to avoid

- **Don't drill 25 at once**: 5 new a week is the speed limit.
- **Don't skip review**: a word isn't learned until it's instant for 3 days straight.
- **Don't sound them out**: that's the whole point — these are the exceptions. Just memorize.

> When your child reads *the* without thinking, they've taken the biggest step in early reading.""",
    },
    {
        "slug": "focus-habits", "tier": "member", "kind": "article",
        "cover_emoji": "🧘", "sort_order": 10,
        "title": "Focus & Habits: A Daily Rhythm That Sticks",
        "excerpt": "Kids don't lack focus — they lack rhythm. Build the day around four anchors.",
        "body": """## The insight

Adults focus with willpower. Kids focus with **rhythm** — predictable sequences their brain can relax into. Four anchors, same order, every day.

## Anchor 1: Morning launch (5 min)

Same three steps after breakfast: get dressed → make the bed → check the day's picture schedule. A visual schedule on the fridge beats verbal reminders every time.

## Anchor 2: Learning block (15–20 min)

One focused activity, timer on, phone away (yours too — they copy you). End with a tiny ritual: sticker on the chart, high five, done. The ritual is what makes it repeatable.

## Anchor 3: Outdoor reset (30+ min)

Physical play isn't a break from learning — it's when the brain files what it learned. No structure needed. Just outside.

## Anchor 4: Evening wind-down (15 min)

Bath → book → bed, same order. Screens off 30 minutes before. This anchor protects sleep, and sleep protects everything else.

## When it falls apart (it will)

Travel, illness, grandparents visiting — rhythm breaks. The rule: **never restart from zero**. Pick up the next anchor, not the whole day. A rhythm you can rejoin is a rhythm that survives.""",
    },
    {
        "slug": "screen-time-rules", "tier": "member", "kind": "article",
        "cover_emoji": "📱", "sort_order": 11,
        "title": "Screen Time Rules That Actually Work",
        "excerpt": "It's not about minutes — it's about which screens, with whom, and what comes after.",
        "body": """## Stop counting minutes

Research keeps finding the same thing: **what** they watch and **how** matter more than how long. An hour of building in Minecraft with dad beats 20 minutes of auto-playing toy unboxings alone.

## The 3 rules that work

### 1. Together beats alone

Co-view whenever possible. Ask questions: "Why do you think she did that?" A show watched together is a conversation. A show watched alone is a babysitter.

### 2. Active beats passive

Building, drawing, coding games > watching videos. If they're creating something, it's barely "screen time" at all.

### 3. Endings beat timers

"When this episode ends" works better than "10 more minutes" — kids understand stories ending. Use natural breakpoints: episode end, level complete, timer for open-ended games.

## The setup that enforces itself

- **One charging station** outside bedrooms — devices sleep there, so do kids
- **No screens during meals** — non-negotiable, applies to parents
- **The 30-minute rule** — screens off 30 minutes before bed, every night

## What to do instead (the real battle)

Rules fail when there's nothing better to do. Keep a "boredom box": puzzles, coloring pages (print ours!), blocks, cards. "I'm bored" should lead to the box, not the tablet.""",
    },
    {
        "slug": "number-tracing", "tier": "member", "kind": "download",
        "cover_emoji": "✏️", "sort_order": 12, "file_path": "worksheets/number-tracing.pdf",
        "title": "Number Tracing: 1–10",
        "excerpt": "Trace big numbers, practice writing, then count and color the dots. Ages 3–5.",
        "body": """## How to use this pack

- **Step 1 — trace**: finger-trace the big gray number first, then trace with a crayon
- **Step 2 — write**: practice in the boxes below (4 tries per number)
- **Step 3 — count**: count the dots and color them in — connects the symbol to the quantity

## Pencil grip check

Thumb and index finger hold, middle finger supports — the "tripod grip." If your child fist-grips, try shorter crayons: they're impossible to fist-hold.

> One number a day is plenty. Finish all 10, then start again — speed and confidence grow with repetition.""",
    },
    {
        "slug": "shapes-colors", "tier": "member", "kind": "download",
        "cover_emoji": "🟢", "sort_order": 13, "file_path": "worksheets/shapes-colors.pdf",
        "title": "Shapes & Colors Coloring Pack",
        "excerpt": "Six shapes to color and name, plus a color-by-instruction challenge. Ages 3–5.",
        "body": """## Page 1: Color and name

Color each shape, then say its name out loud: circle, square, triangle, rectangle, diamond, oval.

**Bonus**: find each shape somewhere in your house. (Hint: the TV is a rectangle.)

## Page 2: Color by instruction

Read each line and color the matching shape the right color. This practices **listening + following multi-step instructions** — a key school-readiness skill.

> When finished, ask: "Which shape was hardest to color inside?" — staying inside the lines is fine-motor practice in disguise.""",
    },
    {
        "slug": "sight-words-cards", "tier": "member", "kind": "download",
        "cover_emoji": "🃏", "sort_order": 14, "file_path": "worksheets/sight-words-cards.pdf",
        "title": "Sight Words Flashcards: First 25",
        "excerpt": "Cut-out flashcards for the 25 most common sight words, plus 3 game ideas. Ages 4–6.",
        "body": """## How to use

1. Print and cut along the dashed lines (cardstock recommended)
2. Start with 5 words — add 5 more each week
3. Three games included on the last page: Fast Flash, Word Hunt, Sentence Builder

## The routine

Hold up a card for 2 seconds. Instant read = keep it. Hesitation = back in the pile. A word counts as learned when it's instant 3 days in a row.

> Pair with our *Sight Words Starter* guide for the full method.""",
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
        ("/tmp/worksheets/number-tracing.pdf", "worksheets/number-tracing.pdf"),
        ("/tmp/worksheets/shapes-colors.pdf", "worksheets/shapes-colors.pdf"),
        ("/tmp/worksheets/sight-words-cards.pdf", "worksheets/sight-words-cards.pdf"),
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
