from allocator import allocate_combinations
import urllib
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY

WIDTH, HEIGHT = A4
L = 20 * mm
R = WIDTH - 20 * mm

DARK_BLUE  = colors.HexColor("#1B3A5C")
MID_BLUE   = colors.HexColor("#2E6DA4")
LIGHT_GREY = colors.HexColor("#F4F6F9")
RULE_COLOR = colors.HexColor("#CCCCCC")
TEXT_COLOR = colors.HexColor("#2C2C2C")
LABEL_COLOR = colors.HexColor("#777777")

# --- HELPERS ---
def y(mm_from_top):
    return HEIGHT - mm_from_top * mm

def draw_letterhead(c):
    c.setFillColor(DARK_BLUE)
    c.rect(0, y(28), WIDTH, 28 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(L, y(13), "OSALASI COMPANY LIMITED")
    c.setFont("Helvetica", 8)
    c.drawString(L, y(19), "Gwodo-Shiroro Dam Express Road, Sabon Gurusu, Niger State")
    c.drawString(L, y(24), "Tel: +234 803 451 3313  |  Email: osalasifarms.ng.ltd@gmail.com")
    c.setFont("Helvetica-Oblique", 8)
    c.drawRightString(R, y(18), "\"Hard Work Pays\"")

def draw_photo_box(c):
    bw = 33 * mm
    bh = 38 * mm
    bx = R - bw
    by = y(104)
    c.setFillColor(LIGHT_GREY)
    c.setStrokeColor(RULE_COLOR)
    c.setLineWidth(0.8)
    c.rect(bx, by, bw, bh, fill=1, stroke=1)
    c.setStrokeColor(MID_BLUE)
    c.setDash(2, 3)
    c.setLineWidth(0.5)
    c.rect(bx + 1.5 * mm, by + 1.5 * mm, bw - 3 * mm, bh - 3 * mm, fill=0, stroke=1)
    c.setDash()
    c.setFillColor(LABEL_COLOR)
    c.setFont("Helvetica", 7)
    cx = bx + bw / 2
    c.drawCentredString(cx, by + bh / 2 + 3, "PASSPORT")
    c.drawCentredString(cx, by + bh / 2 - 6, "PHOTOGRAPH")

def draw_ref_line(c):
    c.setFont("Helvetica", 8.5)
    c.setFillColor(TEXT_COLOR)
    c.drawString(L, y(36), "Our Ref: Osa/CBT/PA/01/2026")
    c.drawString(L + 80 * mm, y(36), "Date: April 14, 2026")

def draw_subject(c):
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(L, y(44), "SUBJECT: ALLOCATION OF COMPUTER-BASED TEST (CBT) EXAMINATION TIMETABLE")
    c.setStrokeColor(MID_BLUE)
    c.setLineWidth(1)
    c.line(L, y(44) - 2 * mm, R, y(44) - 2 * mm)

def draw_salutation(c, row):
    c.setFont("Helvetica", 10)
    c.setFillColor(TEXT_COLOR)
    c.drawString(L, y(54), f"Dear {row['Name']},")

def draw_body(c):
    body = (
        "Following your successful shortlisting in the ongoing recruitment exercise for the "
        "employment of teachers into primary and secondary schools in Rivers State, we are "
        "pleased to formally notify you of your Computer-Based Test (CBT) examination schedule."
    )
    style = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=9.5,
        textColor=TEXT_COLOR, leading=14, alignment=TA_JUSTIFY
    )
    text_width = WIDTH - 2 * 20 * mm - 33 * mm - 5 * mm
    p = Paragraph(body, style)
    w, h = p.wrapOn(c, text_width, 60 * mm)
    p.drawOn(c, L, y(66) - h)

def draw_exam_box(c, row):
    bx = L
    bw = WIDTH - 2 * 20 * mm
    bh = 40 * mm
    by = y(148)
    c.setFillColor(LIGHT_GREY)
    c.setStrokeColor(MID_BLUE)
    c.setLineWidth(1)
    c.rect(bx, by, bw, bh, fill=1, stroke=1)
    c.setFillColor(MID_BLUE)
    c.rect(bx, by + bh - 9 * mm, bw, 9 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(bx + 4 * mm, by + bh - 6 * mm, "EXAMINATION DETAILS")

    col1 = bx + 4 * mm
    col2 = bx + bw / 2 + 4 * mm

    fields = [
        ("EXAMINATION NUMBER", row["ExamNo"],    "TIME SLOT",     row["ExamTime"]),
        ("EXAMINATION DATE",   str(row["ExamDate"])[:10], "ASSIGNED HALL", row["AssignedHall"]),
    ]

    row_top = by + bh - 9 * mm - 5 * mm
    for label1, val1, label2, val2 in fields:
        c.setFont("Helvetica", 7.5)
        c.setFillColor(LABEL_COLOR)
        c.drawString(col1, row_top, label1)
        c.drawString(col2, row_top, label2)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(DARK_BLUE)
        c.drawString(col1, row_top - 5.5 * mm, val1)
        c.drawString(col2, row_top - 5.5 * mm, val2)
        row_top -= 14 * mm

def draw_notice(c):
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(LABEL_COLOR)
    c.drawString(L, y(152),
        "Please note that your examination number determines your specific date. You must strictly adhere to the assigned schedule.")

def draw_instructions(c):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK_BLUE)
    c.drawString(L, y(158), "Important Instructions")
    c.setStrokeColor(RULE_COLOR)
    c.setLineWidth(0.5)
    c.line(L, y(158) - 1.5 * mm, R, y(158) - 1.5 * mm)
    items = [
        "Candidates must report to the examination venue at least one (1) hour before the scheduled time.",
        "You are required to present a valid means of identification before entry into the examination hall.",
        "The use of mobile phones, smart devices, or any electronic gadgets is strictly prohibited during the examination.",
        "Any form of examination malpractice will result in immediate disqualification.",
    ]
    style = ParagraphStyle("bul", fontName="Helvetica", fontSize=9,
                           textColor=TEXT_COLOR, leading=13)
    cur_y = y(164)
    for item in items:
        p = Paragraph(f"• {item}", style)
        w, h = p.wrapOn(c, R - L, 20 * mm)
        cur_y -= h
        p.drawOn(c, L + 2 * mm, cur_y)
        cur_y -= 2 * mm

def draw_compliance(c):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK_BLUE)
    c.drawString(L, y(208), "Compliance Notice")
    c.setStrokeColor(RULE_COLOR)
    c.setLineWidth(0.5)
    c.line(L, y(208) - 1.5 * mm, R, y(208) - 1.5 * mm)
    text = (
        "Failure to appear on your assigned date, as indicated by your examination number, may lead to "
        "automatic forfeiture of your opportunity to proceed in the recruitment process. "
        "We wish you success as you proceed to this important stage of the selection process."
    )
    style = ParagraphStyle("body", fontName="Helvetica", fontSize=9,
                           textColor=TEXT_COLOR, leading=13, alignment=TA_JUSTIFY)
    p = Paragraph(text, style)
    w, h = p.wrapOn(c, R - L, 30 * mm)
    p.drawOn(c, L, y(214) - h)

def draw_signature(c):
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(L, y(238), "Yours faithfully,")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(L, y(250), "For: Osalasi Company Nigeria Limited")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(DARK_BLUE)
    c.drawString(L, y(258), "Prof. Yunusa Danlidi Hakimi")
    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT_COLOR)
    c.drawString(L, y(264), "Principal Consultant")

def draw_footer(c):
    c.setFillColor(DARK_BLUE)
    c.rect(0, 0, WIDTH, 10 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(
        WIDTH / 2, 3.5 * mm,
        "This document is system-generated and is unique to the candidate. "
        "Please bring a printed copy to the examination venue."
    )

def generate_pdf(row, output_folder):
    filename = f"{output_folder}/{row['ExamNo']}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    draw_letterhead(c)
    draw_photo_box(c)
    draw_ref_line(c)
    draw_subject(c)
    draw_salutation(c, row)
    draw_body(c)
    draw_exam_box(c, row)
    draw_notice(c)
    draw_instructions(c)
    draw_compliance(c)
    draw_signature(c)
    draw_footer(c)
    c.save()

if __name__ == "__main__":
    import pandas as pd
    data = pd.read_excel('./data/allocated_exam_schedule.xlsx')
    row = data.iloc[0]
    generate_pdf(row, './pdf')
    print(f"Generated PDF for {row['Name']}")