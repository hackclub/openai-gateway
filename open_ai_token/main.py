from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
app = FastAPI()
from open_ai_token import schemas, crud, models
from open_ai_token.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
check_if_prod = os.getenv("PRODUCTION")
show_in_docs_for_priv_routes = False if check_if_prod == "True" else True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Message": "Hello traveller!\n You have reached the Open AI Token API by Hack Club. \n\nPlease refer to the documentation at /docs or /redoc to get started. \n You may also need to get a token from the Hack Club Slack to use this API. \n\nHappy Hacking!"}

@app.post("/register", include_in_schema=show_in_docs_for_priv_routes, response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = crud.create_user(db, user)
    return db_user
