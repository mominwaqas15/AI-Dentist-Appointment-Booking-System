from pydantic import BaseModel
from datetime import datetime
from pydantic import Field
from typing import Optional, List, Dict
from fastapi import UploadFile, File

class UserSignUp(BaseModel):
    full_name: str
    username: str
    phone_number: str
    age: int
    email: str
    password: str



