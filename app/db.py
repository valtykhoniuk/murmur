from sqlmodel import SQLModel, create_engine, Session, Field
from datetime import datetime
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
def get_session():
    with Session(engine) as session:
        yield session

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str

SQLModel.metadata.create_all(engine)


