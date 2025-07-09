import httpx
import model
from fastapi import FastAPI, Depends, HTTPException
from database import engine, SessionLocal
from model import Base, UserAuth, AppointmentBook
from sqlalchemy.orm import Session
from schema import UserAuhtentication, UserLogin, AppointUser
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth import *
from fastapi.middleware.cors import CORSMiddleware
import json
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()

ULTRA_INSTANCE_ID = os.getenv("INSTANCE")
ULTRA_TOKEN = os.getenv("TOKEN")
YOUR_WHATSAPP_NUMBER = os.getenv("WHATSAPP")  

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,  
        allow_methods=["*"],     
        allow_headers=["*"],     
)

def getdb():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

@app.post("/signup")
def SignUpUser(usersignup:UserAuhtentication, db:Session = Depends(getdb)):
    checkemail = db.query(UserAuth).filter(UserAuth.email == usersignup.email).first()
    checkusername = db.query(UserAuth).filter(UserAuth.username == usersignup.username).first()
    if checkemail or checkusername:
        raise HTTPException(detail="User Exist Already!", status_code=404)
    hashed_pass = hash_password(usersignup.password)
    saveSignUp = UserAuth(username=usersignup.username ,email=usersignup.email, password=hashed_pass)
    db.add(saveSignUp)
    db.commit()
    db.refresh(saveSignUp)
    return {"message": "User created successfully"}

@app.post("/login")
def LoginUser(userlogin:UserLogin, db:Session = Depends(getdb)):
    user = db.query(UserAuth).filter(UserAuth.email == userlogin.email).first()
    if not user or not verify_password(userlogin.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        token = create_token(user.email)
        return {"message": "Succesfully Login!", "token": token}

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    decoded = verify_token(token)
    if decoded is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return decoded.get("email")  

def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

@app.get("/services")
def get_services():
    return load_json("services.json")

@app.get("/doctors")
def get_doctors():
    return load_json("doctors.json")

@app.post("/userappointment")
def UserAppointmentSubmit(user:AppointUser, email: str = Depends(get_current_user_email), db:Session = Depends(getdb)):
    if not user.email == email:
        return {"message": "User Not Found in Authentication"}
    data = AppointmentBook(**user.model_dump())
    db.add(data)
    db.commit()
    db.refresh(data)
    message = (
        f"New Appointment Booked:\n"
        f"Name: {user.name}\n"
        f"Email: {user.email}\n"
        f"Phone: {user.phone}\n"
        f"Day: {user.day}\n"
        f"Time: {user.time}\n"
        f"Service: {user.service}"
    )

    url = f"https://api.ultramsg.com/{ULTRA_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRA_TOKEN,
        "to": YOUR_WHATSAPP_NUMBER,
        "body": message,
    }

    with httpx.Client() as client:
        client.post(url, data=payload)

    return {"message": "Appointment Booked Successfully"}

@app.post("/isaccept/{email}")
def AcceptedUser(email:str ,db:Session = Depends(getdb)):
    data = db.query(AppointmentBook).filter(AppointmentBook.email == email).first()
    if not data:
        return {"message": "User with this email not found!"}
    data.isaccept = True
    db.commit()
    return {"message": "User accepted Succesfully"}

@app.post("/checkedupdone/{email}")
def AcceptedUser(email:str ,db:Session = Depends(getdb)):
    data = db.query(AppointmentBook).filter(AppointmentBook.email == email).first()
    if not data:
        return {"message": "User with this email not found!"}
    data.checkupdone = True
    db.commit()
    return {"message": "User accepted Succesfully"}

@app.get('/userappointment/{email}')
def getUserData(email:str,db:Session = Depends(getdb)):
    return db.query(AppointmentBook).filter(AppointmentBook.email == email).first()

@app.get('/alldata')
def getAllUserData(db:Session = Depends(getdb)):
    return db.query(AppointmentBook).all()

@app.post("/get_user_appointment")
def GetUserAllAppoint(email:str = Depends(get_current_user_email), db:Session = Depends(getdb)):
    data = db.query(AppointmentBook).filter(AppointmentBook.email == email).all()
    if not data:
        return {"message": "User has no appointment"}
    return data

@app.delete("/delete_user_appointment/{id}")
def DeletingSpecificAppointment(id: int, email: str = Depends(get_current_user_email), db: Session = Depends(getdb)):
    data = db.query(AppointmentBook).filter(AppointmentBook.id == id, AppointmentBook.email == email).first()
    
    if not data:
        raise HTTPException(status_code=404, detail="Appointment not found for this user.")
    
    db.delete(data)
    db.commit()
    
    return {"message": "Appointment deleted successfully"}

@app.get("/verify-token")
def VerifyToken(email: str = Depends(get_current_user_email)):
    return {"message": "Token is valid", "email": email}
