"""
Genere un cahier de vacances POFM en PDF (style beige/bleu minimaliste).
Usage: python generate_pdf.py [nb_jours] [utilisateur]
  nb_jours: nombre de jours (defaut 14)
  utilisateur: alia ou imran (defaut alia)
"""
import json
import sys
import random
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable,
)
from reportlab.platypus.flowables import Flowable
from pypdf import PdfReader, PdfWriter

# ── Config ──────────────────────────────────────────────────
NB_JOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 14
USER = sys.argv[2].lower() if len(sys.argv) > 2 else "alia"

if USER == "imran":
    DIFF_RANGE = (3, 5)
    PRENOM = "Imran"
    SOUS_TITRE = "Niveau Lycee"
else:
    PRENOM = "Alia"
    DIFF_RANGE = (1, 4)
    SOUS_TITRE = "Niveau College"

OBJECTIF_POINTS = 10

# ── Palette beige / bleu marine ─────────────────────────────
NAVY       = HexColor("#1B3A6B")   # bleu marine profond
NAVY_MED   = HexColor("#2E5090")   # bleu marine moyen
NAVY_LIGHT = HexColor("#4A7CC9")   # bleu clair
CREAM      = HexColor("#F5F0E8")   # fond creme
CREAM_DARK = HexColor("#E8E0D0")   # creme fonce (bordures)
WARM_WHITE = HexColor("#FDFBF7")   # blanc chaud (cartes)
BEIGE      = HexColor("#D4C9B8")   # beige moyen
BROWN_TEXT = HexColor("#5C4A3A")   # brun chaud (texte)
BROWN_LIGHT= HexColor("#8B7B6B")   # brun clair (texte secondaire)
TERRACOTTA = HexColor("#C47A5A")   # terre cuite (accents chauds)
SAGE       = HexColor("#7A9B7E")   # vert sauge
DUSTY_BLUE = HexColor("#8BACC4")   # bleu poussiereux

THEME_COLORS = {
    "calcul":       (NAVY,       HexColor("#E8EDF5")),
    "geometrie":    (SAGE,       HexColor("#EDF5EE")),
    "arithmetique": (TERRACOTTA, HexColor("#F5EDE8")),
    "combinatoire": (DUSTY_BLUE, HexColor("#E8F0F5")),
}


# ── Styles ──────────────────────────────────────────────────
def _s(name, **kw):
    return ParagraphStyle(name, **kw)

STYLES = {
    "cover_title": _s("cover_title", fontName="Helvetica-Bold", fontSize=30,
                       leading=36, textColor=white, alignment=TA_CENTER),
    "cover_sub": _s("cover_sub", fontName="Helvetica", fontSize=13,
                     leading=17, textColor=HexColor("#B8C8E0"), alignment=TA_CENTER),
    "cover_info": _s("cover_info", fontName="Helvetica", fontSize=10,
                      leading=14, textColor=HexColor("#D0C8B8"), alignment=TA_CENTER),
    "day_title": _s("day_title", fontName="Helvetica-Bold", fontSize=18,
                     leading=22, textColor=NAVY),
    "day_sub": _s("day_sub", fontName="Helvetica", fontSize=9,
                   leading=12, textColor=BROWN_LIGHT),
    "exo_text": _s("exo_text", fontName="Helvetica", fontSize=10.5,
                    leading=15, textColor=BROWN_TEXT, leftIndent=6),
    "answer_line": _s("answer_line", fontName="Helvetica-Oblique", fontSize=9,
                       leading=13, textColor=BEIGE, leftIndent=10),
    "corr_ans": _s("corr_ans", fontName="Helvetica-Bold", fontSize=10,
                    leading=14, textColor=SAGE, leftIndent=10),
    "corr_expl": _s("corr_expl", fontName="Helvetica", fontSize=9,
                     leading=13, textColor=BROWN_LIGHT, leftIndent=10),
    "eval_text": _s("eval_text", fontName="Helvetica", fontSize=9,
                     leading=14, textColor=BROWN_LIGHT),
}


# ── Custom Flowables ────────────────────────────────────────

class RoundedBox(Flowable):
    def __init__(self, width, content_flowables, bg_color=WARM_WHITE,
                 border_color=CREAM_DARK, border_width=0.5, radius=3*mm, padding=5*mm):
        super().__init__()
        self.box_width = width
        self.content = content_flowables
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.radius = radius
        self.padding = padding

    def wrap(self, availWidth, availHeight):
        w = self.box_width - 2 * self.padding
        h = 0
        for f in self.content:
            _, fh = f.wrap(w, availHeight)
            h += fh
        self.width = self.box_width
        self.height = h + 2 * self.padding
        return self.width, self.height

    def draw(self):
        c = self.canv
        w, h = self.box_width, self.height
        c.setFillColor(self.bg_color)
        c.setStrokeColor(self.border_color)
        c.setLineWidth(self.border_width)
        c.roundRect(0, 0, w, h, self.radius, fill=1, stroke=1)
        y = h - self.padding
        for f in self.content:
            fw, fh = f.wrap(w - 2 * self.padding, h)
            f.drawOn(c, self.padding, y - fh)
            y -= fh


class ThemeTag(Flowable):
    def __init__(self, theme, difficulty):
        super().__init__()
        self.theme = theme
        self.difficulty = difficulty
        self.fg, self.bg = THEME_COLORS.get(theme, (NAVY, HexColor("#E8EDF5")))
        self.width = 160 * mm
        self.height = 7 * mm

    def draw(self):
        c = self.canv
        label = self.theme.capitalize()
        pts = self.difficulty
        pts_label = f"{pts} pt{'s' if pts > 1 else ''}"

        # Pill
        c.setFillColor(self.bg)
        c.roundRect(0, 0, 22 * mm, self.height, 3 * mm, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(11 * mm, 2 * mm, label)

        # Dots
        r = 1.5 * mm
        for i in range(5):
            cx = 28 * mm + i * 4 * mm
            cy = self.height / 2
            c.setFillColor(self.fg if i < self.difficulty else CREAM_DARK)
            c.circle(cx, cy, r, fill=1, stroke=0)

        c.setFillColor(self.fg)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(50 * mm, 2 * mm, pts_label)


class SectionDivider(Flowable):
    def __init__(self, label, width):
        super().__init__()
        self.label = label
        self.total_width = width
        self.width = width
        self.height = 12 * mm

    def draw(self):
        c = self.canv
        w = self.total_width
        y = self.height / 2

        c.setStrokeColor(BEIGE)
        c.setLineWidth(0.5)
        c.line(0, y, w * 0.25, y)
        c.line(w * 0.75, y, w, y)

        tw = c.stringWidth(self.label, "Helvetica-Bold", 10)
        px = (w - tw) / 2 - 4 * mm
        pw = tw + 8 * mm
        c.setFillColor(NAVY)
        c.roundRect(px, y - 4 * mm, pw, 8 * mm, 4 * mm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(w / 2, y - 2.5 * mm, self.label)


# ── Exercise selection ──────────────────────────────────────

def select_daily_exercises(bank, diff_range, target_points=10):
    available = [e for e in bank if diff_range[0] <= e["difficulty"] <= diff_range[1]]
    random.shuffle(available)
    selected = []
    points = 0
    for e in available:
        if points >= target_points:
            break
        selected.append(e)
        points += e["difficulty"]
        bank.remove(e)
    selected.sort(key=lambda e: e["difficulty"])
    return selected, points


# ── Page backgrounds ────────────────────────────────────────

COVER_PDF = os.path.join(os.path.dirname(__file__) or ".",
    "Design sans titre.pdf")


def page_bg(canvas, doc):
    """Pages interieures : fond creme subtil."""
    canvas.saveState()
    w, h = A4

    # Fond creme
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    # Fine bande bleu marine en haut
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 2.5 * mm, w, 2.5 * mm, fill=1, stroke=0)


    # Footer
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(BROWN_LIGHT)
    canvas.drawCentredString(w / 2, 8 * mm,
                             f"Cahier POFM de {PRENOM}  -  Page {doc.page}")

    # Fine ligne au-dessus du footer
    canvas.setStrokeColor(CREAM_DARK)
    canvas.setLineWidth(0.3)
    canvas.line(30 * mm, 13 * mm, w - 30 * mm, 13 * mm)

    canvas.restoreState()


# ── Build exercise flowable ─────────────────────────────────

def make_exercise_block(num, ex):
    """Bloc exercice (enonce + ligne de reponse)."""
    elements = []
    elements.append(ThemeTag(ex["theme"], ex["difficulty"]))
    elements.append(Spacer(1, 1.5 * mm))

    q = ex["question"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    navy_hex = "#1B3A6B"
    elements.append(Paragraph(
        f'<font name="Helvetica-Bold" color="{navy_hex}">{num}.</font>  {q}',
        STYLES["exo_text"]
    ))
    elements.append(Spacer(1, 1.5 * mm))
    elements.append(Paragraph("Reponse : ____________________", STYLES["answer_line"]))

    content_width = A4[0] - 30 * mm
    card = RoundedBox(content_width, elements, bg_color=WARM_WHITE,
                      border_color=CREAM_DARK, padding=4 * mm)
    return KeepTogether([card, Spacer(1, 2 * mm)])


def make_correction_block(num, ex):
    """Bloc correction (numero + reponse + explication detaillee, sans enonce)."""
    elements = []

    # En-tete : numero + theme + reponse
    ans = str(ex["answer"])
    theme = ex["theme"].capitalize()
    diff = ex["difficulty"]
    elements.append(Paragraph(
        f'<font name="Helvetica-Bold" color="#1B3A6B" size="11">'
        f'Exercice {num}</font>'
        f'  <font color="#8B7B6B" size="8">({theme} - difficulte {diff})</font>',
        STYLES["exo_text"]
    ))
    elements.append(Spacer(1, 2 * mm))

    # Reponse mise en valeur
    elements.append(Paragraph(
        f'<font name="Helvetica-Bold" color="#7A9B7E" size="11">'
        f'Reponse : {ans}</font>',
        _s("corr_ans_big", fontName="Helvetica-Bold", fontSize=11,
           leading=14, textColor=SAGE, leftIndent=6)
    ))
    elements.append(Spacer(1, 2 * mm))

    # Explication detaillee
    expl = ex["explanation"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    elements.append(Paragraph(
        f'<b>Explication :</b>  {expl}',
        _s("corr_detail", fontName="Helvetica", fontSize=9.5,
           leading=13, textColor=BROWN_TEXT, leftIndent=6)
    ))

    content_width = A4[0] - 30 * mm
    card = RoundedBox(content_width, elements, bg_color=WARM_WHITE,
                      border_color=CREAM_DARK, padding=4 * mm)
    return KeepTogether([card, Spacer(1, 2.5 * mm)])


# ── Main ────────────────────────────────────────────────────

def generate_booklet():
    with open("exercises_bank.json", "r", encoding="utf-8") as f:
        bank = json.load(f)

    random.seed(2026)
    random.shuffle(bank)

    filename = f"pofm_vacances_{USER}_{NB_JOURS}j.pdf"

    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=12 * mm, bottomMargin=15 * mm,
    )

    story = []
    content_width = A4[0] - 30 * mm

    # ───── EXERCICES PAR JOUR ─────
    all_days = []
    global_num = 0

    for day in range(1, NB_JOURS + 1):
        exercises, points = select_daily_exercises(bank, DIFF_RANGE, OBJECTIF_POINTS)
        if not exercises:
            print(f"Jour {day}: plus assez d'exercices")
            break
        all_days.append((day, exercises, points))

        story.append(Paragraph(f"Jour {day}", STYLES["day_title"]))
        story.append(Spacer(1, 1 * mm))
        story.append(Paragraph(
            f"{len(exercises)} exercices  |  {points} points possibles  |  Objectif : {OBJECTIF_POINTS} pts",
            STYLES["day_sub"]
        ))
        story.append(Spacer(1, 1 * mm))
        story.append(HRFlowable(width="100%", thickness=0.4, color=BEIGE, spaceAfter=4 * mm))

        for ex in exercises:
            global_num += 1
            ex["global_num"] = global_num
            story.append(make_exercise_block(global_num, ex))

        # Auto-evaluation
        eval_content = [
            Paragraph("<b>Auto-evaluation du jour</b>", _s(
                "ev_t", fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=NAVY
            )),
            Spacer(1, 2 * mm),
            Paragraph(f"Points gagnes : _______ / {points}", STYLES["eval_text"]),
            Spacer(1, 1 * mm),
            Paragraph("Exercices a revoir : " + "_" * 50, STYLES["eval_text"]),
            Spacer(1, 1 * mm),
            Paragraph("Ce que j'ai appris : " + "_" * 50, STYLES["eval_text"]),
        ]
        eval_box = RoundedBox(content_width, eval_content,
                              bg_color=HexColor("#EDE8DF"), border_color=BEIGE, padding=4 * mm)
        story.append(Spacer(1, 3 * mm))
        story.append(eval_box)
        story.append(PageBreak())

    # ───── TABLEAU DE SUIVI ─────
    story.append(SectionDivider("Suivi des points", content_width))
    story.append(Spacer(1, 6 * mm))

    th_s = _s("th2", fontName="Helvetica-Bold", fontSize=8, leading=10,
              textColor=white, alignment=TA_CENTER)
    tc_s = _s("tc2", fontName="Helvetica", fontSize=8, leading=11,
              textColor=BROWN_TEXT, alignment=TA_CENTER)
    col_widths = [18 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm, 54 * mm]

    table_data = [[
        Paragraph("Jour", th_s), Paragraph("Pts possibles", th_s),
        Paragraph("Pts gagnes", th_s), Paragraph("Cumul", th_s),
        Paragraph("Objectif", th_s), Paragraph("Notes / a revoir", th_s),
    ]]
    cumul_obj = 0
    for day, exercises, points in all_days:
        cumul_obj += OBJECTIF_POINTS
        table_data.append([
            Paragraph(f"<b>{day}</b>", tc_s), Paragraph(str(points), tc_s),
            Paragraph("", tc_s), Paragraph("", tc_s),
            Paragraph(str(cumul_obj), tc_s), Paragraph("", tc_s),
        ])

    tt = Table(table_data, colWidths=col_widths, repeatRows=1)
    tt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WARM_WHITE, CREAM]),
        ("GRID", (0, 0), (-1, -1), 0.4, CREAM_DARK),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tt)
    story.append(PageBreak())

    # ───── EXERCICES BONUS (faciles, sans correction) ─────
    story.append(SectionDivider("Exercices bonus", content_width))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "Des exercices faciles pour gagner des points si tu bloques sur un jour !",
        _s("bonus_intro", fontName="Helvetica-Oblique", fontSize=9,
           leading=13, textColor=BROWN_LIGHT, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 4 * mm))

    # Generer des exos bonus faciles (diff 1-2)
    bonus_bank = [e for e in bank if e["difficulty"] <= 2]
    random.shuffle(bonus_bank)
    bonus_num = global_num
    bonus_count = 0
    # Remplir ~2 pages (~12-15 exos faciles)
    for ex in bonus_bank[:12]:
        bonus_num += 1
        bonus_count += 1
        story.append(make_exercise_block(bonus_num, ex))

    if bonus_count > 0:
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(
            f"<i>{bonus_count} exercices bonus  |  1 pt chacun</i>",
            _s("bonus_footer", fontName="Helvetica-Oblique", fontSize=8,
               leading=11, textColor=BROWN_LIGHT, alignment=TA_CENTER)
        ))

    story.append(PageBreak())

    # ───── CORRIGES ─────
    story.append(SectionDivider("Corriges detailles", content_width))
    story.append(Spacer(1, 6 * mm))

    for day, exercises, points in all_days:
        story.append(Paragraph(
            f'<font color="#1B3A6B"><b>Jour {day}</b></font>',
            _s("cd", fontName="Helvetica-Bold", fontSize=13,
               leading=16, textColor=NAVY, spaceBefore=4 * mm)
        ))
        story.append(HRFlowable(width="40%", thickness=0.4, color=BEIGE, spaceAfter=3 * mm))
        for ex in exercises:
            story.append(make_correction_block(ex["global_num"], ex))

    # ───── CORRIGES BONUS (juste les reponses) ─────
    if bonus_count > 0:
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph(
            '<font color="#1B3A6B"><b>Exercices bonus</b></font>',
            _s("cd_bonus", fontName="Helvetica-Bold", fontSize=13,
               leading=16, textColor=NAVY, spaceBefore=4 * mm)
        ))
        story.append(HRFlowable(width="40%", thickness=0.4, color=BEIGE, spaceAfter=3 * mm))
        # Liste compacte : numero = reponse
        answers_text = "   |   ".join(
            f"<b>{global_num + i + 1}</b> = {bonus_bank[i]['answer']}"
            for i in range(bonus_count)
        )
        story.append(Paragraph(answers_text, _s("bonus_ans", fontName="Helvetica",
            fontSize=9.5, leading=16, textColor=BROWN_TEXT)))

    # ───── PAGES NOTES ─────
    for i in range(2):
        story.append(PageBreak())
        story.append(Paragraph(
            f"Notes",
            _s(f"notes_t{i}", fontName="Helvetica-Bold", fontSize=14,
               leading=18, textColor=NAVY)
        ))
        story.append(HRFlowable(width="100%", thickness=0.4, color=BEIGE, spaceAfter=6 * mm))
        # Lignes pointillees
        for _ in range(28):
            story.append(Paragraph(
                ". " * 80,
                _s(f"dotline{i}", fontName="Helvetica", fontSize=8,
                   leading=18, textColor=CREAM_DARK)
            ))

    # ───── BUILD ─────
    # Generate content pages (without cover)
    content_file = filename.replace(".pdf", "_content.pdf")
    doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)

    # Merge: Canva cover (page 1) + generated content
    writer = PdfWriter()

    if os.path.exists(COVER_PDF):
        cover_reader = PdfReader(COVER_PDF)
        writer.add_page(cover_reader.pages[0])
        print(f"Couverture ajoutee depuis : {os.path.basename(COVER_PDF)}")
    else:
        print(f"ATTENTION: couverture introuvable ({COVER_PDF}), PDF sans couverture")

    content_reader = PdfReader(filename)
    for page in content_reader.pages:
        writer.add_page(page)

    with open(filename, "wb") as f:
        writer.write(f)

    # Clean up temp file
    if os.path.exists(content_file):
        os.remove(content_file)

    print(f"PDF genere : {filename}")
    print(f"  {NB_JOURS} jours, {global_num} exercices, difficulte {DIFF_RANGE[0]}-{DIFF_RANGE[1]}")


if __name__ == "__main__":
    generate_booklet()
