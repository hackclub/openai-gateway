from typing_extensions import Tuple, Union
from fastapi import FastAPI, HTTPException, Query, Response, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import open_ai_token.openai as openai_module
from typing import Annotated
from open_ai_token import schemas, crud
from datetime import datetime

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
    return token

def usage_register(sec: schemas.Token, endpoint: str, data: str, resp,db: Session = Depends(get_db),):
   resp = " ".join([str(x) for x in resp])
   crud.register_usage(db, schemas.UsageCreate(
        token=sec.token,
        request_data=str(data),
        response_data=str(resp),
        created_at=datetime.now(),
        endpoint=endpoint
    ))


@app.get("/")
def read_root():
    return {"Message": "Hello traveller!\n You have reached the Open AI Token API by Hack Club. \n\nPlease refer to the documentation at /docs or /redoc to get started. \n You may also need to get a token from the Hack Club Slack to use this API. \n\nHappy Hacking!"}

@app.exception_handler(ValueError)
@app.post("/register", include_in_schema=show_in_docs_for_priv_routes, response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = crud.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
#

@app.get("/models")
def models(
    response: Response
):
    """
    Get the list of models available on OpenAI API
    """
    res: Tuple = openai_module.models()
    return res

@app.post("/model/{model_name}")
def model(
    model_name: str,
    response: Response
):
    """
    Get the details of a model available on OpenAI API
    """
    res: Tuple = openai_module.model(model_name)
    return res



@app.post("/chat/completions")
def post_chat_completions(
    data: dict, response: Response, credentials=Depends(security), db: Session = Depends(get_db)
):
    """
    Get the completions for a chat model
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.post_chat_completions(data, sec)

    # Register the use of the token
    crud.use_token(db, sec)
    usage_register(sec, "chat/completions", str(data), resp, db)

    if isinstance(resp, tuple) and resp[1] != 200:
        response.status_code = resp[1]
        return resp[0]

    return StreamingResponse(resp, media_type="application/json")

@app.post("/images/generations")
def create_image(data: dict, response: Response, credentials=Depends(security)):
    """
    Create an image on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.create_image(data)
    return StreamingResponse(resp, media_type="image/png")

@app.post("/embeddings")
def embeddings(data: dict, response: Response, credentials=Depends(security)):
    """
    Get the embeddings of a text on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.embeddings(data)
    return StreamingResponse(resp, media_type="application/json")

@app.post("/fine_tuning/jobs")
def create_fine_tuning_jobs(data: dict, response: Response, credentials=Depends(security)):
    """
    Create a fine tuning job on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.create_fine_tuning(data)
    return resp

# List all fine tuning jobs
@app.get("/fine_tuning/jobs")
def list_fine_tuning_jobs(response: Response, credentials=Depends(security)):
    """
    List all fine tuning jobs on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.list_fine_tuning()
    return resp

# List fine tuning events
@app.get("/fine_tuning/jobs/{job_id}/events")
def list_fine_tuning_events(job_id: str, response: Response, credentials=Depends(security)):
    """
    List all fine tuning events on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.list_fine_tuning_events(job_id)
    return resp

# list fine tuning checkpoints
@app.get("/fine_tuning/jobs/{job_id}/checkpoints")
def list_fine_tuning_checkpoints(job_id: str, response: Response, credentials=Depends(security)):
    """
    List all fine tuning checkpoints on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.list_fine_tuning_checkpoints(job_id)
    return resp

# retrieve a fine tuning job
@app.get("/fine_tuning/jobs/{job_id}")
def get_fine_tuning_job(job_id: str, response: Response, credentials=Depends(security)):
    """
    Retrieve a fine tuning job on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.retrieve_fine_tuning(job_id)
    return resp

# cancel a fine tuning job
@app.post("/fine_tuning/jobs/{job_id}/cancel")
def cancel_fine_tuning_job(job_id: str, response: Response, credentials=Depends(security)):
    """
    Cancel a fine tuning job on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.cancel_fine_tuning(job_id)
    return resp

# Batch endpoints

@app.post("/batches")
def create_batch(data: dict, response: Response, credentials=Depends(security)):
    """
    Create a batch on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.create_batch(data)
    return resp

@app.get("/batches")
def list_batches(response: Response, credentials=Depends(security)):
    """
    List all batches on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.list_batches()
    return resp

@app.get("/batches/{batch_id}")
def get_batch(batch_id: str, response: Response, credentials=Depends(security)):
    """
    Retrieve a batch on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.retrieve_batch(batch_id)
    return resp

@app.post("/batches/{batch_id}/cancel")
def cancel_batch(batch_id: str, response: Response, credentials=Depends(security)):
    """
    Cancel a batch on OpenAI API
    """
    sec = authenticate(credentials)

    if not sec:
        response.status_code = 401
        return {"message": "Invalid token"}

    resp = openai_module.cancel_batch(batch_id)
    return resp
