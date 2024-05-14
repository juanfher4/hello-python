from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Inicia el servidor: uvicorn users:app --reload

# Entidad user
class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [User(id=1, name="Brais", surname="Moure", url="https://moure.dev", age=35),
              User(id=2, name="Moure", surname="Dev", url="https://mouredev.com", age=35),
              User(id=3, name="Juan", surname="Fer", url="https://juanfer.com", age=19)]

@app.get("/usersjson")
async def usersjson():
    return [{"name": "Brais", "surname": "Moure", "url": "https://moure.dev", "age": 35},
            {"name": "Moure", "surname": "Dev", "url": "https://mouredev.com", "age": 35},
            {"name": "Juan", "surname": "Fer", "url": "https://juanfer.com", "age": 19}]

@app.get("/users")
async def users():
    return users_list


@app.get("/users/{id}")
async def user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    return list(users)
