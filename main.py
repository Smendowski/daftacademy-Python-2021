import sqlite3
from fastapi import FastAPI, status, Response, HTTPException
from typing import Optional
from fastapi_route_log.log_request import LoggingRoute
from routers import basic_endpoints, extended_endpoints

app = FastAPI()
app.router.route_class = LoggingRoute

app.include_router(
    basic_endpoints.b_router,
    tags=["basic_endpoints"]
)

app.include_router(
    extended_endpoints.e_router,
    tags=["extended_endpoints"]
)


@app.get("/")
def root():
	return {"message": "Hello world!"}


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific 

@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()

@app.get("/categories", status_code=status.HTTP_200_OK)
async def categories():
    cursor = app.db_connection.cursor()
    categories = cursor.execute("SELECT CategoryID, CategoryName FROM Categories").fetchall()
    return {"categories": [{"id": x[0], "name": x[1]} for x in categories]}

@app.get("/customers", status_code=status.HTTP_200_OK)
async def customers():
    cursor = app.db_connection.cursor()
    customers = cursor.execute(
        "SELECT CustomerID, COALESCE(CompanyName, ''), \
        (COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || COALESCE(City, '') || ' ' || COALESCE(Country, '')) \
        FROM Customers ORDER BY UPPER(CustomerID)"
        ).fetchall()
    return {"customers": [{"id": x[0], "name": x[1], "full_address": x[2]} for x in customers]}

@app.get("/products/{product_id}", status_code=status.HTTP_200_OK)
async def single_product(response: Response, product_id: int):
    app.db_connection.row_factory = sqlite3.Row
    product = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = :product_id",
        {'product_id': product_id}).fetchone()
    if product:
        return {"id": product[0], "name": product[1]}    
    response.status_code = status.HTTP_404_NOT_FOUND

@app.get("/employees", status_code=status.HTTP_200_OK)
async def employees(response: Response, limit: Optional[int] = None, offset: Optional[int] = None, order: Optional[str] = ""):
    query = "SELECT EmployeeID, LastName, FirstName, City From Employees"
    assotiations = {"last_name": "LastName", "first_name": "FirstName", "city": "City"}
    if order in assotiations.keys():
        query += f" ORDER BY {assotiations[order]}"
    elif order == "":
        query += f" ORDER BY EmployeeID"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified wrong order"
        )
    if limit != 0 and isinstance(limit, int):
        query += f" LIMIT {limit}"
    if offset != 0 and isinstance(offset, int):
        query += f" OFFSET {offset}"
    employees = app.db_connection.execute(query).fetchall()      
    if employees:
        return {"employees": [{"id": x[0], "last_name": x[1], "first_name": x[2], "city": x[3]} for x in employees]}
