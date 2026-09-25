#!/usr/bin/env python3
"""生成趣学岛示例可打印教具 PDF（纯数字/图形，无需中文字体）。"""
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

W, H = A4
ORANGE = HexColor("#f59e0b")
TEAL = HexColor("#0d9488")
INK = HexColor("#22303c")
LIGHT = HexColor("#fff7e8")


def header(c: Canvas, title: str, subtitle: str):
    c.setFillColor(LIGHT)
    c.rect(0, H - 42 * mm, W, 42 * mm, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(18 * mm, H - 22 * mm, title)
    c.setFillColor(INK)
    c.setFont("Helvetica", 11)
    c.drawString(18 * mm, H - 31 * mm, subtitle)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(W - 18 * mm, H - 22 * mm, "FunLearn Island")


def footer(c: Canvas, page: int):
    c.setFillColor(HexColor("#9aa7b2"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, 12 * mm, f"FunLearn Island · free sample worksheet · page {page}")


def addition_pdf(path: str):
    c = Canvas(path, pagesize=A4)
    random.seed(7)
    problems = []
    while len(problems) < 40:
        a, b = random.randint(0, 9), random.randint(0, 9)
        if a + b <= 10 and (a, b) not in problems:
            problems.append((a, b))
    header(c, "Addition Practice", "Numbers to 10  ·  write the answer in the box  ·  name: ______________   date: __________")
    cols, rows = 4, 5
    x0, y0 = 20 * mm, H - 62 * mm
    dx, dy = 42 * mm, 38 * mm
    idx = 0
    for page in range(2):
        if page:
            c.showPage()
            header(c, "Addition Practice", "Numbers to 10  ·  keep going, you are doing great!")
            footer(c, page + 1)
            x0, y0 = 20 * mm, H - 62 * mm
        else:
            footer(c, 1)
        for r in range(rows):
            for col in range(cols):
                if idx >= len(problems):
                    break
                a, b = problems[idx]
                idx += 1
                x, y = x0 + col * dx, y0 - r * dy
                c.setStrokeColor(HexColor("#e8dcc8"))
                c.setFillColor(white)
                c.roundRect(x, y - 24 * mm, 36 * mm, 26 * mm, 3 * mm, stroke=1, fill=1)
                c.setFillColor(INK)
                c.setFont("Helvetica-Bold", 20)
                c.drawCentredString(x + 18 * mm, y - 12 * mm, f"{a} + {b} =")
                c.setStrokeColor(TEAL)
                c.setLineWidth(1.2)
                c.rect(x + 24 * mm, y - 16 * mm, 9 * mm, 9 * mm, stroke=1, fill=0)
    c.save()


def counting_pdf(path: str):
    c = Canvas(path, pagesize=A4)
    random.seed(21)
    header(c, "Count & Color", "Count the shapes, write the number, then color them!  ·  name: ______________")
    footer(c, 1)
    y = H - 70 * mm
    for row in range(6):
        n = random.randint(2, 8)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(20 * mm, y + 6 * mm, f"{row + 1}.")
        # draw n shapes
        sx = 34 * mm
        color = [ORANGE, TEAL, HexColor("#7c3aed")][row % 3]
        for i in range(n):
            c.setStrokeColor(color)
            c.setLineWidth(1.4)
            if row % 2 == 0:
                c.circle(sx + i * 13 * mm, y, 5 * mm, stroke=1, fill=0)
            else:
                c.rect(sx + i * 13 * mm - 4.5 * mm, y - 4.5 * mm, 9 * mm, 9 * mm, stroke=1, fill=0)
        # answer box
        bx = W - 52 * mm
        c.setFillColor(HexColor("#6b7a89"))
        c.setFont("Helvetica", 11)
        c.drawString(bx, y + 6 * mm, "There are")
        c.setStrokeColor(TEAL)
        c.setLineWidth(1.2)
        c.rect(bx + 22 * mm, y - 2 * mm, 10 * mm, 10 * mm, stroke=1, fill=0)
        c.setFillColor(HexColor("#6b7a89"))
        c.setFont("Helvetica", 11)
        c.drawString(bx + 34 * mm, y + 6 * mm, "in total.")
        y -= 30 * mm
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(W / 2, y - 6 * mm, "Great job! Show it to mom or dad. :)" )
    c.save()


if __name__ == "__main__":
    import os
    os.makedirs("/tmp/worksheets", exist_ok=True)
    addition_pdf("/tmp/worksheets/addition-to-10.pdf")
    counting_pdf("/tmp/worksheets/counting-coloring.pdf")
    print("pdfs written")
