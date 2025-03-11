from fastapi import FastAPI, Depends
from fastapi import UploadFile, HTTPException
from fastapi import FastAPI, Depends, File, Form
from sqlalchemy.orm import Session
from db_conn import create_db
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from typing import List, Optional
import schemas, gpt, call_handler
import uvicorn, os
import models
import shutil
import crud
from datetime import datetime
from models import Appointment

engine, SessionLocal = create_db()
models.Base.metadata.create_all(bind=engine)

UPLOAD_DIRECTORY = "uploads/"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

app = FastAPI()

origins = [
    "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


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
    user = crud.authenticate_user(db, username_or_email=user_credentials.username, password=user_credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username/email or password")
    return user

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
def store_appointment_preferences(
    user_id: int = Form(...),
    dentist_id: int = Form(...),
    first_name: str = Form(...),  # ✅ Updated from patient_name
    last_name: str = Form(...),   # ✅ New field added
    patient_gender: str = Form(...),
    patient_age: str = Form(...),
    patient_phone_number: str = Form(...),
    patient_email_address: str = Form(...),
    preferred_dates: str = Form(...),
    relation: Optional[str] = Form(None),
    special_notes: Optional[str] = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    preference = schemas.AppointmentPreferenceCreate(
        user_id=user_id,
        dentist_id=dentist_id,
        first_name=first_name,  # ✅ Updated field
        last_name=last_name,    # ✅ Updated field
        patient_gender=patient_gender,
        patient_age=patient_age,
        patient_phone_number=patient_phone_number,
        patient_email_address=patient_email_address,
        preferred_dates=preferred_dates,
        relation=relation,
        special_notes=special_notes
    )

    # Handle file upload if provided
    file_path = None
    if file:
        file_path = os.path.join(UPLOAD_DIRECTORY, f"preference_{user_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # Store the appointment preference in the database
    appointment_preference = crud.create_appointment_preference(db, preference, file_path)
    
    return appointment_preference

@app.post("/book-appointment", response_model=dict)
def book_appointment(
    appointment: schemas.AppointmentCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    # Create the initial appointment record with status "Processing"
    new_appointment = Appointment(
        user_id=appointment.user_id,
        dentist_id=appointment.dentist_id,
        appointment_status="Processing",
        created_at=datetime.utcnow()
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    # Run the call processing and appointment update in the background
    background_tasks.add_task(crud.process_appointment_in_background, db, appointment, new_appointment)

    # Return an immediate response
    return {"message": "Appointment request received. Processing in background.", "appointment_id": new_appointment.appointment_id}

@app.get("/get-user-appointment/{user_id}", response_model=list[schemas.AppointmentResponse])
def get_user_appointments(user_id: int, db: Session = Depends(get_db)):
    appointments = crud.get_appointments_by_user(db, user_id)
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found for this user.")
    return appointments

@app.post("/add-dentist", response_model=schemas.DentistResponse)
def add_dentist(dentist: schemas.DentistCreate, db: Session = Depends(get_db)):
    new_dentist = crud.create_dentist(db, dentist)
    return new_dentist

if __name__ == "__main__":
    uvicorn.run("init:app", host=HOST, port=int(PORT), reload=True)