from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from db import Base

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    arxiv_channel = Column(String, nullable=False)
    interest_description = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

