from fastapi import FastAPI
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
    