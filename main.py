import sqlite3
from fastapi import FastAPI, status
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
    pass