from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None

class User(UserBase):
    id: int
    devices: List['Device'] = []

    class Config:
        orm_mode = True

class DeviceBase(BaseModel):
    name: str
    serial_number: str

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    name: Optional[str] = None
    serial_number: Optional[str] = None

class Device(DeviceBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class DeviceReadingBase(BaseModel):
    device_id: int
    reading_date: datetime
    value: float

class DeviceReadingCreate(BaseModel):
    reading_date: datetime
    value: float
    
class DeviceReadingUpdate(BaseModel):
    reading_date: Optional[datetime] = None
    value: Optional[float] = None

class DeviceReading(DeviceReadingBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
