from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    createdAt: datetime
    updatedAt: datetime

class UserProfileResponse(BaseModel):
    user: UserResponse
    message: str
    status: int

class TokenResponse(BaseModel):
    token: str
    user: UserResponse
    message: str
    status: int 