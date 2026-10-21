from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from model import User, engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select

def get_session():
    with SessionLocal() as session:
        yield session


class UserModel(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=30
    )
    login: str = Field(
        min_length=1,
        max_length=20
    )
    password: str = Field(
        min_length=8,
        max_length=30
    )
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='auth.html'
    )

@app.get("/auth_check", response_class=HTMLResponse)
def auth_check(login: str, password: str, request: Request, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.login == login, User.password == password))
    if user:
        return templates.TemplateResponse(
        request=request,
        name='auth_error.html'
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name='main_page.html',
            context={'name': user.name}
        )


@app.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='register.html'
    )

@app.get("/main_page", response_class=HTMLResponse)
def login(UserLocal: UserModel,  request: Request, session: Session = Depends(get_session)):
    existing = session.scalar(select(User).where(User.login == UserLocal.login))
    if existing:
        raise HTTPException(400, "Логин занят")
    user = User(
        name = UserLocal.name,
        login = UserLocal.login,
        password = UserLocal.password
    )
    session.add(user)
    session.commit()
    return templates.TemplateResponse(
        request=request,
        name='main_page.html'
    )
