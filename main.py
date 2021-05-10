import sqlite3
from fastapi import FastAPI, status, Response, HTTPException
from typing import Optional
from fastapi_route_log.log_request import LoggingRoute
from routers import basic_endpoints, extended_endpoints
from models import Category

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
        print("Wejscie do keys")
        query += f" ORDER BY {assotiations[order]}"
    elif order == "":
        query += f" ORDER BY EmployeeID"
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    if limit != 0 and isinstance(limit, int):
        query += f" LIMIT {limit}"
    if offset != 0 and isinstance(offset, int):
        query += f" OFFSET {offset}"
    employees = app.db_connection.execute(query).fetchall()      
    if employees:
       return {"employees": [{"id": x[0], "last_name": x[1], "first_name": x[2], "city": x[3]} for x in employees]}

@app.get("/products_extended", status_code=status.HTTP_200_OK)
async def products_extended():
    cursor = app.db_connection.cursor()
    products_extended = cursor.execute(
        """
        SELECT 
	        p.ProductID, p.ProductName,
	        (SELECT c.CategoryName FROM Categories AS c WHERE c.CategoryID = p.CategoryID) AS category,
	        (SELECT s.CompanyName FROM Suppliers AS s WHERE s.SupplierID = p.SupplierID) AS supplier
        FROM Products AS p 
        ORDER BY p.ProductID;
        """
    ).fetchall()
    return {"products_extended": [{"id": x[0], "name": x[1], "category": x[2], "supplier": x[3]} for x in products_extended]}

@app.get("/products/{id}/orders", status_code=status.HTTP_200_OK)
async def products_orders(response: Response, id: int):
    if not isinstance(id, int):
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    app.db_connection.row_factory = sqlite3.Row
    product_orders = app.db_connection.execute(
        """
        SELECT 
	        od.OrderId,
	        (SELECT c.CompanyName FROM Customers AS c WHERE c.CustomerID = o.CustomerID) AS customer,
	        od.Quantity AS quantity,
	        ROUND(((od.UnitPrice * od.Quantity) - (od.Discount * (od.Quantity * od.UnitPrice))), 2) AS total_price
        FROM 'Order Details' AS od
        JOIN Orders AS o ON o.OrderID = od.OrderId
        JOIN Products AS p ON od.ProductID = p.ProductID 
        WHERE od.ProductID = :pid;
        """,
        {"pid": id}
    )
    if product_orders:
        return {"orders": [{"id": x[0], "customer": x[1], "quantity": x[2], "total_price": x[3]} for x in product_orders]}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return

# @app.post("/categories", status_code=status.HTTP_201_CREATED)
# async def create_category(new_category=Category):
#     cursor = app.db_connection.cursor()
#     cursor.row_factory = sqlite3.Row
#     data = cursor.execute("INSERT INTO Categories(CategoryName) VALUES (:name)", {"name": new_category.name})
#     app.db_connection.commit()
#     return {"id": data.lastrowid , "name": new_category.name}
