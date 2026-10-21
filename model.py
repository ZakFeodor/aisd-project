from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://user:1@localhost/UsersDB"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int]  = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    login: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(30))



