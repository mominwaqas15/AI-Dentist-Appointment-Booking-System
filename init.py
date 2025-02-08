from fastapi import FastAPI, Depends
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from db_conn import create_db
from dotenv import load_dotenv
import schemas
import uvicorn, os
import models
import crud


engine, SessionLocal = create_db()
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI()

load_dotenv()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def sign_up(user: schemas.UserSignUp, db: Session = Depends(get_db)):
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Account with this email already exists")

    # Check if username already exists
    db_username = crud.get_user_by_username(db, username=user.username)
    if db_username:
        raise HTTPException(status_code=400, detail="Username is already taken. Please choose another one.")

    crud.create_user(db=db, user=user)

    return {"message": "Sign Up Successful. Please check your email to verify your account."}

if __name__ == "__main__":
    uvicorn.run("init:app", host="127.0.0.1", port=8000, reload=True)