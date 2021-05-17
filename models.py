from pydantic import BaseModel, Field, PositiveInt, constr


class HelloResp(BaseModel):
    msg: str


class Message(BaseModel):
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


class PatientIdentifier(BaseModel):
    id: int


class Token(BaseModel):
	token: str
    

class Category(BaseModel):
    name: str


# ORM MODELS

class Shipper(BaseModel):
    ShipperID: PositiveInt
    CompanyName: constr(max_length=40)
    Phone: constr(max_length=24)

    class Config:
        orm_mode = True


class Supplier(BaseModel):
    SupplierID: PositiveInt
    CompanyName: constr(max_length=40)

    class Config:
        orm_mode = True


class CategoryData(BaseModel):
    CategoryID: PositiveInt
    CategoryName: str

    class Config:
        orm_mode = True 


class SupplierProduct(BaseModel):
    ProductID: PositiveInt
    ProductName: str
    Category: CategoryData
    Discontinued: int

    class Config:
        orm_mode = True 
