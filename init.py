from fastapi import FastAPI, Depends
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from db_conn import create_db
from dotenv import load_dotenv
from typing import List
import schemas
import uvicorn, os
import models
import crud

engine, SessionLocal = create_db()
models.Base.metadata.create_all(bind=engine)

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

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

@app.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, username=user_credentials.username, password=user_credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "Login successful", "user": user.user_name}

@app.get("/get-services", response_model=list[schemas.ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    services = crud.get_all_services(db)
    return services

@app.get("/get-service-dentists/{service_id}", response_model=list[schemas.DentistResponse])
def get_service_dentists(service_id: int, db: Session = Depends(get_db)):
    dentists = crud.get_dentists_by_service(db, service_id)
    if not dentists:
        raise HTTPException(status_code=404, detail="No dentists found for this service.")
    return dentists

@app.get("/get-dentist-services/{dentist_id}", response_model=List[schemas.DentistServiceResponse])
def get_dentist_services(dentist_id: int, db: Session = Depends(get_db)):
    services = crud.get_services_by_dentist(db, dentist_id)
    return services


@app.get("/get-dentists", response_model=list[schemas.DentistResponse])
def get_dentists(db: Session = Depends(get_db)):
    dentists = crud.get_all_dentists(db)
    return dentists

@app.post("/store-appointment-preferences", response_model=schemas.AppointmentPreferenceResponse)
def get_appointment_preferences(preference: schemas.AppointmentPreferenceCreate, db: Session = Depends(get_db)):
    appointment_preference = crud.create_appointment_preference(db, preference)
    return appointment_preference

@app.post("/book-appointment", response_model=schemas.AppointmentResponse)
def book_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    booked_appointment = crud.create_appointment(db, appointment)
    return booked_appointment

@app.get("/get-user-appointment/{user_id}", response_model=list[schemas.AppointmentResponse])
def get_user_appointments(user_id: int, db: Session = Depends(get_db)):
    appointments = crud.get_appointments_by_user(db, user_id)
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found for this user.")
    return appointments

if __name__ == "__main__":
    uvicorn.run("init:app", host=HOST, port=PORT, reload=True)