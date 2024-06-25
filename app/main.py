from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from io import BytesIO
from . import models, schemas, crud, auth, pdf_generator
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My FastAPI Application",
    description="This is a sample FastAPI application with JWT authentication and CRUD operations.",
    version="1.0.0",
    contact={
        "name": "Your Name",
        "url": "http://your-website.com",
        "email": "your-email@domain.com",
    },
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

# User endpoints...

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=list[schemas.User], tags=["Users"])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(auth.get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.delete("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)

@app.put("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user_update=user)

# Device endpoints
@app.post("/devices/", response_model=schemas.Device, tags=["Devices"])
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    db_device = crud.get_device_by_serial_number(db, serial_number=device.serial_number)
    if db_device:
        raise HTTPException(status_code=400, detail="Device with this serial number already registered")
    return crud.create_device(db=db, device=device, user_id=current_user.id)

@app.get("/devices/{device_id}", response_model=schemas.Device, tags=["Devices"])
def read_device(device_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@app.get("/devices/", response_model=list[schemas.Device], tags=["Devices"])
def read_devices(skip: int = 0, limit: int = 10, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    devices = crud.get_devices(db, user_id=current_user.id, skip=skip, limit=limit)
    return devices

@app.delete("/devices/{device_id}", response_model=schemas.Device, tags=["Devices"])
def delete_device(device_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return crud.delete_device(db=db, device_id=device_id)

@app.put("/devices/{device_id}", response_model=schemas.Device, tags=["Devices"])
def update_device(device_id: int, device: schemas.DeviceCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return crud.update_device(db=db, device_id=device_id, device_update=device)

# DeviceReading endpoints
@app.post("/device_readings/", response_model=schemas.DeviceReading, tags=["Device Readings"])
def create_device_reading(reading: schemas.DeviceReadingCreate, db: Session = Depends(get_db)):
    return crud.create_device_reading(db=db, reading=reading)

@app.get("/device_readings/{reading_id}", tags=["Device Readings"], response_model=schemas.DeviceReading)
def read_device_reading(reading_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    reading = crud.get_device_reading(db, reading_id=reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    return reading

@app.get("/device_readings/", response_model=list[schemas.DeviceReading], tags=["Device Readings"])
def read_device_readings(device_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: schemas.User = Depends(auth.get_current_active_user)):
    readings = crud.get_device_readings(db, device_id=device_id, skip=skip, limit=limit, user_id=current_user.id)
    return readings

@app.get("/device_readings_pdf", tags=["Device Readings"], response_class=Response)
def generate_device_readings_pdf_endpoint(device_id: int = None, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), current_user: schemas.User = Depends(auth.get_current_active_user)):
    readings = crud.get_device_readings(db, device_id=device_id, user_id=current_user.id, skip=0, limit=100)  # Fetching all readings for device_id
    pdf_buffer = pdf_generator.generate_device_readings_pdf(readings)
    response = Response(content=pdf_buffer.getvalue(), media_type="application/pdf")
    response.headers["Content-Disposition"] = 'attachment; filename="device_readings.pdf"'
    return response