from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime
from open_ai_token.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    slack_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_club_leader = Column(Boolean, default=False)
    can_use_superpowers = Column(Boolean, default=False)
    image_uage_allowed = Column(Boolean, default=True)
    gpt4_usage_allowed = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    tokens = relationship("Token", back_populates="owner")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Token(Base):
    __tablename__ = "tokens"
    token = Column(String, primary_key=True, index=True)
    owner_slack_id = Column(String, ForeignKey("users.slack_id"))
    owner = relationship("User", back_populates="tokens")
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False) # This is for the user to revoke the token
    is_expired = Column(Boolean, default=False) # This is for the system to revoke the token
    is_blocked = Column(Boolean, default=False) # This is for the system to block the token due to abuse
    uses_left = Column(Integer, default=500)
    last_used = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
