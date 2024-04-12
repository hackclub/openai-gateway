from sqlalchemy.orm import Session

from open_ai_token import models, schemas


def get_user_by_slack_id(db: Session, slack_id: str):
    return db.query(models.User).filter(models.User.slack_id == slack_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_slack_id_and_email(db: Session, slack_id: str, email: str):
    return db.query(models.User).filter(models.User.slack_id == slack_id, models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(slack_id=user.slack_id, name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_token(db: Session, token: str):
    return db.query(models.Token).filter(models.Token.token == token).first()

def get_tokens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Token).offset(skip).limit(limit).all()

def create_token(db: Session, token: schemas.TokenCreate):
    db_token = models.Token(token=token.token, owner_slack_id=token.owner_slack_id)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def use_token(db: Session, token: schemas.TokenUse):
    db_token = db.query(models.Token).filter(models.Token.token == token.token, models.Token.owner_slack_id == token.owner_slack_id).first()
    db_token.uses_left -= 1
    db.commit()
    db.refresh(db_token)
    return db_token

def revoke_token(db: Session, token: schemas.TokenUse):
    db_token = db.query(models.Token).filter(models.Token.token == token.token, models.Token.owner_slack_id == token.owner_slack_id).first()
    db_token.is_revoked = True
    db.commit()
    db.refresh(db_token)
    return db_token

def block_token(db: Session, token: schemas.TokenUse):
    db_token = db.query(models.Token).filter(models.Token.token == token.token, models.Token.owner_slack_id == token.owner_slack_id).first()
    db_token.is_blocked = True
    db.commit()
    db.refresh(db_token)
    return db_token

def unblock_token(db: Session, token: schemas.TokenUse):
    db_token = db.query(models.Token).filter(models.Token.token == token.token, models.Token.owner_slack_id == token.owner_slack_id).first()
    db_token.is_blocked = False
    db.commit()
    db.refresh(db_token)
    return db_token

def delete_token(db: Session, token: schemas.TokenUse):
    db_token = db.query(models.Token).filter(models.Token.token == token.token, models.Token.owner_slack_id == token.owner_slack_id).first()
    db.delete(db_token)
    db.commit()
    return db_token

def delete_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.slack_id == user.slack_id, models.User.email == user.email).first()
    db.delete(db_user)
    db.commit()
    return db_user

def update_user(db: Session, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.slack_id == user.slack_id, models.User.email == user.email).first()
    db_user.name = user.name
    db.commit()
    db.refresh(db_user)
    return db_user

def update_token(db: Session, token: schemas.TokenCreate):
    db_token = db.query(models.Token).filter(models.Token.token == token.token, models.Token.owner_slack_id == token.owner_slack_id).first()
    db_token.uses_left = token.uses_left
    db.commit()
    db.refresh(db_token)
    return db_token

def get_tokens_by_owner(db: Session, owner_slack_id: str):
    return db.query(models.Token).filter(models.Token.owner_slack_id == owner_slack_id).all()

def get_tokens_by_owner_and_token(db: Session, owner_slack_id: str, token: str):
    return db.query(models.Token).filter(models.Token.owner_slack_id == owner_slack_id, models.Token.token == token).first()

def get_tokens_by_owner_and_token_and_uses_left(db: Session, owner_slack_id: str, token: str, uses_left: int):
    return db.query(models.Token).filter(models.Token.owner_slack_id == owner_slack_id, models.Token.token == token, models.Token.uses_left == uses_left).first()

def get_tokens_by_owner_and_token_and_is_revoked(db: Session, owner_slack_id: str, token: str, is_revoked: bool):
    return db.query(models.Token).filter(models.Token.owner_slack_id == owner_slack_id, models.Token.token == token, models.Token.is_revoked == is_revoked).first()

def get_tokens_by_owner_and_token_and_is_blocked(db: Session, owner_slack_id: str, token: str, is_blocked: bool):
    return db.query(models.Token).filter(models.Token.owner_slack_id == owner_slack_id, models.Token.token == token, models.Token.is_blocked == is_blocked).first()
