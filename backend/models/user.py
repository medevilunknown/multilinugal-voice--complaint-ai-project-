from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # BYOK & Social Identity fields
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    custom_gemini_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_managed_ai: Mapped[bool] = mapped_column(Boolean, default=True)

    complaints = relationship("Complaint", back_populates="user")
