from fastapi import FastAPI, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from io import BytesIO
from . import models, schemas, crud, auth, pdf_generator
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IoT Manager",
    description="IoT Manager is an app created for a university project.",
    version="1.0.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# User endpoints

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me", response_model=schemas.User, tags=["Users"])
def read_user_me(db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User, tags=["Users"])
def update_user_me(user: schemas.UserUpdate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    updated_user = crud.update_user(db, user_id=current_user.id, user=user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@app.delete("/users/me", response_model=schemas.User, tags=["Users"])
def delete_user_me(db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    deleted_user = crud.delete_user(db, user_id=current_user.id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user

@app.get("/users/", response_model=list[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(auth.get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# Device endpoints
@app.post("/devices/", response_model=schemas.Device, tags=["Devices"])
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    db_device = crud.get_device_by_serial_number(db, serial_number=device.serial_number)
    if db_device:
        raise HTTPException(status_code=400, detail="Device with this serial number already registered")
    return crud.create_device(db=db, device=device, user_id=current_user.id)

@app.get("/devices/{device_id}", response_model=schemas.Device, tags=["Devices"])
def read_device(device_id: int, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    device = crud.get_device(db, device_id=device_id, user_id=current_user.id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.get("/devices/", response_model=list[schemas.Device], tags=["Devices"])
def read_devices(skip: int = 0, limit: int = 10, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    devices = crud.get_devices(db, user_id=current_user.id, skip=skip, limit=limit)
    return devices

@app.delete("/devices/{device_id}", response_model=schemas.Device, tags=["Devices"])
def delete_device(device_id: int, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    deleted_device = crud.delete_device(db, device_id=device_id, user_id=current_user.id)
    if not deleted_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return deleted_device

@app.put("/devices/{device_id}", response_model=schemas.Device, tags=["Devices"])
def update_device(device_id: int, device: schemas.DeviceUpdate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    updated_device = crud.update_device(db, device=device, device_id=device_id, user_id=current_user.id)
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device

# DeviceReading endpoints
@app.get("/device_readings/", response_model=list[schemas.DeviceReading], tags=["Device Readings"])
def read_device_readings(device_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    device_readings = crud.get_device_readings(db, device_id=device_id, user_id=current_user.id, skip=skip, limit=limit)
    return device_readings

@app.post("/device_readings/", response_model=schemas.DeviceReading, tags=["Device Readings"])
def create_device_reading(device_id: int, reading: schemas.DeviceReadingCreate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    db_reading = crud.create_device_reading(db=db, reading=reading, device_id=device_id, user_id=current_user.id)
    if not db_reading:
        raise HTTPException(status_code=400, detail="Cannot create reading for this device")
    return db_reading

@app.put("/device_readings/{reading_id}", response_model=schemas.DeviceReading, tags=["Device Readings"])
def update_device_reading(reading_id: int, device_id: int, reading: schemas.DeviceReadingUpdate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    updated_reading = crud.update_device_reading(db=db, reading_id=reading_id, reading=reading, device_id=device_id, user_id=current_user.id)
    if not updated_reading:
        raise HTTPException(status_code=404, detail="Device reading not found or not authorized to update")
    return updated_reading

@app.get("/device_readings_pdf", tags=["Device Readings"], response_class=Response)
def generate_device_readings_pdf_endpoint(device_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: schemas.User = Depends(auth.get_current_active_user)):
    readings = crud.get_device_readings(db, device_id=device_id, user_id=current_user.id, skip=0, limit=100)
    pdf_buffer = pdf_generator.generate_device_readings_pdf(readings)
    response = Response(content=pdf_buffer.getvalue(), media_type="application/pdf")
    response.headers["Content-Disposition"] = 'attachment; filename="device_readings.pdf"'
    return response