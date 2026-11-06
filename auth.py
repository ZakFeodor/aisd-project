import secrets
import hashlib
from fastapi.responses import Response, RedirectResponse
from fastapi import Request
from model import User, engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import select

def get_session():
    with SessionLocal() as session:
        yield session

SESSIONS = {}

def require_user(request: Request):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/", status_code=302)
    return user

def check_credentials(login: str, session: Session) -> bool:
    correct_user = session.scalar(select(User).where(User.login == login))
    if correct_user:
        return True
    return False

def check_password(login: str, password: str, session: Session) -> bool:
    user = session.scalar(select(User).where(User.login == login))
    if user and user.password == hash_password(password):
        return True
    return False

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(request: Request):
    session_id = request.cookies.get('session_id')
    if not session_id:
        return None
    return SESSIONS.get(session_id)

def create_session(response: Response, login: str):
    session_id = secrets.token_hex(16)
    SESSIONS[session_id] = login
    response.set_cookie("session_id", session_id)
    return session_id


def login_user(login: str, password: str, session: Session):
    new_user = User(login=login, password=hash_password(password))
    session.add(new_user)
    session.commit()

def logout_user(response: Response, request: Request, session: Session):
    login = request.cookies.get("session_id")
    user = session.scalar(select(User).where(User.login == login))
    if user:
        session.delete(user)
        session.commit()
    session_id = request.cookies.get('session_id')
    if session_id is not None:
        SESSIONS.pop(session_id, None)
    response.delete_cookie("session_id")
