from pydantic import BaseModel, EmailStr

class UserAuhtentication(BaseModel):
    username:str
    email:EmailStr
    password:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class AppointUser(BaseModel):
    name:str
    email:EmailStr
    phone:str
    day:str
    time:str
    service:str
    isaccept:bool
    checkupdone:bool