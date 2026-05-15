import os
import re
from bs4 import BeautifulSoup


def parse_file(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".html" or ext == ".htm":
        raw_text = parse_html(file_path)
    elif ext == ".pdf":
        raw_text = parse_pdf(file_path)
    elif ext in (".doc", ".docx"):
        raw_text = parse_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    detected = detect_fields(raw_text)
    return {"raw_text": raw_text, "detected_fields": detected}


def parse_html(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator="\n", strip=True)


def parse_pdf(file_path: str) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def parse_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def detect_fields(text: str) -> dict:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    fields = {
        "subject": None,
        "body_paragraphs": [],
        "instructions": [],
        "company_name": None,
    }

    subject_patterns = [
        re.compile(r"(?:RE|SUBJECT|SUB)[:\s]*(.+)", re.IGNORECASE),
    ]

    instruction_mode = False

    for line in lines:
        # Subject detection
        for pat in subject_patterns:
            m = pat.match(line)
            if m:
                fields["subject"] = m.group(1).strip()
                continue

        # Instruction detection
        if re.match(r"(?:instructions?|guidelines?|rules?|note)[:\s]*$", line, re.IGNORECASE):
            instruction_mode = True
            continue

        if instruction_mode:
            cleaned = re.sub(r"^[\d\.\)\-•●\s]+", "", line).strip()
            if cleaned:
                fields["instructions"].append(cleaned)
            if not line.strip():
                instruction_mode = False
            continue

        # Company name heuristic: all-caps line with 2+ words, under 80 chars
        if line.isupper() and len(line.split()) >= 2 and len(line) < 80 and not fields["company_name"]:
            fields["company_name"] = line
            continue

        # Everything else is a body paragraph
        if len(line) > 20:
            fields["body_paragraphs"].append(line)

    return fields
