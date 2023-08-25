from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel


router = APIRouter(tags=["users"], responses={404: {"description": "Not found"}})

# uvicorn users:app --reload

# Entidad user
class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [
    User(id=1,name="Jefry", surname="Hernandez", url="www.jeff.com", age=24),
    User(id=2,name="Laura", surname="Hernandez", url="www.Lau.com", age=22),
]

@router.get("/users/")
async def users():
    return users_list

# Path 
@router.get("/user/{id}")
async def user(id: int):
    return search_user(id)

@router.post("/user/", status_code=status.HTTP_201_CREATED)
async def user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe")
    
    users_list.append(user)
    return user

@router.put('/user/')
async def user(user: User):    
    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            found = True

    if not found:
        return {"error": "No se ha actualizado el usuario"}
    
    return user

@router.delete('/user/{id}')
async def user(id: int):
    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]
            found = True

    if not found:
        return {"error": "No se ha eliminado el usuario"}

def search_user(id: int):
    user = filter(lambda user: user.id == id, users_list)
    try:
        return list(user)[0]
    except:
        return {"error": "No se ha encontrado el usuario"}