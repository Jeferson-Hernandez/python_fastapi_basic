from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

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
        "password": "123456",
    },
    "mauricio": {
        "username": "mauricio",
        "full_name": "Mauricio gomez",
        "email": "Mauricio@gmail.com",
        "disabled": False,
        "password": "1234567",
    },
    "luis": {
        "username": "luis2",
        "full_name": "luis gomez",
        "email": "luis@gmail.com",
        "disabled": False,
        "password": "12345678",
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])
    
async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(
            status_code=400, 
            detail="Credenciales de autenticacion invalidas", headers={"WWW-Authenticate": "Bearer"})
    
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
    if not form.password == user.password:
        raise HTTPException(
            status_code=400, 
            detail="La contraseña no es correcta")
    
    return {"access_token": user.username, "token_type": "bearer"}

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user