from fastapi.testclient import TestClient

from main import app
from models import Person, RegisteredUser
from utils import calculate_day_offset

import sqlite3
import pytest
import json
from collections import namedtuple

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

Credentials = namedtuple("Credentials", ("username", "password"))

@pytest.mark.parametrize("input", [
    {'creds': Credentials(username="4dm1n", password="NotSoSecurePa$$"), 'status': 'ok'},
    {'creds': Credentials(username="4dm1n", password="notsosecurePa$$"), 'status': 'fail'},
    {'creds': Credentials(username="admin", password="NotSoSecurePa$$"), 'status': 'fail'}
    ]
)
def test_session_login_ok(input: dict):
    response = client.post(
        "/login_session", 
        auth=(input['creds'].username, input['creds'].password)
    )

    if input['status'] == 'fail':
        assert response.status_code == 401
    else:
        assert response.status_code == 201
        assert 'session_token' in response.cookies

@pytest.mark.parametrize("input", [
    {'creds': Credentials(username="4dm1n", password="NotSoSecurePa$$"), 'status': 'ok'},
    {'creds': Credentials(username="4dm1n", password="notsosecurePa$$"), 'status': 'fail'},
    {'creds': Credentials(username="admin", password="NotSoSecurePa$$"), 'status': 'fail'}
    ]
)
def test_token_login_ok(input: dict):
    response = client.post(
        "/login_token", 
        auth=(input['creds'].username, input['creds'].password)
    )

    if input['status'] == 'fail':
        assert response.status_code == 401
    else:
        assert response.status_code == 201
        assert 'token' in response.json()

# @pytest.mark.parametrize("fmt", ["", "json", "html"])
# def test_welcome_session_ok(fmt: str):
#     log = client.post('/login_session', auth=("4dm1n", "NotSoSecurePa$$"))
#     response = client.get(f'/welcome_session?format={fmt}', cookies=log.cookies)

#     assert response.status_code == 200

#     if fmt == "html":
#         assert response.headers["content-type"].split(';')[0] == "text/html"
#         assert response.text.__contains__('<h1>Welcome!</h1>')
#     elif fmt == "json":
#         assert response.headers["content-type"].split(';')[0] == "application/json"
#         assert response.json() == {"message": "Welcome!"}
#     else:
#         assert response.headers["content-type"].split(';')[0] == "text/plain"
#         assert response.text == "Welcome!"

def test_welcome_session_none():
    client.cookies.clear()
    response = client.get('/welcome_session')
    assert response.status_code == 401

@pytest.mark.parametrize("fail", ["empty", "wrong"])
def test_welcome_session_fail(fail: str):
    log = client.post('/login_session', auth=("4dm1n", "NotSoSecurePa$$"))

    if fail == 'wrong':
        log.cookies['session_token'] = log.cookies['session_token'][::-1]
    elif fail == "empty":
        log.cookies['session_token'] = ""

    response = client.get('/welcome_session', cookies=log.cookies)

    assert response.status_code == 401

# @pytest.mark.parametrize("fmt", ["", "json", "html"])
# def test_welcome_token_ok(fmt: str):
#     log = client.post('/login_token', auth=("4dm1n", "NotSoSecurePa$$"))
#     response = client.get(f'/welcome_token?token={log.json()["token"]}&format={fmt}')

#     assert response.status_code == 200

#     if fmt == "html":
#         assert response.headers["content-type"].split(';')[0] == "text/html"
#         assert response.text.__contains__('<h1>Welcome!</h1>')
#     elif fmt == "json":
#         assert response.headers["content-type"].split(';')[0] == "application/json"
#         assert response.json() == {"message": "Welcome!"}
#     else:
#         assert response.headers["content-type"].split(';')[0] == "text/plain"
#         assert response.text == "Welcome!"

@pytest.mark.parametrize("fail", [None, "empty", "wrong"])
def test_welcome_token_fail(fail: str):
    token = ""

    if fail == "wrong":
        token = "xd"
    elif fail == None:
        response = client.get(f'/welcome_token')

    response = client.get(f'/welcome_token?token={token}')

    assert response.status_code == 401

def test_redirect_session():
    log = client.post('/login_session', auth=("4dm1n", "NotSoSecurePa$$"))
    resp_del = client.delete('/logout_session', allow_redirects=False)

    assert resp_del.status_code == 302
    assert resp_del.headers['location']

    resp_red = client.get(resp_del.headers['location'])

    assert resp_red.status_code == 200

    resp_wel = client.get('/welcome_session', cookies=log.cookies)

    assert resp_wel.status_code == 401

def test_redirect_token():
    log = client.post('/login_token', auth=("4dm1n", "NotSoSecurePa$$"))
    resp_del = client.delete(f'/logout_token?token={log.json()["token"]}', allow_redirects=False)

    assert resp_del.status_code == 302
    assert resp_del.headers['location']

    resp_red = client.get(resp_del.headers['location'])

    assert resp_red.status_code == 200

    resp_wel = client.get(f'/welcome_token?token={log.json()["token"]}')

    assert resp_wel.status_code == 401

def test_mutliclient_session():
    log1 = client.post('/login_session', auth=("4dm1n", "NotSoSecurePa$$"))
    log2 = client.post('/login_session', auth=("4dm1n", "NotSoSecurePa$$"))
    log3 = client.post('/login_session', auth=("4dm1n", "NotSoSecurePa$$"))
    log4 = client.post('/login_session', auth=("4dm1n", "NotSoSecurePa$$"))

    client.cookies.clear()
    resp_wel1 = client.get('/welcome_session', cookies=log1.cookies)

    assert resp_wel1.status_code == 401

def test_multiclient_token():
    log1 = client.post('/login_token', auth=("4dm1n", "NotSoSecurePa$$"))
    log2 = client.post('/login_token', auth=("4dm1n", "NotSoSecurePa$$"))
    log3 = client.post('/login_token', auth=("4dm1n", "NotSoSecurePa$$"))
    log4 = client.post('/login_token', auth=("4dm1n", "NotSoSecurePa$$"))

    resp_wel1 = client.get(f'/welcome_token?token={log1.json()["token"]}')

    assert resp_wel1.status_code == 401

app.db_connection = sqlite3.connect("northwind.db")
app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific 

def test_categories_database():
    response = client.get("/categories")
    cursor = app.db_connection.cursor()
    categories = cursor.execute("SELECT CategoryID, CategoryName FROM Categories").fetchall()
    assert response.status_code == 200
    assert response.json() == {"categories": [{"id": x[0], "name": x[1]} for x in categories]}

# def test_customers_database():
#     response = client.get("/customers")
#     cursor = app.db_connection.cursor()
#     customers = cursor.execute("SELECT * FROM Customers").fetchall()
#     assert response.status_code == 200
#     assert response.json() == {"customers": customers}


@pytest.mark.parametrize("product_id", [1, 2, 3])
def test_product_ok(product_id: int):
    response = client.get(f"/products/{product_id}")
    app.db_connection.row_factory = sqlite3.Row
    product = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = :product_id",
        {'product_id': product_id}).fetchone()
    assert response.status_code == 200
    assert response.json() == {"id": product[0], "name": product[1]} 

def test_product_fail():
    cursor = app.db_connection.cursor()
    num_of_products = cursor.execute("SELECT COUNT(*) FROM Products").fetchone()[0]
    app.db_connection.row_factory = sqlite3.Row
    response = client.get(f"/products/{num_of_products+1}")
    assert response.status_code == 404
