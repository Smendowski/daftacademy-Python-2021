from fastapi import APIRouter, Request, APIRouter, Request, Response, status, Depends, Query, HTTPException

from fastapi.templating import Jinja2Templates

from utils import check_credentials
from models import Token, HelloResp

from datetime import date

e_router = APIRouter()
e_router.tokens = []
e_router.sessions = []

templates = Jinja2Templates(directory="templates")

@e_router.get("/hello")
def send_hello(request: Request):
    return templates.TemplateResponse(
        "hello.html.j2",
        {"request": request, "today_date": date.today()}
    )

@e_router.post("/login_session", status_code=status.HTTP_201_CREATED)
def login_session(response: Response, session_token: str = Depends(check_credentials)):

    if len(e_router.sessions) >= 3:
        e_router.sessions.pop(0)
    e_router.sessions.append(session_token)

    response.set_cookie(key="session_token", value=session_token)
    return {"message": "Successfully Authorized"}

@e_router.post("/login_token", status_code=status.HTTP_201_CREATED)
def login_token(token: str = Depends(check_credentials)):
	
	if len(e_router.tokens) >= 3:
		e_router.tokens.pop(0)
	e_router.tokens.append(token)
	
	return Token(
		token=token
	)

