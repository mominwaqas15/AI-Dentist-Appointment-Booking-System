from sqlalchemy.orm import Session
from models import User, Service, Dentist, Appointment, AppointmentPreference, DentistService
from datetime import datetime
import schemas
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


from sqlalchemy.orm import Session
from models import User
from datetime import datetime
from fastapi import HTTPException

def get_user_by_email(db: Session, email: str):
    """
    Check if a user exists with the given email.
    :param db: Database session
    :param email: User email to check
    :return: User instance if found, otherwise None
    """
    return db.query(User).filter(User.user_email == email).first()

def get_user_by_username(db: Session, username: str):
    """
    Check if a user exists with the given username.
    :param db: Database session
    :param username: Username to check
    :return: User instance if found, otherwise None
    """
    return db.query(User).filter(User.user_name == username).first()

def create_user(db: Session, user: schemas.UserSignUp):
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        user_name=user.username,
        user_phone_number=user.phone_number,
        user_age=user.age,
        user_email=user.email,
        user_password=user.password,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, username_or_email: str, password: str):
    user = db.query(User).filter(
        (User.user_name == username_or_email) | (User.user_email == username_or_email)
    ).first()

    if not user or user.user_password != password:
        return None

    return user

def get_all_services(db: Session):
    return db.query(Service).all()

def get_dentists_by_service(db: Session, service_id: int):
    return db.query(Dentist).join(DentistService).filter(DentistService.service_id == service_id).all()

def get_all_dentists(db: Session):
    return db.query(Dentist).all()

def create_appointment_preference(db: Session, preference: schemas.AppointmentPreferenceCreate, file_path: str = None):
    try:
        new_preference = AppointmentPreference(
            user_id=preference.user_id,
            dentist_id=preference.dentist_id,
            first_name=preference.first_name,  # ✅ Updated field
            last_name=preference.last_name,    # ✅ Updated field
            patient_gender=preference.patient_gender,
            patient_age=preference.patient_age,
            patient_phone_number=preference.patient_phone_number,
            patient_email_address=preference.patient_email_address,
            preferred_dates=preference.preferred_dates,
            relation=preference.relation,
            special_notes=preference.special_notes,
            created_at=datetime.utcnow(),
            file_path=file_path
        )
        db.add(new_preference)
        db.commit()
        db.refresh(new_preference)
        return new_preference
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid user_id or dentist_id. Please provide valid references.")
    
def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    try:
        new_appointment = Appointment(
            user_id=appointment.user_id,
            dentist_id=appointment.dentist_id,
            appointment_date= "",
            appointment_time= "",
            appointment_status="In Progress",
            created_at=datetime.utcnow()
        )
        
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid user_id or dentist_id. Please provide valid references.")
    
def get_appointments_by_user(db: Session, user_id: int):
    return db.query(Appointment).filter(Appointment.user_id == user_id).all()    

def get_services_by_dentist(db: Session, dentist_id: int):
    services = db.query(Service).join(DentistService).filter(DentistService.dentist_id == dentist_id).all()
    if not services:
        raise HTTPException(status_code=404, detail="No services found for this dentist.")
    return services