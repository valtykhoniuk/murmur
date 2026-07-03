from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from app.db import get_session, User

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/count")
def users_count(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return {"count": len(users)}