from sqlalchemy.orm import Session

from models.complaint import Complaint
from models.user import User
from schemas.complaint import ComplaintCreateRequest
from utils.ticket_service import generate_ticket_id


class ComplaintService:
    def upsert_user(self, db: Session, payload: ComplaintCreateRequest) -> User:
        user = db.query(User).filter(User.email == payload.email).first()
        if user:
            user.name = payload.full_name
            user.phone = payload.phone_number
            user.address = payload.address
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

        user = User(
            name=payload.full_name,
            email=payload.email,
            phone=payload.phone_number,
            address=payload.address,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def create_complaint(self, db: Session, user_id: int, payload: ComplaintCreateRequest) -> Complaint:
        complaint = Complaint(
            ticket_id=generate_ticket_id(),
            user_id=user_id,
            complaint_type=payload.complaint_type,
            description=payload.description,
            status="pending",
            language=payload.language,
            date_time=payload.date_time,
            amount_lost=payload.amount_lost,
            transaction_id=payload.transaction_id,
            platform=payload.platform,
            suspect_details=payload.suspect_details,
            suspect_vpa=payload.suspect_vpa,
            suspect_phone=payload.suspect_phone,
            suspect_bank_account=payload.suspect_bank_account,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return complaint

    def build_user_summary(self, payload: ComplaintCreateRequest, ticket_id: str) -> str:
        return (
            f"Ticket ID: {ticket_id}. "
            f"Type: {payload.complaint_type}. "
            f"Description: {payload.description}. "
            f"Date and Time: {payload.date_time}."
        )

    def build_admin_english_summary(self, payload: ComplaintCreateRequest, ticket_id: str) -> str:
        return (
            f"Ticket ID: {ticket_id}\n"
            f"Name: {payload.full_name}\n"
            f"Phone: {payload.phone_number}\n"
            f"Email: {payload.email}\n"
            f"Address: {payload.address}\n"
            f"Type: {payload.complaint_type}\n"
            f"Date and Time: {payload.date_time}\n"
            f"Description: {payload.description}\n"
            f"Amount Lost: {payload.amount_lost or 'N/A'}\n"
            f"Transaction ID/UTR: {payload.transaction_id or 'N/A'}\n"
            f"Platform: {payload.platform or 'N/A'}\n"
            f"Suspect Details: {payload.suspect_details or 'N/A'}\n"
            f"Original Language: {payload.language}"
        )


complaint_service = ComplaintService()
