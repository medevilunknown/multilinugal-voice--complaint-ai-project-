import re

from email_validator import validate_email, EmailNotValidError

from utils.constants import COMPLAINT_TYPES, REQUIRED_COMPLAINT_FIELDS


PHONE_RE = re.compile(r"^(\+91|91)?[6-9]\d{9}$")
UTR_RE = re.compile(r"^[A-Za-z0-9\-]{8,30}$")
SIMPLE_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationService:
    def validate_required_fields(self, payload: dict) -> list[str]:
        missing = []
        for field in REQUIRED_COMPLAINT_FIELDS:
            if not payload.get(field):
                missing.append(field)
        return missing

    def validate_phone(self, phone: str) -> bool:
        clean = phone.replace(" ", "")
        return bool(PHONE_RE.match(clean))

    def validate_email(self, email: str) -> bool:
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            # Keep syntax-friendly fallback to avoid blocking users on special-use domains.
            return bool(SIMPLE_EMAIL_RE.match(email or ""))

    def validate_utr(self, utr: str | None) -> bool:
        if not utr:
            return True
        return bool(UTR_RE.match(utr))

    def validate_complaint_type(self, complaint_type: str) -> bool:
        return complaint_type in COMPLAINT_TYPES

    def validate_create_complaint(self, payload: dict) -> list[str]:
        errors: list[str] = []

        missing = self.validate_required_fields(payload)
        if missing:
            errors.append(f"Missing required fields: {', '.join(missing)}")

        if "phone_number" in payload and not self.validate_phone(payload["phone_number"]):
            errors.append("Invalid phone format")

        if "email" in payload and not self.validate_email(payload["email"]):
            errors.append("Invalid email format")

        if "transaction_id" in payload and not self.validate_utr(payload.get("transaction_id")):
            errors.append("Invalid UTR/Transaction ID format")

        if "complaint_type" in payload and not self.validate_complaint_type(payload["complaint_type"]):
            errors.append("Invalid complaint type")

        return errors


validation_service = ValidationService()
