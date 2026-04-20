from datetime import datetime
from sqlalchemy import create_engine, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from core.config import settings

# Quando mudar para PostgreSQL, o connect_args pode ser removido.
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()