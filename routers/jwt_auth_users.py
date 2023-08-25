from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 10
SECRET = "f145eff8bfe8d0d5674e217dbcfb7abaeadfeffca68e57dd5e6a94eb907282cd"

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str


users_db = {
    "carlitos": {
        "username": "carlitos1",
        "full_name": "carlitos gomez",
        "email": "carlitos@gmail.com",
        "disabled": False,
        "password": "$2a$12$C/6V6AvuYMoIrO8VSMbcxuYsTY3q3Iefg8fkZvP1OpVJyWMvUkEoG",
    },
    "mauricio": {
        "username": "mauricio",
        "full_name": "Mauricio gomez",
        "email": "Mauricio@gmail.com",
        "disabled": False,
        "password": "$2a$12$wfJo3weO.PdONesATuMlleVEBipxZoz/KVS2/YEZLkyQjBvg9eqZW",
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
            status_code=400, 
            detail="Credenciales de autenticacion invalidas", headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception
          
    except JWTError:
        raise exception
    
    return search_user(username)
        

async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=400, 
            detail="Usuario inactivo")
    
    return user

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=400, 
            detail="El usuario no es correcto")
    
    user = search_user_db(form.username)    

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=400, 
            detail="La contraseña no es correcta")
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)

    access_token = {"sub": user.username, "exp": expire}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user