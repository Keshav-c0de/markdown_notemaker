from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    account_name: str 
    email: EmailStr

class UserRead(UserBase):
    id: int

class NoteUpdate(BaseModel):
    notes: str

class Notepad(BaseModel):
    id: int
    user_id: int
    time: datetime

class UserCreate(UserBase):
    password: str = Field(...,min_length = 8)

class Token(BaseModel):
    access_token: str
    token_type: str