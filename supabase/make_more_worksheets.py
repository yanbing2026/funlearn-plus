#!/usr/bin/env python3
"""生成第二批示例 PDF：数字描红、形状涂色、Sight Words 闪卡。"""
import math
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, lightgrey, black
from reportlab.pdfgen import canvas

W, H = A4
ORANGE = HexColor("#e8632b")
TEAL = HexColor("#2aa198")
PURPLE = HexColor("#7c5cbf")
LIGHT = HexColor("#f2f2f2")


def header(c, title, subtitle):
    c.setFillColor(ORANGE)
    c.rect(0, H - 70, W, 70, stroke=0, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, H - 35, title)
    c.setFont("Helvetica", 11)
    c.drawString(40, H - 55, subtitle)
    c.setFont("Helvetica", 9)
    c.drawRightString(W - 40, H - 30, "FunLearn Island")


def footer(c, page):
    c.setFillColor(lightgrey)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 30, f"FunLearn Island · funlearn · page {page}")


def number_tracing(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Number Tracing 1-10")
    for n in range(1, 11):
        header(c, "Number Tracing", "Trace the big number, then write it in the boxes")
        # big traceable number (light gray to trace over)
        c.setFillColor(HexColor("#d9d9d9"))
        c.setFont("Helvetica-Bold", 260)
        c.drawCentredString(W / 2, H - 400, str(n))
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(W / 2, H - 150, f"Trace the number {n}")
        # practice boxes
        y = 250
        c.setFont("Helvetica", 12)
        c.setFillColor(black)
        c.drawString(60, y + 40, "Now you write it:")
        for i in range(4):
            x = 60 + i * 125
            c.setStrokeColor(lightgrey)
            c.setLineWidth(1.5)
            c.rect(x, y - 70, 110, 90, stroke=1, fill=0)
        # count-the-dots
        c.setFont("Helvetica", 12)
        c.drawString(60, 130, f"Count and color {n} dot(s):")
        cols = 5
        for i in range(n):
            x = 60 + (i % cols) * 50
            y = 40 + (i // cols) * 50
            c.setFillColor(LIGHT)
            c.setStrokeColor(lightgrey)
            c.circle(x + 15, y + 15, 14, stroke=1, fill=1)
        footer(c, n)
        c.showPage()
    c.save()
    print("wrote", path)


def shapes_colors(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Shapes and Colors Coloring Pack")
    header(c, "Shapes & Colors", "Color each shape, then say its name out loud")
    shapes = [
        ("Circle", "circle"),
        ("Square", "square"),
        ("Triangle", "triangle"),
        ("Rectangle", "rectangle"),
        ("Diamond", "diamond"),
        ("Oval", "oval"),
    ]
    cx = [W / 4, 3 * W / 4]
    cy = [H - 220, H - 430, H - 640]
    for i, (name, kind) in enumerate(shapes):
        x, y = cx[i % 2], cy[i // 2]
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(x, y - 95, name)
        c.setStrokeColor(HexColor("#999999"))
        c.setLineWidth(2.5)
        s = 55
        if kind == "circle":
            c.circle(x, y, s, stroke=1, fill=0)
        elif kind == "square":
            c.rect(x - s, y - s, 2 * s, 2 * s, stroke=1, fill=0)
        elif kind == "rectangle":
            c.rect(x - 1.4 * s, y - 0.7 * s, 2.8 * s, 1.4 * s, stroke=1, fill=0)
        elif kind == "triangle":
            p = c.beginPath()
            p.moveTo(x, y + s)
            p.lineTo(x - s, y - s)
            p.lineTo(x + s, y - s)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
        elif kind == "diamond":
            p = c.beginPath()
            p.moveTo(x, y + s)
            p.lineTo(x + s * 0.7, y)
            p.lineTo(x, y - s)
            p.lineTo(x - s * 0.7, y)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
        elif kind == "oval":
            c.ellipse(x - 1.3 * s, y - 0.75 * s, x + 1.3 * s, y + 0.75 * s, stroke=1, fill=0)
    c.setFillColor(TEAL)
    c.setFont("Helvetica", 12)
    c.drawCentredString(W / 2, 90, "Bonus: find each shape somewhere in your house!")
    footer(c, 1)
    c.showPage()

    # page 2: color-by-instruction
    header(c, "Color by Instruction", "Read each line, then color it the right color")
    tasks = [
        ("Color the circle RED", HexColor("#e74c3c")),
        ("Color the square BLUE", HexColor("#3498db")),
        ("Color the triangle GREEN", HexColor("#27ae60")),
        ("Color the star shape YELLOW", HexColor("#f1c40f")),
    ]
    y = H - 180
    for label, col in tasks:
        c.setFillColor(black)
        c.setFont("Helvetica", 13)
        c.drawString(60, y + 60, label)
        c.setStrokeColor(HexColor("#999999"))
        c.setLineWidth(2)
        c.circle(90, y, 32, stroke=1, fill=0)
        c.rect(200, y - 32, 64, 64, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(360, y + 32)
        p.lineTo(328, y - 32)
        p.lineTo(392, y - 32)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        # star (5-point)
        sx, sy, r = 480, y, 36
        pts = []
        for k in range(10):
            ang = math.pi / 2 + k * math.pi / 5
            rad = r if k % 2 == 0 else r * 0.45
            pts.append((sx + rad * math.cos(ang), sy + rad * math.sin(ang)))
        sp = c.beginPath()
        sp.moveTo(*pts[0])
        for pt in pts[1:]:
            sp.lineTo(*pt)
        sp.close()
        c.drawPath(sp, stroke=1, fill=0)
        y -= 150
    footer(c, 2)
    c.showPage()
    c.save()
    print("wrote", path)


SIGHT_WORDS = ["the", "and", "a", "to", "said", "in", "he", "I", "of",
               "it", "was", "you", "they", "on", "she", "is", "for",
               "at", "his", "but", "that", "with", "all", "we", "can"]


def sight_words(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Sight Words Flashcards - First 25")
    header(c, "Sight Words Flashcards", "Cut out the cards. Read fast — no sounding out!")
    per_row, rows = 3, 3
    cw, chh = 150, 110
    x0 = (W - per_row * cw) / 2
    y0 = H - 160
    page = 1
    for i, word in enumerate(SIGHT_WORDS):
        slot = i % (per_row * rows)
        if i > 0 and slot == 0:
            footer(c, page)
            c.showPage()
            page += 1
            header(c, "Sight Words Flashcards", "Cut out the cards. Read fast — no sounding out!")
        r, col = divmod(slot, per_row)
        x = x0 + col * cw
        y = y0 - r * chh
        c.setStrokeColor(lightgrey)
        c.setLineWidth(1)
        c.setDash(4, 3)
        c.rect(x, y - chh, cw, chh, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(PURPLE if i % 2 == 0 else TEAL)
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(x + cw / 2, y - chh / 2 - 10, word)
    footer(c, page)
    c.showPage()
    # instructions page
    header(c, "How to Play", "Three games with these flashcards")
    games = [
        ("1. Fast flash", "Hold up a card for 2 seconds. Correct = keep it. Goal: collect all 25."),
        ("2. Word hunt", "Hide 5 cards around the room. Call out a word — race to find it."),
        ("3. Sentence builder", "Draw 3 cards and make a silly sentence using all three words."),
    ]
    y = H - 200
    c.setFillColor(black)
    for title, desc in games:
        c.setFont("Helvetica-Bold", 15)
        c.drawString(60, y, title)
        c.setFont("Helvetica", 12)
        c.drawString(60, y - 28, desc)
        y -= 90
    c.setFont("Helvetica", 12)
    c.setFillColor(TEAL)
    c.drawString(60, y - 20, "Tip: practice 5 new words a week. Review old ones every day.")
    footer(c, page + 1)
    c.showPage()
    c.save()
    print("wrote", path)


if __name__ == "__main__":
    import os
    os.makedirs("/tmp/worksheets", exist_ok=True)
    number_tracing("/tmp/worksheets/number-tracing.pdf")
    shapes_colors("/tmp/worksheets/shapes-colors.pdf")
    sight_words("/tmp/worksheets/sight-words-cards.pdf")
