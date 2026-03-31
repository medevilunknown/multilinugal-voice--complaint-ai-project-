from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.admin import Admin
from models.complaint import Complaint
from schemas.admin import AdminLoginRequest, AdminLoginResponse
from schemas.complaint import ComplaintStatusUpdateRequest
from services.auth_service import auth_service, get_current_admin


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login_admin(db, email=payload.email, password=payload.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return AdminLoginResponse(access_token=token)


@router.get("/complaints")
def get_all_complaints(
    db: Session = Depends(get_db),
    _admin: Admin = Depends(get_current_admin),
):
    complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()

    return [
        {
            "ticket_id": c.ticket_id,
            "name": c.user.name if c.user else "",
            "email": c.user.email if c.user else "",
            "phone": c.user.phone if c.user else "",
            "complaint_type": c.complaint_type,
            "description": c.description,
            "status": c.status,
            "language": c.language,
            "created_at": c.created_at,
            "evidence_files": [
                {
                    "file_path": e.file_path,
                    "file_url": f"/{e.file_path.replace('\\\\', '/')}",
                    "extracted_text": e.extracted_text,
                }
                for e in c.evidence_items
            ],
        }
        for c in complaints
    ]


@router.put("/update-status")
def update_status(
    payload: ComplaintStatusUpdateRequest,
    db: Session = Depends(get_db),
    _admin: Admin = Depends(get_current_admin),
):
    complaint = db.query(Complaint).filter(Complaint.ticket_id == payload.ticket_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = payload.status
    db.add(complaint)
    db.commit()

    return {"message": "Status updated", "ticket_id": complaint.ticket_id, "status": complaint.status}
