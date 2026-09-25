#!/usr/bin/env python3
"""批量生成 35 个会员可打印 PDF。reportlab 标准字体不支持 emoji，PDF 内只用纯文本。"""
import math
import os
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, lightgrey, black, white
from reportlab.pdfgen import canvas

W, H = A4
ORANGE = HexColor("#e8632b")
TEAL = HexColor("#2aa198")
PURPLE = HexColor("#7c5cbf")
GRAY = HexColor("#999999")
LIGHT = HexColor("#f2f2f2")
TRACE = HexColor("#d9d9d9")

random.seed(7)


def header(c, title, subtitle):
    c.setFillColor(ORANGE)
    c.rect(0, H - 70, W, 70, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(40, H - 35, title)
    c.setFont("Helvetica", 11)
    c.drawString(40, H - 55, subtitle)
    c.setFont("Helvetica", 9)
    c.drawRightString(W - 40, H - 30, "FunLearn Island")


def footer(c, page):
    c.setFillColor(lightgrey)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 30, "FunLearn Island - page %d" % page)


def new_canvas(path, title):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle(title)
    return c


# ---------------- math sheets ----------------
def math_sheet(path, title, subtitle, problems, answer_hint=""):
    c = new_canvas(path, title)
    per_page = 20
    page = 1
    for start in range(0, len(problems), per_page):
        header(c, title, subtitle)
        chunk = problems[start:start + per_page]
        c.setFillColor(black)
        for i, p in enumerate(chunk):
            col, row = divmod(i, 10)
            x = 70 + col * 240
            y = H - 150 - row * 55
            c.setFont("Helvetica-Bold", 20)
            c.drawString(x, y, p)
            c.setStrokeColor(GRAY)
            c.setLineWidth(1)
            c.line(x + 130, y - 6, x + 200, y - 6)
        if answer_hint and start == 0:
            c.setFillColor(TEAL)
            c.setFont("Helvetica", 11)
            c.drawString(70, 80, answer_hint)
        footer(c, page)
        c.showPage()
        page += 1
    c.save()


def gen_math_sub():
    probs = []
    for _ in range(40):
        a = random.randint(2, 10)
        b = random.randint(1, a)
        probs.append("%d - %d =" % (a, b))
    return probs


def gen_math_add20():
    probs = []
    for _ in range(40):
        a = random.randint(6, 15)
        b = random.randint(2, 20 - a)
        probs.append("%d + %d =" % (a, b))
    return probs


def gen_bonds():
    probs = []
    pairs = [(i, 10 - i) for i in range(1, 10)] * 4 + [(5, 5)] * 4
    random.shuffle(pairs)
    for a, b in pairs[:40]:
        probs.append("%d + __ = 10" % a if random.random() < 0.5 else "__ + %d = 10" % b)
    return probs


def gen_compare():
    probs = []
    for _ in range(24):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        if a == b:
            b = a + 1 if a < 20 else a - 1
        probs.append("%d  [ ]  %d" % (a, b))
    return probs


# ---------------- count / ten-frames ----------------
def count_sheet(path, title, subtitle, counts):
    c = new_canvas(path, title)
    header(c, title, subtitle)
    y = H - 140
    c.setFillColor(black)
    for n in counts:
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, y + 30, "Count and write:")
        cols = 10
        for i in range(n):
            x = 60 + (i % cols) * 42
            yy = y - (i // cols) * 42
            c.setFillColor(LIGHT)
            c.setStrokeColor(GRAY)
            shapes = ["circle", "rect", "tri"]
            kind = shapes[(n + i) % 3]
            if kind == "circle":
                c.circle(x + 15, yy + 10, 13, stroke=1, fill=1)
            elif kind == "rect":
                c.rect(x + 2, yy - 3, 26, 26, stroke=1, fill=1)
            else:
                p = c.beginPath()
                p.moveTo(x + 15, yy + 24)
                p.lineTo(x + 2, yy - 3)
                p.lineTo(x + 28, yy - 3)
                p.close()
                c.drawPath(p, stroke=1, fill=1)
        c.setFillColor(black)
        c.setFont("Helvetica", 13)
        c.drawString(60, y - 60, "There are ______")
        c.setStrokeColor(GRAY)
        c.rect(430, y - 75, 90, 40, stroke=1, fill=0)
        y -= 150
        if y < 120:
            footer(c, 1)
            c.showPage()
            header(c, title, subtitle)
            y = H - 140
    footer(c, 1)
    c.showPage()
    c.save()


def tenframes_sheet(path):
    c = new_canvas(path, "Ten-Frames Practice")
    header(c, "Ten-Frames Practice", "Color the frame to show each number")
    nums = [3, 7, 5, 9, 2, 8, 4, 6, 10, 1, 7, 5]
    y = H - 150
    for idx, n in enumerate(nums):
        x = 70 + (idx % 2) * 250
        if idx % 2 == 0 and idx > 0:
            y -= 110
        if y < 100:
            footer(c, 1)
            c.showPage()
            header(c, "Ten-Frames Practice", "Color the frame to show each number")
            y = H - 150
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y + 60, "Show %d:" % n)
        for i in range(10):
            cx = x + (i % 5) * 34
            cy = y + (i // 5) * 34
            c.setStrokeColor(GRAY)
            c.rect(cx, cy, 32, 32, stroke=1, fill=0)
        c.setFont("Helvetica", 11)
        c.drawString(x, y - 20, "How many more to make 10? ______")
        if idx % 2 == 1:
            pass
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- tracing ----------------
def tracing_letters(path, title, letters):
    c = new_canvas(path, title)
    page = 1
    for i, (letter, word) in enumerate(letters):
        if i % 2 == 0:
            if i > 0:
                footer(c, page)
                c.showPage()
                page += 1
            header(c, title, "Trace the big letter, then write it in the boxes")
        top = (i % 2 == 0)
        base_y = H - 160 if top else H - 480
        c.setFillColor(TRACE)
        c.setFont("Helvetica-Bold", 200)
        c.drawCentredString(W / 2 - 60, base_y - 220, letter)
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(60, base_y + 10, "%s is for %s" % (letter, word))
        c.setStrokeColor(GRAY)
        for b in range(3):
            c.rect(60 + b * 120, base_y - 300, 105, 70, stroke=1, fill=0)
        c.setFillColor(black)
        c.setFont("Helvetica", 11)
        c.drawString(60, base_y - 320, "Now you write it:")
    footer(c, page)
    c.showPage()
    c.save()


def trace_shapes_sheet(path):
    c = new_canvas(path, "Shape Tracing Pack")
    header(c, "Shape Tracing Pack", "Trace each shape 3 times, then name it")
    shapes = ["Circle", "Square", "Triangle", "Rectangle", "Diamond", "Oval"]
    y = H - 160
    for s in shapes:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y + 40, s)
        c.setStrokeColor(TRACE)
        c.setLineWidth(4)
        r = 32
        x = 200
        if s == "Circle":
            c.circle(x, y, r, stroke=1, fill=0)
        elif s == "Square":
            c.rect(x - r, y - r, 2 * r, 2 * r, stroke=1, fill=0)
        elif s == "Rectangle":
            c.rect(x - 1.4 * r, y - 0.7 * r, 2.8 * r, 1.4 * r, stroke=1, fill=0)
        elif s == "Triangle":
            p = c.beginPath()
            p.moveTo(x, y + r); p.lineTo(x - r, y - r); p.lineTo(x + r, y - r); p.close()
            c.drawPath(p, stroke=1, fill=0)
        elif s == "Diamond":
            p = c.beginPath()
            p.moveTo(x, y + r); p.lineTo(x + r * 0.7, y); p.lineTo(x, y - r); p.lineTo(x - r * 0.7, y); p.close()
            c.drawPath(p, stroke=1, fill=0)
        else:
            c.ellipse(x - 1.3 * r, y - 0.75 * r, x + 1.3 * r, y + 0.75 * r, stroke=1, fill=0)
        c.setStrokeColor(GRAY)
        c.setLineWidth(1)
        for b in range(2):
            c.rect(330 + b * 110, y - 35, 95, 70, stroke=1, fill=0)
        y -= 95
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- flashcards ----------------
def flashcard_grid(path, title, subtitle, cards, cols=3):
    c = new_canvas(path, title)
    rows = 3
    per_page = cols * rows
    cw, chh = 155, 110
    page = 1
    for start in range(0, len(cards), per_page):
        header(c, title, subtitle)
        chunk = cards[start:start + per_page]
        x0 = (W - cols * cw) / 2
        y0 = H - 160
        for i, card in enumerate(chunk):
            r, col = divmod(i, cols)
            x = x0 + col * cw
            y = y0 - r * chh
            text, sub, color = card
            c.setStrokeColor(lightgrey)
            c.setDash(4, 3)
            c.rect(x, y - chh, cw, chh, stroke=1, fill=0)
            c.setDash()
            c.setFillColor(color)
            size = 26 if len(text) <= 6 else 20
            c.setFont("Helvetica-Bold", size)
            c.drawCentredString(x + cw / 2, y - chh / 2 + (2 if not sub else 8), text)
            if sub:
                c.setFillColor(GRAY)
                c.setFont("Helvetica", 11)
                c.drawCentredString(x + cw / 2, y - chh / 2 - 22, sub)
        footer(c, page)
        c.showPage()
        page += 1
    c.save()


def fc_color(i):
    return [PURPLE, TEAL, ORANGE][i % 3]

# ---------------- dot to dot ----------------
def dotdot_sheet(path):
    c = new_canvas(path, "Dot-to-Dot")
    header(c, "Dot-to-Dot: 1 to 20", "Connect the dots in order, then color the picture")
    def blob(cx, cy, r, n, wobble=0.25):
        pts = []
        for i in range(n):
            ang = 2 * math.pi * i / n - math.pi / 2
            rr = r * (1 + wobble * math.sin(3 * ang + n))
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        return pts
    shapes = [blob(W / 2, H / 2 - 40, 170, 12), blob(W / 2, H / 2 - 40, 170, 16),
              blob(W / 2, H / 2 - 40, 170, 20)]
    for pg, pts in enumerate(shapes):
        if pg > 0:
            footer(c, pg)
            c.showPage()
            header(c, "Dot-to-Dot: 1 to 20", "Connect the dots in order, then color the picture")
        c.setFillColor(black)
        for i, (x, y) in enumerate(pts):
            c.circle(x, y, 3, stroke=0, fill=1)
            c.setFont("Helvetica", 10)
            c.drawString(x + 8, y + 6, str(i + 1))
    footer(c, 3)
    c.showPage()
    c.save()


# ---------------- mazes ----------------
def gen_maze(cols, rows):
    walls = [[{"N": True, "S": True, "E": True, "W": True} for _ in range(cols)] for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        x, y = stack[-1]
        nbs = []
        for dx, dy, d1, d2 in [(0, -1, "N", "S"), (0, 1, "S", "N"), (1, 0, "E", "W"), (-1, 0, "W", "E")]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx]:
                nbs.append((nx, ny, d1, d2))
        if nbs:
            nx, ny, d1, d2 = random.choice(nbs)
            walls[y][x][d1] = False
            walls[ny][nx][d2] = False
            visited[ny][nx] = True
            stack.append((nx, ny))
        else:
            stack.pop()
    return walls


def draw_maze(c, walls, x0, y0, cell):
    rows, cols = len(walls), len(walls[0])
    c.setStrokeColor(black)
    c.setLineWidth(2)
    for y in range(rows):
        for x in range(cols):
            w = walls[y][x]
            px, py = x0 + x * cell, y0 - y * cell
            if w["N"]:
                c.line(px, py, px + cell, py)
            if w["S"]:
                c.line(px, py - cell, px + cell, py - cell)
            if w["W"]:
                c.line(px, py, px, py - cell)
            if w["E"]:
                c.line(px + cell, py, px + cell, py - cell)
    # start / finish markers
    c.setFillColor(TEAL)
    c.circle(x0 + cell / 2, y0 - cell / 2, 7, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    px = x0 + (cols - 1) * cell + cell / 2
    py = y0 - (rows - 1) * cell - cell / 2
    c.rect(px - 7, py - 7, 14, 14, stroke=0, fill=1)


def mazes_sheet(path):
    c = new_canvas(path, "Easy Mazes")
    sizes = [(5, 5), (7, 7), (7, 7), (9, 9), (9, 9), (11, 11)]
    page = 1
    for i, (cols, rows) in enumerate(sizes):
        if i % 2 == 0:
            if i > 0:
                footer(c, page)
                c.showPage()
                page += 1
            header(c, "Easy Mazes", "Start at the green dot, finish at the orange square")
        walls = gen_maze(cols, rows)
        cell = 300 / max(cols, rows)
        top = (i % 2 == 0)
        x0 = (W - cols * cell) / 2
        y0 = (H - 120 - (0 if top else 330)) if top else H - 450
        if top:
            y0 = H - 130
        else:
            y0 = H - 130 - 340
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(60, y0 + 12, "Maze %d" % (i + 1))
        draw_maze(c, walls, x0, y0, cell)
    footer(c, page)
    c.showPage()
    c.save()


# ---------------- color by number ----------------
def cbn_sheet(path):
    c = new_canvas(path, "Color by Number")
    header(c, "Color by Number", "Match each number to the color key")
    # heart pattern on 12x12 grid
    heart = [
        ".XX.XX......",
        "XXXXXXXX....",
        "XXXXXXXX....",
        ".XXXXXX.....",
        "..XXXX......",
        "...XX.......",
    ]
    grid = []
    for r in range(12):
        row = []
        for col in range(12):
            if r < 6 and col < 11 and heart[r][col] == "X":
                row.append(1)
            elif (r - 6) ** 2 + (col - 5) ** 2 < 14:
                row.append(2)
            else:
                row.append(3)
        grid.append(row)
    legend = [(1, "RED", HexColor("#e74c3c")), (2, "BLUE", HexColor("#3498db")), (3, "YELLOW", HexColor("#f1c40f"))]
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(black)
    c.drawString(60, H - 110, "Color key:")
    for i, (num, name, col) in enumerate(legend):
        x = 60 + i * 150
        c.setFillColor(col)
        c.rect(x, H - 150, 26, 26, stroke=1, fill=1)
        c.setFillColor(black)
        c.setFont("Helvetica", 12)
        c.drawString(x + 34, H - 132, "%d = %s" % (num, name))
    cell = 34
    x0 = (W - 12 * cell) / 2
    y0 = H - 200
    for r in range(12):
        for col in range(12):
            x = x0 + col * cell
            y = y0 - r * cell
            c.setStrokeColor(GRAY)
            c.rect(x, y - cell, cell, cell, stroke=1, fill=0)
            c.setFillColor(black)
            c.setFont("Helvetica", 10)
            c.drawCentredString(x + cell / 2, y - cell / 2 - 4, str(grid[r][col]))
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- patterns ----------------
def patterns_sheet(path):
    c = new_canvas(path, "Complete the Pattern")
    header(c, "Complete the Pattern", "Say the pattern out loud, then draw what comes next")
    pats = [
        (["circle", "square"], "AB"),
        (["circle", "circle", "square"], "ABB"),
        (["tri", "square", "circle"], "ABC"),
        (["square", "tri", "tri"], "ABB"),
        (["circle", "tri", "circle", "tri"], "AB"),
        (["rect", "rect", "circle"], "AAB"),
    ]
    y = H - 140
    for pi, (seq, name) in enumerate(pats):
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y + 28, "Pattern %d (%s):" % (pi + 1, name))
        x = 60
        full = (seq * 4)[:9]
        for s in full:
            draw_shape(c, s, x + 18, y, 15)
            x += 42
        c.setStrokeColor(GRAY)
        c.setDash(4, 3)
        for b in range(3):
            c.rect(x + 6, y - 16, 34, 34, stroke=1, fill=0)
            x += 42
        c.setDash()
        y -= 80
        if y < 90 and pi < len(pats) - 1:
            footer(c, 1)
            c.showPage()
            header(c, "Complete the Pattern", "Say the pattern out loud, then draw what comes next")
            y = H - 140
    footer(c, 1)
    c.showPage()
    c.save()


def draw_shape(c, kind, x, y, r):
    c.setStrokeColor(HexColor("#555555"))
    c.setLineWidth(1.5)
    if kind == "circle":
        c.circle(x, y, r, stroke=1, fill=0)
    elif kind == "square":
        c.rect(x - r, y - r, 2 * r, 2 * r, stroke=1, fill=0)
    elif kind == "rect":
        c.rect(x - 1.4 * r, y - 0.7 * r, 2.8 * r, 1.4 * r, stroke=1, fill=0)
    elif kind == "tri":
        p = c.beginPath()
        p.moveTo(x, y + r); p.lineTo(x - r, y - r); p.lineTo(x + r, y - r); p.close()
        c.drawPath(p, stroke=1, fill=0)


# ---------------- cutting ----------------
def cutting_sheet(path):
    c = new_canvas(path, "Cutting Practice")
    header(c, "Cutting Practice", "Cut along the dashed lines - thumbs up on top!")
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.setDash(6, 4)
    y = H - 150
    # straight
    c.line(60, y, W - 60, y)
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    c.drawString(60, y + 14, "Straight")
    y -= 90
    # zigzag
    p = c.beginPath()
    x = 60
    p.moveTo(x, y)
    up = True
    while x < W - 60:
        x += 30
        p.lineTo(x, y + (18 if up else -18))
        up = not up
    c.drawPath(p, stroke=1, fill=0)
    c.drawString(60, y + 34, "Zigzag")
    y -= 100
    # wave
    p = c.beginPath()
    p.moveTo(60, y)
    x = 60
    while x < W - 60:
        x += 20
        p.curveTo(x - 15, y + 20, x - 5, y - 20, x, y)
    c.drawPath(p, stroke=1, fill=0)
    c.drawString(60, y + 34, "Wavy")
    y -= 110
    # spiral
    cx, cy = W / 2, y
    p = c.beginPath()
    for t in range(0, 360 * 3, 5):
        ang = math.radians(t)
        r = 4 + t * 0.09
        x = cx + r * math.cos(ang)
        yy = cy + r * math.sin(ang) * 0.7
        if t == 0:
            p.moveTo(x, yy)
        else:
            p.lineTo(x, yy)
    c.drawPath(p, stroke=1, fill=0)
    c.drawString(60, y + 70, "Spiral")
    c.setDash()
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- symmetry ----------------
def symmetry_sheet(path):
    c = new_canvas(path, "Symmetry Drawing")
    header(c, "Symmetry Drawing", "Complete the mirror side - fold on the dotted line first")
    # butterfly half
    cx = W / 2
    y = H - 320
    c.setStrokeColor(GRAY)
    c.setDash(4, 3)
    c.line(cx, y + 110, cx, y - 110)
    c.setDash()
    c.setStrokeColor(black)
    c.setLineWidth(2)
    # left wing (upper + lower)
    p = c.beginPath()
    p.moveTo(cx, y + 40)
    p.curveTo(cx - 90, y + 110, cx - 130, y + 60, cx - 60, y + 30)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath()
    p.moveTo(cx, y - 20)
    p.curveTo(cx - 80, y - 30, cx - 90, y - 90, cx - 30, y - 70)
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    c.line(cx, y + 60, cx, y - 90)  # body
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(60, y - 140, "Butterfly - draw the right half!")
    # face half
    y2 = y - 260
    c.setStrokeColor(GRAY)
    c.setDash(4, 3)
    c.line(cx, y2 + 80, cx, y2 - 80)
    c.setDash()
    c.setStrokeColor(black)
    c.setLineWidth(2)
    c.arc(cx - 60, y2 - 60, cx, y2 + 60, startAng=90, extent=180)
    c.circle(cx - 30, y2 + 20, 6, stroke=1, fill=0)  # eye
    p = c.beginPath()
    p.moveTo(cx - 45, y2 - 25)
    p.curveTo(cx - 30, y2 - 40, cx - 10, y2 - 35, cx, y2 - 25)
    c.drawPath(p, stroke=1, fill=0)  # smile half
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(60, y2 - 110, "Face - draw the right half!")
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- clocks ----------------
def clocks_sheet(path):
    c = new_canvas(path, "Telling Time Practice")
    header(c, "Telling Time Practice", "Draw the hands - short hand FIRST")
    times = [("3 o'clock", 3, 0), ("7 o'clock", 7, 0), ("10 o'clock", 10, 0),
             ("half past 4", 4, 30), ("half past 9", 9, 30), ("12 o'clock", 12, 0),
             ("half past 2", 2, 30), ("5 o'clock", 5, 0), ("half past 11", 11, 30)]
    x0, y0 = 90, H - 170
    for i, (label, h, m) in enumerate(times):
        col, row = i % 3, i // 3
        x = x0 + col * 150
        y = y0 - row * 150
        c.setStrokeColor(black)
        c.setLineWidth(2)
        c.circle(x, y, 42, stroke=1, fill=0)
        for hh in range(12):
            ang = math.radians(hh * 30)
            x1 = x + 36 * math.sin(ang)
            y1 = y + 36 * math.cos(ang)
            c.circle(x1, y1, 1.5, stroke=0, fill=1)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x, y - 62, label)
        c.setFont("Helvetica", 10)
        c.setFillColor(GRAY)
        c.drawCentredString(x, y - 76, "draw the hands")
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- coins ----------------
def coins_sheet(path):
    c = new_canvas(path, "Counting Coins")
    header(c, "Counting Coins", "Name each coin - remember, size does NOT match value")
    coins = [("penny", "1c", 26), ("nickel", "5c", 30), ("dime", "10c", 22), ("quarter", "25c", 34)]
    y = H - 150
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(60, y + 30, "The four coins:")
    x = 80
    for name, val, r in coins:
        c.setStrokeColor(black)
        c.circle(x, y, r, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x, y - 4, val)
        c.setFont("Helvetica", 11)
        c.drawCentredString(x, y - r - 16, name)
        x += 110
    y -= 130
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(black)
    c.drawString(60, y + 30, "Count each piggy bank:")
    banks = [[25, 10, 5, 1], [10, 10, 5], [25, 25, 1, 1], [5, 5, 5, 1]]
    for bi, bank in enumerate(banks):
        c.setFont("Helvetica", 12)
        c.drawString(60, y, "Bank %d: %s = ______c" % (bi + 1, " + ".join("%dc" % v for v in bank)))
        y -= 40
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(60, y + 30, "You have 40c. Circle what you can buy:")
    c.setFont("Helvetica", 12)
    for item, price in [("sticker pack - 25c", 25), ("balloon - 15c", 15), ("toy car - 50c", 50), ("candy - 10c", 10)]:
        c.drawString(60, y, item)
        c.setStrokeColor(GRAY)
        c.circle(330, y + 4, 12, stroke=1, fill=0)
        y -= 34
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- charts & journals ----------------
def table_sheet(path, title, subtitle, headers, rows, note="", checkbox=True):
    c = new_canvas(path, title)
    header(c, title, subtitle)
    col_w = (W - 120) / len(headers)
    y = H - 150
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 12)
    for i, h in enumerate(headers):
        c.drawString(70 + i * col_w, y, h)
    y -= 10
    c.setStrokeColor(GRAY)
    c.line(60, y, W - 60, y)
    y -= 28
    c.setFont("Helvetica", 11)
    for r in rows:
        for i, val in enumerate(r):
            if checkbox and i == len(r) - 1 and val == "":
                c.rect(70 + i * col_w, y - 4, 16, 16, stroke=1, fill=0)
            else:
                c.drawString(70 + i * col_w, y, val)
        y -= 34
        if y < 90:
            footer(c, 1)
            c.showPage()
            header(c, title, subtitle)
            y = H - 150
    if note:
        c.setFillColor(TEAL)
        c.setFont("Helvetica", 11)
        c.drawString(60, max(y - 20, 60), note)
    footer(c, 1)
    c.showPage()
    c.save()


def journal_sheet(path, title, subtitle, prompts, boxes=True):
    c = new_canvas(path, title)
    header(c, title, subtitle)
    y = H - 150
    c.setFillColor(black)
    for p in prompts:
        c.setFont("Helvetica-Bold", 13)
        c.drawString(60, y, p)
        y -= 24
        if boxes:
            c.setStrokeColor(GRAY)
            c.rect(60, y - 90, W - 120, 90, stroke=1, fill=0)
            y -= 110
        else:
            for _ in range(3):
                c.setStrokeColor(lightgrey)
                c.line(60, y, W - 60, y)
                y -= 26
            y -= 14
        if y < 130:
            footer(c, 1)
            c.showPage()
            header(c, title, subtitle)
            y = H - 150
    footer(c, 1)
    c.showPage()
    c.save()


def schedule_sheet(path):
    c = new_canvas(path, "Weekly Visual Schedule")
    header(c, "Weekly Visual Schedule", "Fill in your repeating blocks - let the paper be the boss")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    slots = ["Morning", "Afternoon", "Evening"]
    col_w = (W - 160) / 7
    row_h = 90
    x0, y0 = 100, H - 180
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(black)
    for i, d in enumerate(days):
        c.drawCentredString(x0 + i * col_w + col_w / 2, y0 + 16, d)
    c.setFont("Helvetica", 10)
    for r, s in enumerate(slots):
        c.drawString(30, y0 - r * row_h - 50, s)
        for i in range(7):
            x = x0 + i * col_w
            y = y0 - r * row_h
            c.setStrokeColor(GRAY)
            c.rect(x, y - row_h, col_w, row_h, stroke=1, fill=0)
    c.setFillColor(TEAL)
    c.setFont("Helvetica", 11)
    c.drawString(60, 70, "Tip: draw a small picture in each block - pictures beat words for little kids.")
    footer(c, 1)
    c.showPage()
    c.save()


def storyseq_sheet(path):
    c = new_canvas(path, "Story Sequencing Cards")
    header(c, "Story Sequencing Cards", "Draw first, next, then, last - then tell the story")
    labels = ["1. FIRST", "2. NEXT", "3. THEN", "4. LAST"]
    for i, lab in enumerate(labels):
        col, row = i % 2, i // 2
        x = 60 + col * 250
        y = H - 180 - row * 270
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y + 10, lab)
        c.setStrokeColor(GRAY)
        c.setLineWidth(1.5)
        c.rect(x, y - 220, 230, 210, stroke=1, fill=0)
    footer(c, 1)
    c.showPage()
    c.save()


def allaboutme_sheet(path):
    c = new_canvas(path, "All About Me")
    header(c, "All About Me", "Fill it in, draw in every box, hang it up!")
    c.setFillColor(black)
    prompts = ["My name is...", "I am ___ years old", "My favorite color",
               "My favorite animal", "My favorite food", "When I grow up I want to be..."]
    y = H - 150
    for i, p in enumerate(prompts):
        col, row = i % 2, i // 2
        x = 60 + col * 250
        yy = y - row * 170
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(PURPLE if i % 2 == 0 else TEAL)
        c.drawString(x, yy, p)
        c.setStrokeColor(GRAY)
        c.rect(x, yy - 110, 230, 95, stroke=1, fill=0)
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, 70, "Date: __________    Redo in 6 months and compare!")
    footer(c, 1)
    c.showPage()
    c.save()


def scavenger_sheet(path):
    c = new_canvas(path, "Nature Scavenger Hunt")
    header(c, "Nature Scavenger Hunt", "Find each thing, check it off, bring treasures home")
    items = ["Something smooth", "Something rough", "A Y-shaped stick", "3 different leaves",
             "Something red in nature", "A feather", "Something that makes a sound",
             "The tiniest rock you can find", "Something a bird might eat", "A flower",
             "Something round", "An interesting shadow", "Something that smells good",
             "A seed or nut", "Something you have never seen before", "Your favorite find!"]
    y = H - 140
    c.setFillColor(black)
    for i, item in enumerate(items):
        col, row = i % 2, i // 2
        x = 60 + col * 250
        yy = y - row * 40
        c.setStrokeColor(GRAY)
        c.rect(x, yy - 4, 16, 16, stroke=1, fill=0)
        c.setFont("Helvetica", 12)
        c.drawString(x + 26, yy, item)
    footer(c, 1)
    c.showPage()
    c.save()


# ---------------- dispatch ----------------
def build_all(outdir):
    os.makedirs(outdir, exist_ok=True)
    P = lambda f: os.path.join(outdir, f)
    math_sheet(P("subtraction-to-10.pdf"), "Subtraction Practice", "Numbers to 10 - one page a day", gen_math_sub())
    math_sheet(P("addition-to-20.pdf"), "Addition Practice", "Numbers to 20", gen_math_add20())
    math_sheet(P("number-bonds-10.pdf"), "Number Bonds to 10", "Fill in the missing number", gen_bonds())
    math_sheet(P("greater-less-than.pdf"), "Greater Than / Less Than", "Draw > or < in the box - the mouth eats the bigger number", gen_compare())
    count_sheet(P("counting-to-20.pdf"), "Count and Write to 20", "Point, count, write, color", [11, 13, 15, 17, 19, 12, 14, 16, 18, 20])
    tenframes_sheet(P("tens-frames-10.pdf"))
    tracing_letters(P("alphabet-tracing-a-m.pdf"), "Alphabet Tracing A-M",
                    [(ch, w) for ch, w in zip("ABCDEFGHJKLM", ["Apple", "Ball", "Cat", "Dog", "Egg", "Fish", "Grapes", "Hat", "Ice", "Jam", "Kite", "Lion", "Moon"])])
    tracing_letters(P("alphabet-tracing-n-z.pdf"), "Alphabet Tracing N-Z",
                    [(ch, w) for ch, w in zip("NOPQRSTUVWXYZ", ["Nest", "Orange", "Pig", "Queen", "Rain", "Sun", "Tiger", "Umbrella", "Van", "Whale", "Xylophone", "Yo-yo", "Zebra"])])
    trace_shapes_sheet(P("shape-tracing.pdf"))
    flashcard_grid(P("word-families.pdf"), "Word Families", "Cut out - change the first letter, hear the pattern",
                   [("-at", "cat hat mat", fc_color(0)), ("-an", "can ran pan", fc_color(1)), ("-ot", "hot pot dot", fc_color(2)),
                    ("-op", "hop mop top", fc_color(0)), ("-ug", "hug bug rug", fc_color(1)), ("-ed", "bed red fed", fc_color(2)),
                    ("-in", "pin win tin", fc_color(0)), ("-ake", "cake lake make", fc_color(1))] * 6)
    rhymes = [("cat", "hat"), ("dog", "frog"), ("sun", "run"), ("cake", "snake"), ("ball", "tall"),
              ("fish", "dish"), ("bear", "chair"), ("pig", "wig"), ("car", "star"), ("bee", "tree"),
              ("cup", "pup"), ("box", "fox")]
    flashcard_grid(P("rhyming-pairs.pdf"), "Rhyming Pairs", "Find the pair that rhymes!",
                   [(a, "rhymes with", fc_color(0)) for a, b in rhymes] + [(b, "rhymes with", fc_color(1)) for a, b in rhymes], cols=4)
    facts = []
    for _ in range(36):
        a = random.randint(1, 9)
        b = random.randint(1, 9 - a + 1)
        facts.append(("%d + %d" % (a, b), "=", fc_color(a)))
    flashcard_grid(P("addition-flashcards.pdf"), "Addition Flashcards", "2-second rule: instant = keep!", facts, cols=4)
    facts = []
    for _ in range(36):
        a = random.randint(2, 10)
        b = random.randint(1, a)
        facts.append(("%d - %d" % (a, b), "=", fc_color(b)))
    flashcard_grid(P("subtraction-flashcards.pdf"), "Subtraction Flashcards", "2-second rule: instant = keep!", facts, cols=4)
    animals = [("Lion", "wild"), ("Dog", "pet"), ("Cat", "pet"), ("Fish", "water"), ("Bird", "flies"),
               ("Bear", "wild"), ("Frog", "pond"), ("Horse", "farm"), ("Cow", "farm"), ("Duck", "farm"),
               ("Shark", "ocean"), ("Whale", "ocean"), ("Monkey", "jungle"), ("Tiger", "wild"),
               ("Rabbit", "pet"), ("Turtle", "slow"), ("Bee", "flies"), ("Butterfly", "flies"),
               ("Pig", "farm"), ("Sheep", "farm"), ("Elephant", "big"), ("Giraffe", "tall"),
               ("Penguin", "cold"), ("Owl", "night")]
    flashcard_grid(P("animal-flashcards.pdf"), "Animal Flashcards", "Name it, then sort: farm / wild / ocean",
                   [(a, s, fc_color(i)) for i, (a, s) in enumerate(animals)], cols=4)
    colors = [("Red", ""), ("Blue", ""), ("Yellow", ""), ("Green", ""), ("Orange", ""), ("Purple", ""),
              ("Pink", ""), ("Brown", ""), ("Black", ""), ("White", ""), ("Gray", ""), ("Light Blue", "shade")]
    flashcard_grid(P("color-flashcards.pdf"), "Color Flashcards", "Hold up a card - find that color in the room!",
                   [(t, s, fc_color(i)) for i, (t, s) in enumerate(colors)], cols=4)
    emotions = [("Happy", ""), ("Sad", ""), ("Angry", ""), ("Scared", ""), ("Excited", ""),
                ("Frustrated", ""), ("Proud", ""), ("Nervous", ""), ("Silly", ""), ("Calm", ""),
                ("Jealous", ""), ("Surprised", ""), ("Tired", ""), ("Brave", ""), ("Lonely", ""), ("Thankful", "")]
    flashcard_grid(P("emotion-flashcards.pdf"), "Emotions Flashcards", "Which face are you today?",
                   [(t, s, fc_color(i)) for i, (t, s) in enumerate(emotions)], cols=4)
    dotdot_sheet(P("dot-to-dot-fun.pdf"))
    mazes_sheet(P("easy-mazes.pdf"))
    cbn_sheet(P("color-by-number.pdf"))
    patterns_sheet(P("pattern-complete.pdf"))
    cutting_sheet(P("cutting-practice.pdf"))
    symmetry_sheet(P("symmetry-draw.pdf"))
    clocks_sheet(P("telling-time-practice.pdf"))
    coins_sheet(P("money-coins.pdf"))
    table_sheet(P("chore-chart.pdf"), "Weekly Chore Chart", "Pick 3 a day - stars are earned, never taken away",
                ["Chore", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                [["Make bed", "", "", "", "", "", "", ""], ["Put toys away", "", "", "", "", "", "", ""],
                 ["Set the table", "", "", "", "", "", "", ""], ["Feed pet", "", "", "", "", "", "", ""],
                 ["Wipe table", "", "", "", "", "", "", ""], ["Sort laundry", "", "", "", "", "", "", ""],
                 ["Water plants", "", "", "", "", "", "", ""], ["Tidy shoes", "", "", "", "", "", "", ""]])
    table_sheet(P("reward-chart.pdf"), "4-Week Sticker Chart", "One goal, stickers right away, celebrate milestones",
                ["Week", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                [["Week 1 - goal: __________", "", "", "", "", "", "", ""],
                 ["Week 2", "", "", "", "", "", "", ""],
                 ["Week 3", "", "", "", "", "", "", ""],
                 ["Week 4 - celebration!", "", "", "", "", "", "", ""]])
    table_sheet(P("weather-tracker.pdf"), "7-Day Weather Tracker", "Same time each morning - draw, measure, record",
                ["Day", "Clouds (draw)", "Temp", "Rain?", "Wind"],
                [["Monday", "", "", "", ""], ["Tuesday", "", "", "", ""], ["Wednesday", "", "", "", ""],
                 ["Thursday", "", "", "", ""], ["Friday", "", "", "", ""], ["Saturday", "", "", "", ""],
                 ["Sunday", "", "", "", ""]], note="Sunday question: what was the pattern this week?")
    journal_sheet(P("feelings-journal.pdf"), "Feelings Journal", "One page a day - pick it, draw it, say why",
                  ["Today I feel...", "I feel this way because...", "Something that would help:"])
    journal_sheet(P("gratitude-journal.pdf"), "Gratitude Journal", "One page a day - specific beats generic",
                  ["One good thing today:", "One kind person:", "One thing in nature:"])
    table_sheet(P("planting-log.pdf"), "Bean Diary: 14-Day Log", "Observe daily - the drawing IS the data",
                ["Day", "Date", "What I see (draw)", "Height", ""],
                [["Day %d" % d, "", "", "", ""] for d in range(1, 15)], checkbox=False,
                note="Measure the sprout with a ruler every day.")
    journal_sheet(P("science-journal.pdf"), "My Experiment Sheet", "One sheet per experiment - guess BEFORE testing",
                  ["My question:", "My guess:", "What I did:", "What happened:", "What surprised me:"], boxes=False)
    schedule_sheet(P("weekly-schedule.pdf"))
    storyseq_sheet(P("story-sequence.pdf"))
    allaboutme_sheet(P("all-about-me.pdf"))
    scavenger_sheet(P("nature-scavenger-hunt.pdf"))
    print("all 35 pdfs built")


if __name__ == "__main__":
    build_all("/tmp/worksheets2")
