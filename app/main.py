from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from app.auth.router import router as auth_router
from app.db import engine, get_session
from app.models.user import User
from app.seed import seed_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    with Session(engine) as session:
        seed_users(session)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/users/count")
def users_count(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return {"count": len(users)}
