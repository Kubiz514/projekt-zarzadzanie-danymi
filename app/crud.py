from sqlalchemy.orm import Session
from . import models, schemas, auth
from passlib.context import CryptContext
from datetime import datetime
from app.auth import get_current_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

# Device CRUD operations
def get_device(db: Session, device_id: int, user_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id, models.Device.owner_id == user_id).first()

def get_device_by_serial_number(db: Session, serial_number: str):
    return db.query(models.Device).filter(models.Device.serial_number == serial_number).first()

def get_devices(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Device).filter(models.Device.owner_id == user_id).offset(skip).limit(limit).all()

def create_device(db: Session, device: schemas.DeviceCreate, user_id: int):
    db_device = models.Device(**device.dict(), owner_id=user_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int, user_id: int):
    db_device = get_device(db, device_id, user_id)
    if not db_device:
        return None
    db.delete(db_device)
    db.commit()
    return db_device

def update_device(db: Session, device: schemas.DeviceUpdate, device_id: int, user_id: int):
    db_device = get_device(db, device_id, user_id)
    if not db_device:
        return None
    for key, value in device.dict(exclude_unset=True).items():
        setattr(db_device, key, value)
    db.commit()
    db.refresh(db_device)
    return db_device

# DeviceReading CRUD operations
def get_device_readings(db: Session, device_id: int, user_id: int, skip: int = 0, limit: int = 100):
    device = get_device(db, device_id=device_id, user_id=user_id)
    if not device:
        return []
    return db.query(models.DeviceReading).filter(models.DeviceReading.device_id == device_id).offset(skip).limit(limit).all()

def get_device_by_id_and_user(db: Session, device_id: int, user_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id, models.Device.owner_id == user_id).first()

def create_device_reading(db: Session, reading: schemas.DeviceReadingCreate, device_id: int, user_id: int):
    db_reading = models.DeviceReading(**reading.dict(), device_id=device_id)
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def update_device_reading(db: Session, reading_id: int, reading: schemas.DeviceReadingUpdate, user_id: int, device_id: int):
    device = get_device(db, device_id=device_id, user_id=user_id)
    if not device:
        return None
    db_reading = db.query(models.DeviceReading).filter(models.DeviceReading.id == reading_id, models.DeviceReading.device_id == device_id).first()
    if not db_reading:
        return None
    for key, value in reading.dict(exclude_unset=True).items():
        setattr(db_reading, key, value)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def delete_device_reading(db: Session, reading_id: int, device_id: int, user_id: int):
    device = get_device(db, device_id=device_id, user_id=user_id)
    if not device:
        return None
    db_reading = db.query(models.DeviceReading).filter(models.DeviceReading.id == reading_id, models.DeviceReading.device_id == device_id).first()
    if not db_reading:
        return None
    db.delete(db_reading)
    db.commit()
    return db_reading