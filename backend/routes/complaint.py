import mimetypes
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.complaint import Complaint
from models.evidence import Evidence
from schemas.complaint import ComplaintCreateRequest, ComplaintCreateResponse, ComplaintTrackResponse
from services.complaint_service import complaint_service
from services.email_service import email_service
from services.gemini_service import gemini_service
from services.translation_service import translation_service
from services.validation_service import validation_service
from utils.file_utils import save_upload_file


router = APIRouter(prefix="/complaint", tags=["Complaint"])
logger = logging.getLogger(__name__)


@router.post("/create", response_model=ComplaintCreateResponse)
def create_complaint(payload: ComplaintCreateRequest, db: Session = Depends(get_db)):
    errors = validation_service.validate_create_complaint(payload.model_dump())
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    user = complaint_service.upsert_user(db, payload)
    complaint = complaint_service.create_complaint(db, user_id=user.id, payload=payload)

    success_message = "Complaint created successfully"
    localized_message = success_message
    localized_summary = complaint_service.build_user_summary(payload, complaint.ticket_id)
    admin_summary_en = complaint_service.build_admin_english_summary(payload, complaint.ticket_id)

    # Non-critical integrations should never block complaint creation.
    try:
        localized_summary = translation_service.translate(localized_summary, payload.language)
        admin_summary_en = translation_service.to_english(admin_summary_en)
        localized_message = translation_service.translate(success_message, payload.language)
    except Exception as exc:
        logger.warning("Translation failed for ticket %s: %s", complaint.ticket_id, exc)

    try:
        email_service.send_user_ticket_email(payload.email, complaint.ticket_id, localized_summary)
        email_service.send_admin_complaint_email(settings.admin_email, complaint.ticket_id, admin_summary_en)
    except Exception as exc:
        logger.warning("Email dispatch failed for ticket %s: %s", complaint.ticket_id, exc)

    return ComplaintCreateResponse(
        ticket_id=complaint.ticket_id,
        status=complaint.status,
        created_at=complaint.created_at,
        message=localized_message,
    )


@router.post("/upload")
def upload_evidence(
    ticket_id: str = Form(...),
    file_kind: str = Form("evidence"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(Complaint.ticket_id == ticket_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Ticket not found")

    sub_dir = "id_proofs" if file_kind == "id_proof" else "evidence"
    file_path = save_upload_file(file, sub_dir=sub_dir)

    mime_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    extracted_text = ""
    try:
        extracted_text = gemini_service.analyze_evidence(file_path=file_path, mime_type=mime_type)
    except Exception as exc:
        logger.warning("Evidence analysis failed for %s: %s", file_path, exc)

    evidence = Evidence(
        complaint_id=complaint.id,
        file_path=file_path,
        extracted_text=extracted_text,
    )
    db.add(evidence)

    # Issue 1 Fix: Verify/override user name based on Government ID
    if file_kind == "id_proof" and extracted_text:
        try:
            prompt = "Extract the full name of the person from this Government ID text. Return ONLY the name, nothing else. If you can't find a name, return EMPTY."
            response = gemini_service.model.generate_content([prompt, extracted_text])
            extracted_name = (response.text or "").strip()
            if extracted_name and extracted_name != "EMPTY" and complaint.user:
                complaint.user.name = extracted_name
                db.add(complaint.user)
        except Exception as e:
            logger.error(f"Failed to extract name from ID proof: {e}")

    db.commit()
    db.refresh(evidence)

    return {
        "ticket_id": complaint.ticket_id,
        "evidence_id": evidence.id,
        "file_path": evidence.file_path,
        "extracted_text": evidence.extracted_text,
    }


@router.get("/{ticket_id}", response_model=ComplaintTrackResponse)
def track_complaint(ticket_id: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.ticket_id == ticket_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return ComplaintTrackResponse(
        ticket_id=complaint.ticket_id,
        status=complaint.status,
        complaint_type=complaint.complaint_type,
        description=complaint.description,
        language=complaint.language,
        created_at=complaint.created_at,
    )
