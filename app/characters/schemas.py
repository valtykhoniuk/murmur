from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str
    persona: str
    start_message: str
    avatar_url: str = ""


class CharacterRead(BaseModel):
    id: int
    owner_id: int
    name: str
    persona: str
    start_message: str
    avatar_url: str
