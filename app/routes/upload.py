import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models import UploadResponse
from app.services.document_parser import parse_file
from app import config

router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    allowed = (".pdf", ".doc", ".docx", ".html", ".htm", ".txt")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed)}"
        )

    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    file_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(config.UPLOAD_FOLDER, f"{file_id}{ext}")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    try:
        result = parse_file(save_path)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {e}")

    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        raw_text=result["raw_text"],
        detected_fields=result["detected_fields"],
    )
