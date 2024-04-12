from typing import Union

from pydantic import BaseModel

import datetime

class UserBase(BaseModel):
    slack_id: str
    name: str
    is_admin: bool = False
    is_club_leader: bool = False
    can_use_superpowers: bool = False
    image_usage_allowed: bool = True
    gpt4_usage_allowed: bool = False
    is_banned: bool = False
    is_active: bool = True

    def __str__(self):
        return self.name

class UserCreate(UserBase):
    email: str

class User(UserBase):
    email: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TokenBase(BaseModel):
    token: str
    owner_slack_id: str
    is_active: bool = True
    is_revoked: bool = False
    is_expired: bool = False
    is_blocked: bool = False
    uses_left: int = 500
    last_used: datetime.datetime

class TokenCreate(TokenBase):
    pass

class Token(TokenBase):
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TokenUse(BaseModel):
    token: str
    owner_slack_id: str

    class Config:
        from_attributes = True
