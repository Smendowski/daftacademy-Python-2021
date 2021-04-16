from fastapi import FastAPI, Request, Response, status

from pydantic import BaseModel

import hashlib

app = FastAPI()
app.counter = 0


class HelloResp(BaseModel):
    msg: str


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
