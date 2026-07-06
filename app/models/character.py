from sqlmodel import Field, SQLModel

class Character(SQLModel, table=True):
    __tablename__ = "characters"

    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="users.id", index=True)
    name: str
    persona: str
    start_message: str
    avatar_url: str
