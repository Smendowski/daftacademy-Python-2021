from fastapi import APIRouter, Request, Response, status

from pydantic import BaseModel

from models import Person, RegisteredUser, HelloResp
from utils import calculate_day_offset
from datetime import date, timedelta


import hashlib

b_router = APIRouter()

b_router.counter = 0
b_router.id = 0
b_router.patients = []


@b_router.api_route("/method", methods=['GET', 'POST', 'DELETE', 'PUT', 'OPTIONS'])
def handle_method(request: Request, response: Response):
    if request.method == 'POST':
        response.status_code = status.HTTP_201_CREATED
    return {"method": f"{request.method}"}

@b_router.get("/auth")
async def authorize_password(response: Response, password: str = '', password_hash: str = ''):
    if password != '' and password_hash != '':
        hash_checked = hashlib.sha512(password.encode()).hexdigest()
        if password_hash == hash_checked:
            response.status_code = status.HTTP_204_NO_CONTENT
            return    
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return

@b_router.post("/register", response_model=RegisteredUser, status_code=status.HTTP_201_CREATED)
async def register_user(response: Response, person: Person):
    vac_date = date.today() + timedelta(days=calculate_day_offset(person.name, person.surname))
    b_router.id += 1
    patient = RegisteredUser(
        id=b_router.id,
        name=person.name,
        surname=person.surname,
        register_date=date.today().strftime("%Y-%m-%d"), 
        vaccination_date=vac_date.strftime("%Y-%m-%d")
    )

    b_router.patients.append(patient)
    return patient

@b_router.get("/patient/{patient_id}", response_model=RegisteredUser, status_code=status.HTTP_200_OK)
async def get_registered_patient(response: Response, patient_id: int):
	if patient_id < 1:
		response.status_code = status.HTTP_400_BAD_REQUEST
		return
	
	if patient_id not in [patient.id for patient in b_router.patients]:
		response.status_code = status.HTTP_404_NOT_FOUND
		return

	return [patient for patient in b_router.patients if patient.id == patient_id][0]

@b_router.get("/hello/{name}")
def hello_name_view(name: str):
    return f"Hello {name}"

@b_router.get('/counter')
def counter():
    b_router.counter += 1
    return b_router.counter

@b_router.get("/hello/{name}", response_model=HelloResp)
async def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")
