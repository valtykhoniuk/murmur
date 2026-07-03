from sqlmodel import Session, select

from app.auth.security import hash_password
from app.config import (
    DEMO_EMAIL,
    DEMO_PASSWORD,
    FRIEND_EMAIL,
    FRIEND_PASSWORD,
    OWNER_EMAIL,
    OWNER_PASSWORD,
)
from app.models.user import User


def seed_users(session: Session) -> None:

    candidates: list[tuple[str | None, str | None, str]] = [
        (OWNER_EMAIL, OWNER_PASSWORD, "owner"),
        (FRIEND_EMAIL, FRIEND_PASSWORD, "friend"),
        (DEMO_EMAIL, DEMO_PASSWORD, "public"),
    ]

    for email, password, role in candidates:
        if not email or not password:
            continue

        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            continue

        session.add(
            User(
                email=email,
                password_hash=hash_password(password),
                role=role,
            )
        )

    session.commit()


if __name__ == "__main__":
    from app.db import engine

    with Session(engine) as session:
        seed_users(session)
    print("Seed done.")
