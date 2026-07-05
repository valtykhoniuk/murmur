from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.deps import get_current_user
from app.auth.schemas import LoginRequest, TokenResponse, UserRead
from app.auth.security import create_access_token, verify_password
from app.config import DEMO_EMAIL
from app.db import get_session
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid account")

    token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=token)


@router.post("/demo", response_model=TokenResponse)
def demo_login(session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == DEMO_EMAIL)).first()
    if not user:
        raise HTTPException(status_code=503, detail="Demo user is not configured")

    token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )
