from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class ComplaintCreateRequest(BaseModel):
    full_name: str
    phone_number: str
    email: EmailStr
    address: str
    complaint_type: str
    date_time: str
    description: str
    amount_lost: str | None = None
    transaction_id: str | None = None
    platform: str | None = None
    suspect_details: str | None = None
    suspect_vpa: str | None = None
    suspect_phone: str | None = None
    suspect_bank_account: str | None = None
    language: str = "English"


class ComplaintCreateResponse(BaseModel):
    ticket_id: str
    status: str
    created_at: datetime
    message: str


class ComplaintTrackResponse(BaseModel):
    ticket_id: str
    status: str
    complaint_type: str
    description: str
    language: str
    created_at: datetime


class ComplaintStatusUpdateRequest(BaseModel):
    ticket_id: str = Field(..., min_length=4)
    status: str = Field(..., pattern="^(pending|reviewing|resolved)$")
