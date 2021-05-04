from fastapi import APIRouter, Request, APIRouter, Request, Response, status, Depends, Query, HTTPException

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from utils import check_credentials
from models import Token, HelloResp, Message

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

@e_router.get("/welcome_session")
def welcome_session(request: Request, format: str = ""):
	if ("session_token" not in request.cookies.keys()) or (request.cookies["session_token"] is None) or (request.cookies["session_token"] not in e_router.sessions):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Not authorized"
		)

	if format == 'json':
		return Message(
			message="Welcome!"
		)
	elif format == 'html':
		return templates.TemplateResponse(
			"welcome.html.j2",
			{"request": request}
		)
	else:
		return Response(
			content="Welcome!", 
			media_type="text/plain"
		)


@e_router.get("/welcome_token")
def welcome_token(request: Request, token: str = "", format: str = ""):
	if (not token) or (token == "") or (token not in e_router.tokens):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Not authorized"
		)

	if format == 'json':
		return Message(
			message="Welcome!"
		)
	elif format == 'html':
		return templates.TemplateResponse(
			"welcome.html.j2",
			{"request": request}
		)
	else:
		return Response(
			content="Welcome!",
			media_type="text/plain"
        )

@e_router.delete('/logout_session', status_code=status.HTTP_302_FOUND)
def logout_session(request: Request, format: str = ""):
	if ("session_token" not in request.cookies.keys()) or (request.cookies["session_token"] is None) or (request.cookies["session_token"] not in e_router.sessions):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Not authorized"
		)
	
	e_router.sessions.remove(request.cookies["session_token"])

	return RedirectResponse(
		url=f"/logged_out?format={format}", 
		status_code=302
)

@e_router.delete('/logout_token', status_code=status.HTTP_302_FOUND)
def logout_token(request: Request, token: str = "", format: str = ""):
	if (not token) or (token == "") or (token not in e_router.tokens):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Not authorized"
		)

	e_router.tokens.remove(token)

	return RedirectResponse(
		url=f"/logged_out?format={format}", 
		status_code=302
	)


@e_router.api_route('/logged_out', status_code=status.HTTP_200_OK, methods=['GET', 'DELETE'])
def logged_out(request: Request, format: str = ""):

	if format == 'json':
		return Message(
			message="Logged out!"
		)
	elif format == 'html':
		return templates.TemplateResponse(
			"logged_out.html.j2",
			{"request": request}
		)
	else:
		return Response(
			content="Logged out!",
			media_type="text/plain"
		)
