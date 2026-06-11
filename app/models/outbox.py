import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from app.core.database import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


class LogOutbox(Base, TimestampMixin):
    __tablename__ = "outbox_logs"

    outbox_id:  Mapped[int] = mapped_column(primary_key=True, autoincrement=True)   
    log_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    processed: Mapped[bool]  = mapped_column(Boolean, default=False, index=True)