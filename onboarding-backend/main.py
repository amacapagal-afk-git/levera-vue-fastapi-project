from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
import model
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from schemas import UserCreate, UserUpdate

app = FastAPI()
model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: db_dependency):
    db_user = db.query(model.User).filter(model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/")
async def create_user(user: UserCreate, db: db_dependency):
    db_user = model.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserCreate, db: db_dependency):
    db_user = db.query(model.User).filter(model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(model.User).filter(model.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}