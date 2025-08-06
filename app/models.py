from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid


class URLMapping(Base):
    __tablename__ = "url_mappings"

    shortcode = Column(String(255), primary_key=True, index=True)
    original_url = Column(String(2048), nullable=False)
    update_id = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    last_redirect = Column(DateTime(timezone=True), nullable=True)
    redirect_count = Column(Integer, default=0)
