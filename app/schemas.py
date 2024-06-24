# Remove this import if not used elsewhere
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class DeviceBase(BaseModel):
    name: str
    serial_number: str

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int

    class Config:
        orm_mode = True

class DeviceReadingBase(BaseModel):
    device_id: int
    reading_date: datetime
    value: float

class DeviceReadingCreate(DeviceReadingBase):
    pass

class DeviceReading(DeviceReadingBase):
    id: int

    class Config:
        orm_mode = True
