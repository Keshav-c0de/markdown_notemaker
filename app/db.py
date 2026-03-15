import os
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship , mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import String, ForeignKey, DateTime, Text
from datetime import datetime
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL= os.getenv("DATABASE_URL")

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "login_info"
    id: Mapped[int] = mapped_column(primary_key= True)
    account_name: Mapped[str] = mapped_column(String(100), nullable = False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable = False)
    password: Mapped[str] = mapped_column(String(100), nullable = False)

    notes = relationship(argument= "Note", back_populates="login_info")

class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(primary_key= True)
    user_id: Mapped[int] = mapped_column(ForeignKey("login_info.id"), nullable = False)
    note: Mapped[str] = mapped_column(Text)
    time: Mapped[datetime] = mapped_column(server_default= func.now())

    login_info:Mapped["User"] = relationship(back_populates="notes")



engine= create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit= False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    async with async_session_maker() as session:
        yield session
        