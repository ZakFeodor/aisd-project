from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from model import User, engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select
import hashlib

def get_session():
    with SessionLocal() as session:
        yield session

def get_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


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
    user = session.scalar(select(User).where(User.login == login).limit(1))
    if not user or (user and user.password != get_hash(password)):
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

@app.post("/main_page",  response_class=HTMLResponse)
def login(
    request: Request,
    name: str = Form(min_length=1, max_length=30),
    login: str = Form(min_length=1, max_length=20),
    password: str = Form(min_length=5, max_length=30),
    session: Session = Depends(get_session),
):

    user = User(
        name=name,
        login=login,
        password=get_hash(password)
    )
    session.add(user)
    session.commit()
    return templates.TemplateResponse(
        request=request,
        name='main_page.html',
        context={'name': user.name}
    )

@app.post("/main_page/{name}/upload", response_class=HTMLResponse):
def upload_file(name, file, request: Request):
    return templates.TemplateResponse(
        request=request,
        name='file_accepted.html',
    )

@app.get("/main_page/{name}/get_hashmap", response_class=HTMLResponse)
def hashmap(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='hashmap.html'
    )

@app.get("/main_page/{name}/get_segment_tree", response_class=HTMLResponse)
def segment_tree(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='segment_tree.html'
    )