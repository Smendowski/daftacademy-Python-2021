from fastapi import FastAPI, Request, Response, status

from pydantic import BaseModel

from models import Person, RegisteredUser, HelloResp
from utils import calculate_day_offset
from datetime import date, timedelta

import hashlib

app = FastAPI()
app.counter = 0
app.id = 0
app.patients = []


@app.get("/")
def root():
	return {"message": "Hello world!"}

@app.api_route("/method", methods=['GET', 'POST', 'DELETE', 'PUT', 'OPTIONS'])
def handle_method(request: Request, response: Response):
    if request.method == 'POST':
        response.status_code = status.HTTP_201_CREATED
    return {"method": f"{request.method}"}

@app.get("/auth")
async def authorize_password(response: Response, password: str = '', password_hash: str = ''):
    if password != '' and password_hash != '':
        hash_checked = hashlib.sha512(password.encode()).hexdigest()
        if password_hash == hash_checked:
            response.status_code = status.HTTP_204_NO_CONTENT
            return    
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return

@app.post("/register", response_model=RegisteredUser, status_code=status.HTTP_201_CREATED)
async def register_user(response: Response, person: Person):
    vac_date = date.today() + timedelta(days=calculate_day_offset(person.name, person.surname))
    app.id += 1
    patient = RegisteredUser(
        id=app.id,
        name=person.name,
        surname=person.surname,
        register_date=date.today().strftime("%Y-%m-%d"), 
        vaccination_date=vac_date.strftime("%Y-%m-%d")
    )

    app.patients.append(patient)
    return patient

@app.get("/hello/{name}")
def hello_name_view(name: str):
    return f"Hello {name}"

@app.get('/counter')
def counter():
    app.counter += 1
    return app.counter

@app.get("/hello/{name}", response_model=HelloResp)
async def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")
