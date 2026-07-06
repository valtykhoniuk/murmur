from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.deps import get_current_user
from app.characters.schemas import CharacterCreate, CharacterRead, CharacterUpdate
from app.chats.cleanup import delete_character_chats
from app.db import get_session
from app.models.character import Character
from app.models.user import User

router = APIRouter()


def _get_owned_character(
    character_id: int,
    session: Session,
    current_user: User,
) -> Character:
    character = session.get(Character, character_id)
    if not character or character.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.get("", response_model=list[CharacterRead])
def get_characters(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    characters = session.exec(
        select(Character).where(Character.owner_id == current_user.id)
    ).all()
    return characters


@router.post("", response_model=CharacterRead)
def create_character(
    character_data: CharacterCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    existing = session.exec(
        select(Character).where(
            Character.name == character_data.name,
            Character.owner_id == current_user.id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Character already exists")

    character = Character(
        owner_id=current_user.id,
        name=character_data.name,
        persona=character_data.persona,
        start_message=character_data.start_message,
        avatar_url=character_data.avatar_url,
    )
    session.add(character)
    session.commit()
    session.refresh(character)
    return character


@router.get("/{character_id}", response_model=CharacterRead)
def get_character(
    character_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return _get_owned_character(character_id, session, current_user)


@router.put("/{character_id}", response_model=CharacterRead)
def update_character(
    character_id: int,
    body: CharacterUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    character = _get_owned_character(character_id, session, current_user)

    duplicate = session.exec(
        select(Character).where(
            Character.name == body.name,
            Character.owner_id == current_user.id,
            Character.id != character_id,
        )
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="Character name already in use")

    character.name = body.name
    character.persona = body.persona
    character.start_message = body.start_message
    character.avatar_url = body.avatar_url
    session.add(character)
    session.commit()
    session.refresh(character)
    return character


@router.delete("/{character_id}", status_code=204)
def delete_character(
    character_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    character = _get_owned_character(character_id, session, current_user)
    delete_character_chats(session, character.id)
    session.delete(character)
    session.commit()
