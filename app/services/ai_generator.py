import json
import anthropic

from app.models import TemplateConfig
from app import config


SYSTEM_PROMPT = """You are a PDF template designer for VolleyPacket, an exam invitation letter generator.

Given extracted text from a document, produce a JSON template config that will render a professional PDF letter.

The template schema has these sections:
- theme: {primary_color, secondary_color, accent_color, text_color, label_color} — hex colors
- header: {logo_path (null), company_name, address_lines[], contact_lines[], motto (optional), show_number (bool)}
- reference: {our_ref (optional), date (optional)}
- subject: the subject line string
- salutation: e.g. "Dear {Name}," — use {Name} placeholder for candidate name
- show_photo: boolean
- body_paragraphs: list of paragraph strings (HTML bold <b> tags allowed)
- detail_box: {title, field_rows: [[{label, value}]]} — value can use placeholders like {ExamNo}, {ExamDate}, {ExamTime}, {AssignedHall}. Rows with 2 fields display side-by-side, rows with 1 field span full width.
- notice: optional notice string
- instructions: {heading, items[]} — bullet point items (HTML <b> tags allowed)
- compliance: {heading, text} — closing compliance paragraph
- signature: {closing, name, title}
- footer: {text, credit (optional)}

Available candidate placeholders: {Name}, {ExamNo}, {ExamDate}, {ExamTime}, {AssignedHall}, {Number}, {Email}

Return ONLY valid JSON matching this schema. No markdown, no explanation."""


def generate_template_from_content(parsed_content: dict, instructions: str = None) -> TemplateConfig:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    user_message = f"Document content:\n\n{json.dumps(parsed_content, indent=2)}"
    if instructions:
        user_message += f"\n\nAdditional instructions from user:\n{instructions}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_json = response.content[0].text.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.split("\n", 1)[1].rsplit("```", 1)[0]

    template_data = json.loads(raw_json)
    return TemplateConfig(**template_data)
