from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import  AsyncSession
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from app.schema import Notepad, UserRead ,UserCreate ,Token, NoteUpdate
from app.auth import create_access_token, hash_password, verify_password, verify_access_token
from app.config import settings
from app.user import get_current_user
from app.db import Note, get_async_session , create_db_and_tables, User 
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan= lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", status_code=201)
async def register_user(
    user_data: UserCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        account_name=user_data.account_name,
        email=user_data.email,
        password=hashed_pwd  
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/api/User/token")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                    session: AsyncSession = Depends(get_async_session)):
    '''try:'''
    result = await session.execute(select(User).where(User.email== form_data.username))
    user= result.scalars().first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code = 401, detail= "Incorrect password or email")

    access_token_expires = timedelta(minutes= settings.access_token_expire_minutes)
    access_token = create_access_token(data = {"sub":str(user.id)}, expire_delta= access_token_expires)
    return Token(access_token = access_token, token_type = "bearer")

    '''except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")'''
    
@app.get("/User/me", response_model=UserRead)
async def read_users_me(
    current_user_id : Annotated[User, Depends(get_current_user)],session: AsyncSession = Depends(get_async_session)): 
    result = await session.execute(select(User).where(User.id == int(current_user_id)))
    current_user_info = result.scalars().first()
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user_info

@app.get("/view")
async def show_notes(user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Note).order_by(Note.time.desc()))
    notes = result.scalars().all()
    return notes

@app.patch("/edit/{note_id}")
async def edit_note(note_id : str,
                    update_data : NoteUpdate, 
                    user: User = Depends(get_current_user),
                    session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.get(Note, int(note_id))
        if not result:
            raise HTTPException(status_code=404, detail="No result")
        result.note = update_data.notes
        await session.commit()
        return result
    except Exception as e:
        raise HTTPException(status_code= e, detail= "Not found")
    

@app.put("/create")
async def create_note(
    user: User = Depends(get_current_user),
    note_content: str = Form(...),
    session: AsyncSession = Depends(get_async_session)):
    try:
        created_note = Note(
        note= note_content,
        user_id= int(user))

        session.add(created_note)
        await session.commit()
        await session.refresh(created_note)
        return created_note

    except Exception as e:
        raise HTTPException(status_code = 500, detail = {e})


@app.delete("/remove/{note_id}")
async def  delete_note(note_id: int,user: User = Depends(get_current_user),session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(Note).where(Note.id== note_id))
        removed_note = result.scalars().first()

        if not removed_note:
            raise HTTPException(status_code= 404,detail = "Not found")

    except Exception as e:
        raise HTTPException(status_code = 500, detail = {e})        

    await session.delete(removed_note)
    await session.commit()

    return {"success":True, "message": "note had been removed"}
