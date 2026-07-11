"""Render a Dataset + narrative into a Jett-branded PDF (bytes).

SYNOPSIS SEAM: the section order below (header band, at-a-glance table,
narrative, highlights, disclaimer footer) approximates the jAIme study
synopsis layout. When mining pemf_bot_v2, match its real synopsis
structure here — this module is the only place layout lives.
"""
from __future__ import annotations

import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

import config
from marketer import branding
from marketer.stats import Dataset

_STYLES = {
    "wordmark": ParagraphStyle(
        "wordmark", fontName=branding.FONT_BOLD, fontSize=16,
        textColor=colors.white, leading=20,
    ),
    "title": ParagraphStyle(
        "title", fontName=branding.FONT_BOLD, fontSize=20,
        textColor=colors.HexColor(branding.NAVY), spaceAfter=2, leading=24,
    ),
    "period": ParagraphStyle(
        "period", fontName=branding.FONT_BODY, fontSize=11,
        textColor=colors.HexColor(branding.TEAL), spaceAfter=14,
    ),
    "h2": ParagraphStyle(
        "h2", fontName=branding.FONT_BOLD, fontSize=12,
        textColor=colors.HexColor(branding.NAVY), spaceBefore=14, spaceAfter=6,
    ),
    "body": ParagraphStyle(
        "body", fontName=branding.FONT_BODY, fontSize=10.5,
        textColor=colors.HexColor(branding.SLATE), leading=15, spaceAfter=6,
    ),
    "disclaimer": ParagraphStyle(
        "disclaimer", fontName=branding.FONT_BODY, fontSize=7.5,
        textColor=colors.HexColor(branding.SLATE), leading=10,
    ),
}


def _header_band(width: float):
    if config.LOGO_PATH.is_file():
        mark = Image(str(config.LOGO_PATH), width=1.4 * inch, height=0.45 * inch)
    else:
        mark = Paragraph(branding.WORDMARK, _STYLES["wordmark"])
    band = Table([[mark]], colWidths=[width], rowHeights=[0.6 * inch])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(branding.NAVY)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ]))
    return band


def _metrics_table(ds: Dataset, width: float):
    rows = [["Metric", "Value", "Basis"]]
    for m in ds.metrics:
        value = f"{m['value']}{m.get('unit', '')}"
        basis = f"n={m['n']}" if m.get("n") is not None else "—"
        rows.append([m["label"], value, basis])
    table = Table(rows, colWidths=[width * 0.56, width * 0.22, width * 0.22])
    style = [
        ("FONTNAME", (0, 0), (-1, 0), branding.FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), branding.FONT_BODY),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor(branding.SLATE)),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(branding.TEAL)),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor(branding.TEAL)),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(2, len(rows), 2):
        style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(branding.LIGHT)))
    table.setStyle(TableStyle(style))
    return table


def render_pdf(ds: Dataset, narrative: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=ds.title, author=branding.WORDMARK,
    )
    width = doc.width

    story = [
        _header_band(width),
        Spacer(1, 18),
        Paragraph(ds.title, _STYLES["title"]),
        Paragraph(ds.period, _STYLES["period"]),
        Paragraph("At a glance", _STYLES["h2"]),
        _metrics_table(ds, width),
        Paragraph("What the numbers say", _STYLES["h2"]),
    ]
    for para in narrative.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), _STYLES["body"]))

    if ds.highlights:
        story.append(Paragraph("Highlights", _STYLES["h2"]))
        for h in ds.highlights:
            story.append(Paragraph(f"•  {h}", _STYLES["body"]))

    story += [
        Spacer(1, 22),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor(branding.TEAL)),
        Spacer(1, 6),
        Paragraph(
            f"{branding.DISCLAIMER} Source: {ds.source}. "
            f"Generated {date.today().isoformat()}.",
            _STYLES["disclaimer"],
        ),
    ]
    doc.build(story)
    return buf.getvalue()
