from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from open_ai_token.openai import chat_completions

load_dotenv()

origins = ["*"]

security = HTTPBearer()

app = FastAPI(
    title="OpenAI Gateway",
    description="API Gateway for OpenAI",
    version="0.1.0",
    contact={"name": "Arpan Pandey", "email": "arpan@hackclub.com"}
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from open_ai_token import schemas, crud, models
from open_ai_token.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
check_if_prod = bool(os.getenv("PRODUCTION"))
show_in_docs_for_priv_routes = not check_if_prod

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    db = SessionLocal()
    if not crud.check_token(db, token):
        raise ValueError("Invalid token")
    token = crud.get_token(db, token)
    if token is None:
        raise ValueError("Invalid token")
    if token.uses_left == 0:
        raise ValueError("No uses left")
    if token.is_expired or not token.is_active or token.is_revoked or token.is_blocked:
        raise ValueError("Token is expired or disabled")

@app.get("/")
def read_root():
    return {"Message": "Hello traveller!\n You have reached the Open AI Token API by Hack Club. \n\nPlease refer to the documentation at /docs or /redoc to get started. \n You may also need to get a token from the Hack Club Slack to use this API. \n\nHappy Hacking!"}

@app.post("/register", include_in_schema=show_in_docs_for_priv_routes, response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db, user)
        return db_user
    except ValueError as e:
        return {"Error": str(e)}

@app.get("/users", include_in_schema=show_in_docs_for_priv_routes, response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    if len(users) == 0:
        raise HTTPException(status_code=404, detail="No users found")
    return users

@app.get("/user/{slack_id}", include_in_schema=show_in_docs_for_priv_routes, response_model=schemas.User)
def read_user(slack_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_slack_id(db, slack_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/token/{token}", include_in_schema=show_in_docs_for_priv_routes, response_model=schemas.Token)
def read_token(token: str, db: Session = Depends(get_db)):
    db_token = crud.get_token(db, token)
    if db_token is None:
        raise HTTPException(status_code=404, detail="Token not found")
    return db_token

@app.get("/tokens", include_in_schema=show_in_docs_for_priv_routes, response_model=list[schemas.Token])
def read_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tokens = crud.get_tokens(db, skip=skip, limit=limit)
    if len(tokens) == 0:
        raise HTTPException(status_code=404, detail="No tokens found")
    return tokens

@app.post("/token", include_in_schema=show_in_docs_for_priv_routes, response_model=schemas.Token)
def create_token(token: schemas.TokenCreate, db: Session = Depends(get_db)):
    try:
        db_token = crud.create_token(db, token)
        return db_token
    except ValueError as e:
        return {"Error": str(e)}

# Now we create the public routes
# These routes are always included in the documentation
# These mirror the OpenAI API routes
# Use tokens for authentication as headers

@app.post("/chat/completions", include_in_schema=True)
async def post_chat_completions(prompt: schemas.Prompt, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    This route is used to get completions for a prompt.
    """

    try:
        authenticate(credentials)
        token = credentials.credentials
        db_token = crud.get_token(db, token)
        if db_token is None:
            raise ValueError("Token not found")
        db_token.uses_left -= 1
        db.commit()
        try:
            completions = await chat_completions(prompt, db_token)
            if completions[1] != 200:
                raise HTTPException(status_code=completions[1], detail=completions[0])
            return completions[0]
        except ValueError as e:
            return {"Error": str(e)}

    except ValueError as e:
        return {"Error": str(e)}
