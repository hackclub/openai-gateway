from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid

from sqlalchemy.types import BLOB, Text
from open_ai_token.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    slack_id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_club_leader = Column(Boolean, default=False)
    can_use_superpowers = Column(Boolean, default=False)
    image_usage_allowed = Column(Boolean, default=True)
    gpt4_usage_allowed = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    tokens = relationship("Token", back_populates="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Token(Base):
    __tablename__ = "tokens"
    token = Column(String, primary_key=True, default=uuid.uuid4)
    user_id = Column(String, ForeignKey("users.slack_id"))
    is_active = Column(Boolean, default=True)
    is_revoked = Column(Boolean, default=False) # This is for the user to revoke the token
    is_expired = Column(Boolean, default=False) # This is for the system to revoke the token
    is_blocked = Column(Boolean, default=False) # This is for the system to block the token due to abuse
    uses_left = Column(Integer, default=500)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="tokens")
    usages = relationship("Usage", backref="token")


class Usage(Base):
    __tablename__ = "usages"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    request_data = Column(Text)
    response_data = Column(Text)
    token_id = Column(String, ForeignKey("tokens.token"))
    endpoint = Column(String)
