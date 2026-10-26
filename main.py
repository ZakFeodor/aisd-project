from fastapi import FastAPI, Request, Depends, UploadFile, Form, File
import os
import uuid
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from model import User, engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select
import hashlib
from typing import Optional


def get_session():
    with SessionLocal() as session:
        yield session


def get_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class UserModel(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    login: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=8, max_length=30)


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request=request, name='auth.html')


@app.post("/auth_check")
def auth_check(
        request: Request,
        login: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)
):
    user = session.scalar(select(User).where(User.login == login).limit(1))
    if not user or user.password != get_hash(password):
        return templates.TemplateResponse(request=request, name='auth_error.html')

    return RedirectResponse(url=f"/main_page/{user.name}", status_code=303)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name='register.html')


@app.post("/register")
def register_user(
        request: Request,
        name: str = Form(...),
        login: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)
):
    new_user = User(name=name, login=login, password=get_hash(password))
    session.add(new_user)
    session.commit()
    return RedirectResponse(url=f"/main_page/{new_user.name}", status_code=303)


@app.get("/main_page", response_class=HTMLResponse)
@app.get("/main_page/{name}", response_class=HTMLResponse)
def main_page(request: Request, name: Optional[str] = None):
    if name is None:
        name = "Гость"
    return templates.TemplateResponse(
        request=request,
        name='main_page.html',
        context={'name': name}
    )


@app.post("/main_page/{name}/upload")
def upload_file(name: str, file: UploadFile = File(...)):
    user_dir = os.path.join("uploads", name)
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return RedirectResponse(url=f"/main_page/{name}", status_code=303)


@app.get("/main_page/{name}/get_hashmap", response_class=HTMLResponse)
def hashmap(request: Request, name: str):
    if os.path.exists(f"uploads/{name}/olympics_history_1896_2024_FullSchema.csv"):
        return templates.TemplateResponse(
            request=request,
            name='hashmap.html',
            context={'name': name}
        )

    return RedirectResponse(url=f"/main_page/{name}", status_code=303)


@app.get("/main_page/{name}/get_segment_tree", response_class=HTMLResponse)
def segment_tree(request: Request, name: str):
    if os.path.exists(f"uploads/{name}/olympics_history_1896_2024_FullSchema.csv"):
        return templates.TemplateResponse(
            request=request,
            name='segment_tree.html',
            context={'name': name}
        )

    return RedirectResponse(url=f"/main_page/{name}", status_code=303)