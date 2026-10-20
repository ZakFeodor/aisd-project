from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='auth.html'
    )

@app.get("/auth_check", response_class=HTMLResponse)
def auth_check(login: str, password: str, request: Request):
    if login != "admin" and password != "1234":
        return templates.TemplateResponse(
        request=request,
        name='auth_error.html'
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name='main_page.html'
        )


@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='register.html'
    )

@app.get("/main_page", response_class=HTMLResponse)
def login(login: str, password: str, name:str, request: Request):
    return templates.TemplateResponse(
        request=request,
        name='main_page.html'
    )
