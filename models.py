from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Boolean, Table, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(Text, nullable=False)
    user_name = Column(Text, nullable=False, unique=True)
    user_phone_number = Column(Text, nullable=False)
    user_email = Column(Text, unique=True)
    user_age = Column(Integer, nullable=False)
    user_password = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="user")
    preferences = relationship("AppointmentPreference", back_populates="user")

class Dentist(Base):
    __tablename__ = "dentist"
    
    dentist_id = Column(Integer, primary_key=True, index=True)
    dentist_name = Column(Text, nullable=False)
    years_of_experience = Column(Integer)
    dentist_speciality = Column(Text)
    dentist_clinic = Column(Text, nullable=False)
    dentist_phone_number = Column(Text, nullable=False)
    dentist_email = Column(Text, unique=True)
    dentist_address = Column(Text, nullable=False)
    dentist_working_hours = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="dentist")
    services = relationship("DentistService", back_populates="dentist")
    preferences = relationship("AppointmentPreference", back_populates="dentist")

class Appointment(Base):
    __tablename__ = "appointment"
    
    appointment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    dentist_id = Column(Integer, ForeignKey("dentist.dentist_id"), nullable=False)
    appointment_date = Column(Text)
    appointment_time = Column(Text)
    appointment_status = Column(Text, nullable=False)
    appointment_created = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="appointments")
    dentist = relationship("Dentist", back_populates="appointments")

class Service(Base):
    __tablename__ = "service"
    
    service_id = Column(Integer, primary_key=True, index=True)
    service_name = Column(Text, nullable=False)
    service_description = Column(Text)
    
    dentist_services = relationship("DentistService", back_populates="service")

class DentistService(Base):
    __tablename__ = "dentist_service"
    
    dentist_service_id = Column(Integer, primary_key=True, index=True)
    dentist_id = Column(Integer, ForeignKey("dentist.dentist_id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service.service_id"), nullable=False)
    
    dentist = relationship("Dentist", back_populates="services")
    service = relationship("Service", back_populates="dentist_services")

class AppointmentPreference(Base):
    __tablename__ = "appointment_preference"
    
    appointment_preference_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    dentist_id = Column(Integer, ForeignKey("dentist.dentist_id"), nullable=False)
    patient_name = Column(Text, nullable=False)
    patient_gender = Column(Text, nullable=False)
    patient_age = Column(Text, nullable=False)
    patient_phone_number = Column(Text, nullable=False)
    patient_email_address = Column(Text, nullable=False)
    preferred_dates = Column(Text, nullable=False)
    relation = Column(Text)
    special_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="preferences")
    dentist = relationship("Dentist", back_populates="preferences")
