"""
step3_pdf_builder.py — 3. rīks: apvieno visus vizuāļus un aprakstus vienā PDF.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    PageBreak, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config import PDF_OUTPUT

os.makedirs(os.path.dirname(PDF_OUTPUT), exist_ok=True)

# ─── Reģistrē Unicode fontus ──────────────────────────────────────────────────

def _register_fonts():
    """Meklē un reģistrē Unicode fontu ar latviešu atbalstu."""
    candidates = [
        # Windows
        ("C:/Windows/Fonts/arial.ttf",        "C:/Windows/Fonts/arialbd.ttf"),
        ("C:/Windows/Fonts/calibri.ttf",      "C:/Windows/Fonts/calibrib.ttf"),
        ("C:/Windows/Fonts/tahoma.ttf",       "C:/Windows/Fonts/tahomabd.ttf"),
        ("C:/Windows/Fonts/verdana.ttf",      "C:/Windows/Fonts/verdanab.ttf"),
        # Linux
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ]
    for regular, bold in candidates:
        if os.path.exists(regular):
            pdfmetrics.registerFont(TTFont("UniFont", regular))
            if os.path.exists(bold):
                pdfmetrics.registerFont(TTFont("UniFont-Bold", bold))
            else:
                pdfmetrics.registerFont(TTFont("UniFont-Bold", regular))
            print(f"  ✅ Fonts reģistrēts: {regular}")
            return "UniFont", "UniFont-Bold"
    print("  ⚠️  Unicode fonts nav atrasts, izmanto Helvetica")
    return "Helvetica", "Helvetica-Bold"

FONT_NORMAL, FONT_BOLD = _register_fonts()

# ─── Krāsas ───────────────────────────────────────────────────────────────────

BRAND_BLUE  = colors.HexColor("#1a5f9e")
BRAND_LIGHT = colors.HexColor("#e8f1fb")
BRAND_GRAY  = colors.HexColor("#555555")
BRAND_DARK  = colors.HexColor("#1a1a2e")

# ─── Stili ────────────────────────────────────────────────────────────────────

def _build_styles():
    base = getSampleStyleSheet()
    s = {}
    def ps(name, **kw):
        kw.setdefault("fontName", FONT_NORMAL)
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    s["cover_title"] = ps("cover_title", fontName=FONT_BOLD, fontSize=28,
        textColor=BRAND_BLUE, spaceAfter=10, alignment=TA_CENTER, leading=34)
    s["cover_sub"] = ps("cover_sub", fontSize=13, textColor=BRAND_GRAY,
        alignment=TA_CENTER, spaceAfter=6)
    s["section_num"] = ps("section_num", fontSize=11, textColor=colors.white,
        alignment=TA_CENTER, leading=14)
    s["section_title"] = ps("section_title", fontName=FONT_BOLD, fontSize=16,
        textColor=BRAND_BLUE, spaceBefore=6, spaceAfter=4, leading=20)
    s["desc"] = ps("desc", fontSize=10, textColor=BRAND_GRAY,
        spaceAfter=8, leading=14, alignment=TA_JUSTIFY)
    s["insight_title"] = ps("insight_title", fontName=FONT_BOLD, fontSize=11,
        textColor=BRAND_BLUE, spaceBefore=8, spaceAfter=4)
    s["insight_body"] = ps("insight_body", fontSize=10, textColor=BRAND_DARK,
        leading=15, spaceAfter=6, alignment=TA_JUSTIFY)
    s["sql_label"] = ps("sql_label", fontName=FONT_BOLD, fontSize=9,
        textColor=BRAND_GRAY, spaceBefore=4)
    s["sql_code"] = ps("sql_code", fontName="Courier", fontSize=8,
        textColor=BRAND_DARK, backColor=colors.HexColor("#f4f4f4"),
        leftIndent=8, rightIndent=8, spaceAfter=6, leading=12)
    s["toc_item"] = ps("toc_item", fontSize=11, textColor=BRAND_DARK,
        spaceAfter=5, leading=16)
    s["error"] = ps("error", fontSize=10, textColor=colors.red, spaceAfter=6)
    return s

# ─── Lappušu numuri ───────────────────────────────────────────────────────────

def _on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_NORMAL, 8)
    canvas.setFillColor(BRAND_GRAY)
    w, _ = A4
    canvas.drawCentredString(w / 2, 1.2 * cm, str(doc.page))
    canvas.restoreState()

# ─── PDF celtniecība ──────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    """Notīra markdown ** un * no teksta."""
    return text.replace("**", "").replace("*", "") if text else ""

def build_pdf(results: list, database: str):
    doc = SimpleDocTemplate(
        PDF_OUTPUT, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )
    styles = _build_styles()
    story = []
    W = A4[0] - 4.4*cm

    # ── Titullapa ──
    story.append(Spacer(1, 2.5*cm))
    story.append(Paragraph("Datu Analizes Atskaite", styles["cover_title"]))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width=W, thickness=2, color=BRAND_BLUE, spaceAfter=12))
    story.append(Paragraph(f"Datubaze: {database}", styles["cover_sub"]))
    story.append(Paragraph(
        f"Generets: {datetime.now().strftime('%Y. gada %d. %B, %H:%M')}",
        styles["cover_sub"]))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"Si atskaite satur {len(results)} datu vizualizacijas, "
        "kas automatiski generetas izmantojot LLM (Claude) un Python.",
        styles["desc"]))
    story.append(PageBreak())

    # ── Satura rādītājs ──
    story.append(Paragraph("Satura raditajs", styles["section_title"]))
    story.append(HRFlowable(width=W, thickness=1, color=BRAND_LIGHT, spaceAfter=8))
    for i, res in enumerate(results, 1):
        status = "OK" if not res.get("error") else "KLUDА"
        story.append(Paragraph(f"{status}  {i}.  {_clean(res['name'])}", styles["toc_item"]))
    story.append(PageBreak())

    # ── Katrs vizuālis ──
    for i, res in enumerate(results, 1):
        header_data = [[
            Paragraph(str(i), styles["section_num"]),
            Paragraph(_clean(res["name"]), styles["section_title"]),
        ]]
        header_table = Table(header_data, colWidths=[1.2*cm, W-1.2*cm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), BRAND_BLUE),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(_clean(res["description"]), styles["desc"]))

        if res.get("error"):
            story.append(Paragraph(f"Kludа: {res['error']}", styles["error"]))
        elif res.get("chart_path") and os.path.exists(res["chart_path"]):
            img = Image(res["chart_path"])
            img.drawWidth = W
            img.drawHeight = W * 0.58
            story.append(img)
            story.append(Spacer(1, 0.3*cm))

        if res.get("insight"):
            story.append(Paragraph("Datu ieskati", styles["insight_title"]))
            story.append(Paragraph(_clean(res["insight"]), styles["insight_body"]))

        if res.get("sql"):
            story.append(Paragraph("SQL vaicajums:", styles["sql_label"]))
            sql_display = res["sql"][:500] + ("..." if len(res["sql"]) > 500 else "")
            story.append(Paragraph(sql_display.replace("\n", "<br/>"), styles["sql_code"]))

        story.append(HRFlowable(width=W, thickness=0.5, color=BRAND_LIGHT, spaceAfter=6))
        story.append(PageBreak())

    # ── Beigu lapa ──
    story.append(Spacer(1, 4*cm))
    story.append(HRFlowable(width=W, thickness=2, color=BRAND_BLUE, spaceAfter=16))
    story.append(Paragraph("Atskaite pabeigta", styles["cover_title"]))
    story.append(Paragraph(
        "Generets automatiski ar Python + OpenRouter + Claude API",
        styles["cover_sub"]))

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    print(f"\n PDF saglabats: {PDF_OUTPUT}")
    return PDF_OUTPUT
