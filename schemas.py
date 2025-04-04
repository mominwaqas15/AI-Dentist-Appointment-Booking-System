from pydantic import BaseModel
from datetime import datetime
from pydantic import Field
from typing import Optional, List, Dict
from fastapi import UploadFile, File

class UserSignUp(BaseModel):
    first_name: str  # Changed from full_name
    last_name: str   # Added last_name
    username: str
    phone_number: str
    age: int
    email: str
    password: str

class UserLogin(BaseModel):
    username: str  # Can be either username or email
    password: str


class ServiceResponse(BaseModel):
    service_id: int
    service_name: str
    service_description: str

from pydantic import BaseModel

class DentistResponse(BaseModel):
    dentist_id: int
    dentist_name: str
    years_of_experience: int
    dentist_speciality: str
    dentist_clinic: str
    dentist_phone_number: str
    dentist_email: str
    dentist_address: str
    dentist_working_hours: str

class DentistListResponse(BaseModel):
    dentists: List[DentistResponse]

class AppointmentPreferenceCreate(BaseModel):
    user_id: int
    dentist_id: int
    first_name: str  # ✅ Updated field
    last_name: str   # ✅ Updated field
    patient_gender: str
    patient_age: str
    patient_phone_number: str
    patient_email_address: str
    preferred_dates: str
    relation: Optional[str] = None
    special_notes: Optional[str] = None

class AppointmentPreferenceResponse(BaseModel):
    appointment_preference_id: int
    user_id: int
    dentist_id: int
    first_name: str  # ✅ Updated field
    last_name: str   # ✅ Updated field
    patient_gender: str
    patient_age: str
    patient_phone_number: str
    patient_email_address: str
    preferred_dates: str
    relation: Optional[str]
    special_notes: Optional[str]
    file_path: Optional[str] = None
    created_at: datetime

class AppointmentCreate(BaseModel):
    user_id: int
    dentist_id: int

class AppointmentResponse(BaseModel):
    appointment_id: int
    user_id: int
    dentist_id: int
    appointment_date: Optional[str] = ""
    appointment_time: Optional[str] = ""
    appointment_status: str
    created_at: str

class AppointmentResponse(BaseModel):
    appointment_id: int
    user_id: int
    dentist_id: int
    appointment_date: str
    appointment_time: str
    appointment_status: str
    created_at: datetime

class UserAppointmentListResponse(BaseModel):
    appointments: List[AppointmentResponse] 

class DentistServiceResponse(BaseModel):
    service_id: int
    service_name: str
    service_description: str    