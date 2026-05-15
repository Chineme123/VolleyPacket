import os
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models import TemplateConfig, SaveTemplateRequest
from app.services.template_renderer import render_preview
from app import config

router = APIRouter()


def _load_template(template_id: str) -> TemplateConfig:
    path = os.path.join(config.TEMPLATE_FOLDER, f"{template_id}.json")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    with open(path, "r") as f:
        return TemplateConfig(**json.load(f))


def _list_template_files() -> list[dict]:
    templates = []
    if not os.path.isdir(config.TEMPLATE_FOLDER):
        return templates
    for filename in sorted(os.listdir(config.TEMPLATE_FOLDER)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(config.TEMPLATE_FOLDER, filename)
        try:
            with open(path, "r") as f:
                data = json.load(f)
            templates.append({
                "id": data.get("id", filename.replace(".json", "")),
                "name": data.get("name", "Untitled"),
                "description": data.get("description", ""),
            })
        except Exception:
            continue
    return templates


@router.get("")
def list_templates():
    return _list_template_files()


@router.get("/{template_id}/preview")
def preview_template(template_id: str):
    template = _load_template(template_id)
    os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)
    preview_path = os.path.join(config.OUTPUT_FOLDER, f"preview_{template_id}.pdf")
    render_preview(template, preview_path)
    return FileResponse(
        preview_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"},
    )


@router.post("/save")
def save_template(request: SaveTemplateRequest):
    template = request.template
    os.makedirs(config.TEMPLATE_FOLDER, exist_ok=True)
    path = os.path.join(config.TEMPLATE_FOLDER, f"{template.id}.json")
    with open(path, "w") as f:
        json.dump(template.model_dump(), f, indent=2)
    return {"message": "Template saved", "id": template.id}
