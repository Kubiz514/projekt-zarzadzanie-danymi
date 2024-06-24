from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.username = user_update.username
        db_user.hashed_password = pwd_context.hash(user_update.password)
        db.commit()
        db.refresh(db_user)
    return db_user

# Device CRUD operations
def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()

def get_device_by_serial_number(db: Session, serial_number: str):
    return db.query(models.Device).filter(models.Device.serial_number == serial_number).first()

def get_devices(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Device).offset(skip).limit(limit).all()

def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = models.Device(name=device.name, serial_number=device.serial_number)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
    return db_device

def update_device(db: Session, device_id: int, device_update: schemas.DeviceCreate):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if db_device:
        db_device.name = device_update.name
        db_device.serial_number = device_update.serial_number
        db.commit()
        db.refresh(db_device)
    return db_device

# DeviceReading CRUD operations
def get_device_reading(db: Session, reading_id: int):
    return db.query(models.DeviceReading).filter(models.DeviceReading.id == reading_id).first()

def get_device_readings(db: Session, device_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.DeviceReading).filter(models.DeviceReading.device_id == device_id).offset(skip).limit(limit).all()

def create_device_reading(db: Session, reading: schemas.DeviceReadingCreate):
    db_reading = models.DeviceReading(device_id=reading.device_id, reading_date=reading.reading_date, value=reading.value)
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def delete_device_reading(db: Session, reading_id: int):
    db_reading = db.query(models.DeviceReading).filter(models.DeviceReading.id == reading_id).first()
    if db_reading:
        db.delete(db_reading)
        db.commit()
    return db_reading

def update_device_reading(db: Session, reading_id: int, reading_update: schemas.DeviceReadingCreate):
    db_reading = db.query(models.DeviceReading).filter(models.DeviceReading.id == reading_id).first()
    if db_reading:
        db_reading.device_id = reading_update.device_id
        db_reading.reading_date = reading_update.reading_date
        db_reading.value = reading_update.value
        db.commit()
        db.refresh(db_reading)
    return db_reading
