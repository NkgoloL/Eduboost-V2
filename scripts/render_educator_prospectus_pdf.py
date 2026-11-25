#!/usr/bin/env python3
"""Render the educator prospectus Markdown into a paginated PDF."""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/educator_prospectus.md"
DEFAULT_OUTPUT = ROOT / "output/pdf/eduboost_educator_prospectus_2026-11-23.pdf"
BLUE = colors.HexColor("#154c79")
PALE_BLUE = colors.HexColor("#eaf3fa")
INK = colors.HexColor("#1c2935")
MUTED = colors.HexColor("#536574")


def inline(text: str) -> str:
    links: list[str] = []
    def link(match):
        label, url = match.group(1), match.group(2)
        links.append(f'<link href="{html.escape(url, quote=True)}" color="#176b9b">{html.escape(label)}</link>')
        return f"@@LINK{len(links)-1}@@"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = text.replace("—", " - ").replace("–", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    for index, value in enumerate(links):
        text = text.replace(f"@@LINK{index}@@", value)
    return text


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("EBTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=BLUE, alignment=TA_LEFT, spaceAfter=8),
        "subtitle": ParagraphStyle("EBSubtitle", parent=base["Normal"], fontSize=10, leading=14, textColor=MUTED, spaceAfter=18),
        "h2": ParagraphStyle("EBH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=BLUE, spaceBefore=16, spaceAfter=8, keepWithNext=True),
        "h3": ParagraphStyle("EBH3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK, spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("EBBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.3, textColor=INK, spaceAfter=7),
        "quote": ParagraphStyle("EBQuote", parent=base["BodyText"], fontName="Helvetica", fontSize=9.4, leading=14, textColor=BLUE, leftIndent=9, rightIndent=7, spaceBefore=6, spaceAfter=11),
        "bullet": ParagraphStyle("EBBullet", parent=base["BodyText"], fontName="Helvetica", fontSize=9, leading=12.5, textColor=INK, spaceAfter=3),
        "table": ParagraphStyle("EBTable", parent=base["BodyText"], fontName="Helvetica", fontSize=7.6, leading=10, textColor=INK),
        "table_head": ParagraphStyle("EBTableHead", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.7, leading=10, textColor=colors.white),
    }


def parse_markdown(text: str, styles):
    lines = text.splitlines()
    story = []
    i = 0
    first_heading = True
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                i += 1
                if row and all(re.fullmatch(r"[-: ]+", cell or "-") for cell in row):
                    continue
                rows.append(row)
            data = []
            for ri, row in enumerate(rows):
                style = styles["table_head"] if ri == 0 else styles["table"]
                data.append([Paragraph(inline(cell), style) for cell in row])
            if data:
                widths = [None] * len(data[0])
                table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#c5d2dc")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_BLUE]),
                ]))
                story.extend([Spacer(1, 4), table, Spacer(1, 8)])
            continue
        if line.startswith("# "):
            title = line[2:]
            story.append(Paragraph(inline(title), styles["title"]))
            story.append(HRFlowable(width="100%", thickness=1.2, color=BLUE, spaceAfter=9))
            first_heading = False
            i += 1
            continue
        if line.startswith("## What is implemented, and what is not established?"):
            story.append(PageBreak())
            story.append(Paragraph(inline(line[3:]), styles["h2"]))
            i += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["h2"]))
            i += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), styles["h3"]))
            i += 1
            continue
        if line.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            quote = Table([[Paragraph("<b>" + inline(" ".join(quote_lines)) + "</b>", styles["quote"])]], colWidths=[170 * mm])
            quote.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bed6e7")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
            story.extend([quote, Spacer(1, 7)])
            continue
        if re.match(r"^\d+\.\s", line) or line.startswith("- "):
            ordered = bool(re.match(r"^\d+\.\s", line))
            items = []
            while i < len(lines):
                candidate = lines[i].strip()
                match = re.match(r"^(?:\d+\.\s|- )(.*)$", candidate)
                if not match:
                    break
                items.append(ListItem(Paragraph(inline(match.group(1)), styles["bullet"]), leftIndent=8))
                i += 1
            story.append(ListFlowable(items, bulletType="1" if ordered else "bullet", start="1", leftIndent=18, bulletFontName="Helvetica", bulletFontSize=8, bulletColor=BLUE, spaceAfter=6))
            continue
        paragraph_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(("#", ">", "|", "- ")) and not re.match(r"^\d+\.\s", lines[i].strip()):
            paragraph_lines.append(lines[i].strip())
            i += 1
        story.append(Paragraph(inline(" ".join(paragraph_lines)), styles["body"]))
    return story


def page_chrome(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#d5dfe7"))
        canvas.setLineWidth(0.5)
        canvas.line(20 * mm, h - 14 * mm, w - 20 * mm, h - 14 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(20 * mm, h - 11 * mm, "EDUBOOST  |  EDUCATOR DISCUSSION COPY")
    canvas.setStrokeColor(colors.HexColor("#d5dfe7"))
    canvas.line(20 * mm, 14 * mm, w - 20 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 9.5 * mm, "Discussion only - no learner recruitment or learner-data access is in place")
    canvas.drawRightString(w - 20 * mm, 9.5 * mm, str(doc.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    story = parse_markdown(SOURCE.read_text(encoding="utf-8"), styles)
    doc = SimpleDocTemplate(
        str(args.output),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=21 * mm,
        bottomMargin=20 * mm,
        title="EduBoost: An Educator Prospectus",
        author="EduBoost",
    )
    doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    print(args.output)


if __name__ == "__main__":
    main()
