import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.utils import ImageReader

from app.models import TemplateConfig


WIDTH, HEIGHT = A4
L = 20 * mm
R = WIDTH - 20 * mm
CENTER = WIDTH / 2

PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")

SAMPLE_ROW = {
    "Name": "John Doe",
    "ExamNo": "RV/TE/UOE/AS/F/0001",
    "ExamDate": "2026-05-21",
    "ExamTime": "9:00 AM",
    "AssignedHall": "Hall 1",
    "Number": 1,
    "Email": "johndoe@example.com",
    "PhotoLink": "",
    "PhoneNumber": "08012345678",
}


def y(mm_from_top):
    return HEIGHT - mm_from_top * mm


def fill_placeholders(text, row):
    def replacer(match):
        key = match.group(1)
        val = row.get(key, match.group(0))
        return str(val)[:10] if key == "ExamDate" else str(val)
    return PLACEHOLDER_RE.sub(replacer, str(text))


def render_pdf(template: TemplateConfig, row: dict, output_path: str, photo_path: str = None):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=A4)

    theme = template.theme
    primary = colors.HexColor(theme.primary_color)
    secondary = colors.HexColor(theme.secondary_color)
    accent = colors.HexColor(theme.accent_color)
    text_color = colors.HexColor(theme.text_color)
    label_color = colors.HexColor(theme.label_color)

    # --- HEADER ---
    header = template.header

    # Logo
    logo_w = 16 * mm
    logo_h = 16 * mm
    logo_x = CENTER - logo_w / 2
    logo_y = y(20)

    logo_path = header.logo_path
    logo_drawn = False
    if logo_path and os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, logo_x, logo_y, width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
            logo_drawn = True
        except Exception:
            pass

    if not logo_drawn:
        c.setFillColor(accent)
        c.setStrokeColor(primary)
        c.setLineWidth(1)
        c.circle(CENTER, logo_y + logo_h / 2, logo_w / 2, fill=1, stroke=1)
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(CENTER, logo_y + logo_h / 2 - 2, "LOGO")

    # Number
    if header.show_number:
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(R, y(20), f"Number: {row.get('Number', '')}")

    # Company name
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(CENTER, y(25), header.company_name)

    # Address + contact
    c.setFillColor(text_color)
    c.setFont("Helvetica", 8.5)
    line_y = 30
    for line in header.address_lines + header.contact_lines:
        c.drawCentredString(CENTER, y(line_y), line)
        line_y += 4

    # Motto
    if header.motto:
        c.setFillColor(primary)
        c.setFont("Helvetica-BoldOblique", 9)
        c.drawCentredString(CENTER, y(line_y + 1), header.motto)

    # Divider
    divider_y = line_y + 4
    c.setStrokeColor(primary)
    c.setLineWidth(1.2)
    c.line(L, y(divider_y), R, y(divider_y))
    c.setStrokeColor(secondary)
    c.setLineWidth(0.4)
    c.line(L, y(divider_y + 1), R, y(divider_y + 1))

    # --- REFERENCE LINE ---
    ref = template.reference
    ref_y = divider_y + 7
    if ref.our_ref or ref.date:
        c.setFont("Helvetica", 8.5)
        c.setFillColor(text_color)
        if ref.our_ref:
            c.drawString(L, y(ref_y), f"Our Ref: {ref.our_ref}")
        c.drawCentredString(CENTER, y(ref_y), "Your Ref: ___________________")
        if ref.date:
            c.drawRightString(R, y(ref_y), f"Date: {ref.date}")

    # --- SUBJECT ---
    subject_y = ref_y + 9
    if template.subject:
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(CENTER, y(subject_y), template.subject)
        c.setStrokeColor(secondary)
        c.setLineWidth(1)
        c.line(L, y(subject_y) - 2 * mm, R, y(subject_y) - 2 * mm)

    # --- SALUTATION ---
    sal_y = subject_y + 10
    c.setFont("Helvetica", 10)
    c.setFillColor(text_color)
    c.drawString(L, y(sal_y), fill_placeholders(template.salutation, row))

    # --- PHOTO BOX ---
    photo_box_top = sal_y + 10
    if template.show_photo:
        bw = 33 * mm
        bh = 38 * mm
        bx = R - bw
        by = y(photo_box_top + 38)

        c.setFillColor(accent)
        c.setStrokeColor(colors.HexColor("#CCCCCC"))
        c.setLineWidth(0.8)
        c.rect(bx, by, bw, bh, fill=1, stroke=1)

        if photo_path and os.path.exists(photo_path):
            try:
                img = ImageReader(photo_path)
                c.drawImage(img, bx + 1.5 * mm, by + 1.5 * mm,
                            width=bw - 3 * mm, height=bh - 3 * mm,
                            preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        else:
            c.setStrokeColor(secondary)
            c.setDash(2, 3)
            c.setLineWidth(0.5)
            c.rect(bx + 1.5 * mm, by + 1.5 * mm, bw - 3 * mm, bh - 3 * mm, fill=0, stroke=1)
            c.setDash()
            c.setFillColor(label_color)
            c.setFont("Helvetica", 7)
            cx = bx + bw / 2
            c.drawCentredString(cx, by + bh / 2 + 3, "PASSPORT")
            c.drawCentredString(cx, by + bh / 2 - 6, "PHOTOGRAPH")

    # --- BODY PARAGRAPHS ---
    body_y = sal_y + 8
    text_width = WIDTH - 2 * 20 * mm
    if template.show_photo:
        text_width = text_width - 33 * mm - 5 * mm

    style = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=9.5,
        textColor=text_color, leading=14, alignment=TA_JUSTIFY
    )
    cur_y = y(body_y)
    for para_text in template.body_paragraphs:
        filled = fill_placeholders(para_text, row)
        p = Paragraph(filled, style)
        w, h = p.wrapOn(c, text_width, 80 * mm)
        cur_y -= h
        p.drawOn(c, L, cur_y)
        cur_y -= 4 * mm

    # --- DETAIL BOX ---
    detail_box = template.detail_box
    if detail_box:
        num_rows = len(detail_box.field_rows)
        bx = L
        bw = WIDTH - 2 * 20 * mm
        row_height = 13 * mm
        header_height = 9 * mm
        bh = header_height + (num_rows * row_height) + 2 * mm
        by = y(172)

        c.setFillColor(accent)
        c.setStrokeColor(primary)
        c.setLineWidth(1)
        c.rect(bx, by, bw, bh, fill=1, stroke=1)

        # Header strip
        c.setFillColor(primary)
        c.rect(bx, by + bh - header_height, bw, header_height, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(bx + 4 * mm, by + bh - 6 * mm, detail_box.title)

        col1 = bx + 4 * mm
        col2 = bx + bw / 2 + 4 * mm
        row_top = by + bh - header_height - 5 * mm

        for field_row in detail_box.field_rows:
            if len(field_row) == 1:
                field = field_row[0]
                c.setFont("Helvetica", 7.5)
                c.setFillColor(label_color)
                c.drawString(col1, row_top, field.label)
                c.setFont("Helvetica-Bold", 9.5)
                c.setFillColor(primary)
                c.drawString(col1, row_top - 5.5 * mm, fill_placeholders(field.value, row))
            elif len(field_row) >= 2:
                f1, f2 = field_row[0], field_row[1]
                c.setFont("Helvetica", 7.5)
                c.setFillColor(label_color)
                c.drawString(col1, row_top, f1.label)
                c.drawString(col2, row_top, f2.label)
                c.setFont("Helvetica-Bold", 9.5)
                c.setFillColor(primary)
                c.drawString(col1, row_top - 5.5 * mm, fill_placeholders(f1.value, row))
                c.drawString(col2, row_top - 5.5 * mm, fill_placeholders(f2.value, row))
            row_top -= row_height

    # --- NOTICE ---
    if template.notice:
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(label_color)
        c.drawString(L, y(176), fill_placeholders(template.notice, row))

    # --- INSTRUCTIONS ---
    if template.instructions and template.instructions.items:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(primary)
        c.drawString(L, y(184), template.instructions.heading)
        c.setStrokeColor(secondary)
        c.setLineWidth(0.6)
        c.line(L, y(184) - 1.5 * mm, R, y(184) - 1.5 * mm)

        bullet_style = ParagraphStyle(
            "bul", fontName="Helvetica", fontSize=9,
            textColor=text_color, leading=13
        )
        cur_y = y(189)
        for item in template.instructions.items:
            filled = fill_placeholders(item, row)
            p = Paragraph(f"• {filled}", bullet_style)
            w, h = p.wrapOn(c, R - L - 2 * mm, 20 * mm)
            cur_y -= h
            p.drawOn(c, L + 2 * mm, cur_y)
            cur_y -= 1.5 * mm

    # --- COMPLIANCE ---
    if template.compliance:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(primary)
        c.drawString(L, y(225), template.compliance.heading)
        c.setStrokeColor(secondary)
        c.setLineWidth(0.6)
        c.line(L, y(225) - 1.5 * mm, R, y(225) - 1.5 * mm)

        comp_style = ParagraphStyle(
            "comp", fontName="Helvetica", fontSize=9,
            textColor=text_color, leading=13, alignment=TA_JUSTIFY
        )
        filled = fill_placeholders(template.compliance.text, row)
        p = Paragraph(filled, comp_style)
        w, h = p.wrapOn(c, R - L, 30 * mm)
        p.drawOn(c, L, y(230) - h)

    # --- SIGNATURE ---
    sig = template.signature
    c.setFont("Helvetica", 9)
    c.setFillColor(text_color)
    c.drawString(L, y(254), "Thank you.")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(L, y(260), sig.closing)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(primary)
    c.drawString(L, y(268), sig.name)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(text_color)
    c.drawString(L, y(273), sig.title)

    # --- FOOTER ---
    footer = template.footer
    c.setFillColor(primary)
    c.rect(0, 0, WIDTH, 12 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(WIDTH / 2, 7 * mm, footer.text)
    if footer.credit:
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(WIDTH / 2, 3 * mm, footer.credit)

    c.save()
    return output_path


def render_preview(template: TemplateConfig, output_path: str):
    return render_pdf(template, SAMPLE_ROW, output_path)
