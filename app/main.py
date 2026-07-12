import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.auth.router import router as auth_router
from app.characters.router import router as characters_router
from app.chats.router import router as chats_router
from app.db import engine, get_session, init_db
from app.models.user import User
from app.seed import seed_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(engine) as session:
        seed_users(session)
    yield


app = FastAPI(lifespan=lifespan)

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(characters_router, prefix="/characters", tags=["characters"])
app.include_router(chats_router, prefix="/chats", tags=["chats"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/users/count")
def users_count(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return {"count": len(users)}
