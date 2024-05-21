import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError, PyJWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

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
    "juanfher": {
        "username": "juanfher",
        "full_name": "Juan Fernández",
        "email": "juanfpcr6@gmail.com",
        "disabled": False,
        "password": "$2a$12$pOQpL2db9pIOezkmJ1IoCe04R3P3vV3EttHfkc2DzkF0/VadWk9ju"
    },
    "juanfher2": {
        "username": "juanfher2",
        "full_name": "Juan Fernández 2",
        "email": "juanfpcr62@gmail.com",
        "disabled": True,
        "password": "$2a$12$35jUzWuSrFepXpXisdSjI.6/geHFuJYl1.G8nAKfIjXuf/HiYQvyq"
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas", 
            headers={"WWW-Authenticate": "Bearer"})

    try: 
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception
        
    except PyJWTError:
        raise exception
    
    return search_user(username)
        

async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario incactivo")
    
    return user
    

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = user_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    
    user = search_user_db(form.username)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    access_token = {"sub":user.username, 
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}


@router.get("/user/me")
async def me(user: User = Depends(current_user)):
    return user
