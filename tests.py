from fastapi.testclient import TestClient

from main import app
from models import Person, RegisteredUser
from utils import calculate_day_offset

import pytest
import json
from datetime import date, timedelta

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world!"}

@pytest.mark.parametrize("method", ['GET', 'POST', 'DELETE', 'PUT', 'OPTIONS'])
def test_http_method(method: str):
    response = client.request(method=method, url='/method')
    assert response.status_code == 200 if method != 'POST' else response.status_code == 201
    assert response.json() == {"method": f"{method}"}

def test_password():
    response = client.get(f"/auth?password=haslo&password_hash=013c6889f799cd986a735118e1888727d1435f7f623d05d58c61bf2cd8b49ac90105e5786ceaabd62bbc27336153d0d316b2d13b36804080c44aa6198c533215")
    assert response.status_code == 204
    response = client.get(f"/auth?password=haslo&password_hash=f34ad4b3ae1e2cf33092e2abb60dc0444781c15d0e2e9ecdb37e4b14176a0164027b05900e09fa0f61a1882e0b89fbfa5dcfcc9765dd2ca4377e2c794837e091")
    assert response.status_code == 401
    response = client.get(f"/auth")
    assert response.status_code == 401

@pytest.mark.parametrize("name", ["Zenek", "Marek", "Alojzy Niezdąży"])
def test_hello_name(name: str):
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.text == f'"Hello {name}"'

def test_counter():
    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "1"
    response = client.get(f"/counter")
    assert response.status_code == 200
    assert response.text == "2"

registered_patients = {}

@pytest.mark.parametrize("new_user", [Person(name='Jan', surname='Kowalski'), Person(name='Jacek', surname='Warzyńczak')])
def test_registartion(new_user: Person):
    response = client.post(url='/register', data=new_user.json())
    assert response.status_code == 201 
    assert type(response.json()['id']) == int 
    assert response.json()['name'] == new_user.name
    assert response.json()['surname'] == new_user.surname
    assert response.json()['register_date'] == date.today().strftime(format="%Y-%m-%d")
    vac_date = date.today() + timedelta(days=calculate_day_offset(new_user.name, new_user.surname))
    assert response.json()['vaccination_date'] == vac_date.strftime(format="%Y-%m-%d")
    registered_patients[response.json()['id']] = response.json()

@pytest.mark.parametrize("patient_id", [1, 2])
def test_getting_patients_good_identifier(patient_id):
    response = client.get(f"patient/{patient_id}")
    assert response.status_code == 200
    assert response.json() == registered_patients[patient_id]

@pytest.mark.parametrize("patient_id", registered_patients.keys())
def test_getting_patients_bad_identifier(patient_id):
    response = client.get(f"patient/{patient_id}")
    assert response.status_code == 400

@pytest.mark.parametrize("patient_id", [1000, 2000])
def test_getting_patients_patinet_not_identified(patient_id):
    response = client.get(f"patient/{patient_id}")
    assert response.status_code == 404

def test_hello_html_template():
    response = client.get("/hello")

    today = date.today()

    assert response.headers["content-type"].split(';')[0] == "text/html"
    assert response.text.__contains__(f'<h1>Hello! Today date is {today.strftime("%Y-%m-%d")}</h1>')
