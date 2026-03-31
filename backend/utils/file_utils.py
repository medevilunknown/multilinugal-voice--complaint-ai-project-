from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from config import settings


def ensure_upload_dirs() -> None:
    base = Path(settings.upload_dir)
    (base / "evidence").mkdir(parents=True, exist_ok=True)
    (base / "id_proofs").mkdir(parents=True, exist_ok=True)


def save_upload_file(upload: UploadFile, sub_dir: str) -> str:
    ensure_upload_dirs()
    safe_name = upload.filename or "file"
    extension = Path(safe_name).suffix
    final_name = f"{uuid4().hex}{extension}"
    final_path = Path(settings.upload_dir) / sub_dir / final_name

    with final_path.open("wb") as f:
        f.write(upload.file.read())

    return str(final_path)
