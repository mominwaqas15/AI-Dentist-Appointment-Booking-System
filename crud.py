from sqlalchemy.orm import Session
from models import User, Service, Dentist, Appointment, AppointmentPreference, DentistService
from datetime import datetime
# from passlib.context import CryptContext
import schemas
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        full_name=user.full_name,
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

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    
    # Ensure user exists
    if not user:
        return None

    # Direct string comparison (since no hashing is applied)
    if user.user_password != password:
        return None

    return user

def get_all_services(db: Session):
    return db.query(Service).all()

def get_dentists_by_service(db: Session, service_id: int):
    return db.query(Dentist).join(DentistService).filter(DentistService.service_id == service_id).all()

def get_all_dentists(db: Session):
    return db.query(Dentist).all()

def create_appointment_preference(db: Session, preference: schemas.AppointmentPreferenceCreate):
    try:
        new_preference = AppointmentPreference(
            user_id=preference.user_id,
            dentist_id=preference.dentist_id,
            patient_name=preference.patient_name,
            patient_gender=preference.patient_gender,
            patient_age=preference.patient_age,
            patient_phone_number=preference.patient_phone_number,
            patient_email_address=preference.patient_email_address,
            preferred_dates=preference.preferred_dates,
            relation=preference.relation,
            special_notes=preference.special_notes,
            created_at=datetime.utcnow()
        )
        db.add(new_preference)
        db.commit()
        db.refresh(new_preference)
        return new_preference

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid user_id or dentist_id. Please provide valid references.")
    
def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    try:
        new_appointment = Appointment(
            user_id=appointment.user_id,
            dentist_id=appointment.dentist_id,
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            appointment_status=appointment.appointment_status,
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