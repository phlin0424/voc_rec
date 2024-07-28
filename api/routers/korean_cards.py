from typing import Dict, List

import aiofiles
import utils.db_sync as sync
from config import settings
from cruds.korean_cards import (
    create_card,
    delete_card,
    get_all_similarities,
    get_card,
    insert_card,
    update_card,
)
from db import get_db
from fastapi import APIRouter, Depends, HTTPException
from schemas.anki_note import (
    KoNoteResponseSchema,
    KoNoteSchema,
    KoRecomWordResponseSchema,
    KoVocResponseSchema,
    KoVocSchema,
)
from sqlalchemy.ext.asyncio import AsyncSession
from utils.tools import parse_csv

router = APIRouter()


@router.post("/insert_korean_card", response_model=KoNoteResponseSchema)
async def insert_korean_card(
    korean_note: KoNoteSchema, session: AsyncSession = Depends(get_db)
):
    anki_note = await insert_card(session, korean_note)
    return anki_note


@router.get("/get_korean_card", response_model=KoVocResponseSchema)
async def get_korean_card(front: str, session: AsyncSession = Depends(get_db)):
    card = await get_card(session=session, front=front)
    if card:
        return card
    raise HTTPException(status_code=404, detail="card not found")


@router.post("/create_korean_card", response_model=KoVocResponseSchema)
async def create_korean_card(
    korean_note: KoVocSchema, session: AsyncSession = Depends(get_db)
):
    existing_card = await get_card(session=session, front=korean_note.front)
    if existing_card:
        updated_anki_note = await update_card(
            session=session,
            existing_card=existing_card,
            anki_note_update=korean_note,
        )
        return updated_anki_note
    else:
        anki_note = await create_card(session, korean_note)
        return anki_note


@router.delete("/delete_korean_card", response_model=Dict[str, str])
async def delete_korean_card(front: str, session: AsyncSession = Depends(get_db)):
    success = await delete_card(session=session, front=front)
    if success:
        return {"detail": f"card: {front} deleted successfully"}
    raise HTTPException(status_code=404, detail="Card not found")


@router.post("/upload_csv", response_model=List[Dict[str, str]])
async def upload_csv(csv_name: str, session: AsyncSession = Depends(get_db)):
    # Validate the csv filename
    if not csv_name.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )

    # reading and writing files asynchronously,
    # User must specify the csv file that is located under api/data
    async with aiofiles.open(settings.mp3_path / csv_name) as f:
        contents = await f.read()

    # Parse the text read from the csv file into dict
    card_data_list = parse_csv(contents)

    # Record the error message:
    response_list = []

    # Upload the card one by one
    for card in card_data_list:
        try:
            # Create the input based on the predefined schema
            korean_note = KoVocSchema(**card)

            existing_card = await get_card(session=session, front=card["front"])

            if existing_card:
                updated_anki_note = await update_card(
                    session=session,
                    existing_card=existing_card,
                    anki_note_update=korean_note,
                )
            else:
                anki_note = await create_card(session, korean_note)
        except Exception as e:
            response_list.append({"front": card["front"], "error": e})

    return response_list


@router.post("/sync", response_model=List[Dict[str, str]])
async def sync_anki(session: AsyncSession = Depends(get_db)):
    """A router to directly pulled cards from .anki2

    Args:
        session (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Returns:
        _type_: _description_
    """
    # Fetch all the cards in .anki2 DB
    all_cards = sync.extract_all_cards_from_anki2()
    card_data_list = []
    for card in all_cards:
        card_data_list.append(
            sync.prase_card(
                sync.split_field(card),
            )
        )

    # Record the error message:
    response_list = []

    # Upload the card one by one
    for card in card_data_list:
        try:
            # Create the input based on the predefined schema
            korean_note = KoVocSchema(**card)

            existing_card = await get_card(session=session, front=card["front"])

            if existing_card:
                updated_anki_note = await update_card(
                    session=session,
                    existing_card=existing_card,
                    anki_note_update=korean_note,
                )
            else:
                anki_note = await create_card(session, korean_note)
        except Exception as e:
            response_list.append({"front": card["front"], "error": str(e)})

    if not response_list:
        return [{"msg": "all the cards are synchronized successfully."}]
    return response_list


@router.get(
    "/find_similar",
    response_model=KoRecomWordResponseSchema,
)
async def find_similar(word: str, session: AsyncSession = Depends(get_db)):
    existing_card = await get_card(session=session, front=word)
    if existing_card is None:
        raise HTTPException(status_code=404, detail="card not found")

    similarities = await get_all_similarities(
        session=session,
        target_note=existing_card,
    )

    if len(similarities) == 0:
        raise HTTPException(status_code=405, detail="No similar word found")

    return KoRecomWordResponseSchema(recommendation=similarities)
