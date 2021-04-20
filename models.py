from pydantic import BaseModel


class HelloResp(BaseModel):
    msg: str


class Person(BaseModel):
    name: str
    surname: str


class RegisteredUser(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str
