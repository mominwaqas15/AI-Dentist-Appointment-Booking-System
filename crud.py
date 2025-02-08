from sqlalchemy.orm import Session
from models import User
from datetime import datetime
import schemas

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