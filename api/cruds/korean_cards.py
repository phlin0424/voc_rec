import logging
from typing import Dict, List

import numpy as np
from models.anki_cards import AnkiNoteModel
from schemas.anki_note import KoNoteSchema, KoVocSchema
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.embedding_vector import generate_vector
from utils.korean_tools import create_audio, translate_to_jp
from utils.tools import compute_cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def insert_card(
    session: AsyncSession,
    anki_note_create: KoNoteSchema,
) -> AnkiNoteModel:
    """Simply add an Ankicard by filling all the arguments

    Args:
        db (AsyncSession): _description_
        anki_note_create (KoNoteSchema): _description_

    Returns:
        AnkiNoteModel: _description_
    """
    # vector = await generate_vector(anki_note_create.front)

    anki_note = AnkiNoteModel(
        deck_name=anki_note_create.deck_name,
        front=anki_note_create.front,
        back=anki_note_create.back,
        sentence=anki_note_create.sentence,
        translated_sentence=anki_note_create.translated_sentence,
        audio=anki_note_create.audio,
        vector=[0] * 1536,
        back_vector=[0] * 1536,
    )

    session.add(anki_note)
    await session.commit()
    await session.refresh(anki_note)
    return anki_note


async def get_card(session: AsyncSession, front: str) -> AnkiNoteModel:
    result = await session.execute(
        select(AnkiNoteModel).filter(AnkiNoteModel.front == front)
    )
    return result.scalars().first()


async def update_card(
    session: AsyncSession,
    existing_card: AnkiNoteModel,
    anki_note_update: KoVocSchema,
) -> AnkiNoteModel:
    # Generate translated word:
    if anki_note_update.back is None:
        back = translate_to_jp(anki_note_update.front)
    else:
        back = anki_note_update.back

    # Generate Korean audio file
    if anki_note_update.audio is None:
        audio = create_audio(anki_note_update.front)
    else:
        audio = anki_note_update.audio

    # Generate embedding vector
    # DO NOT OVERWRITING THE VECTOR
    # Calculate the vector only when the existing vector stored in db is None
    # (since the vector is dependent on the front word it self)
    vector_flg = True if existing_card.vector is None else False
    # When the vector stored in db is None, the flag got turn on.
    # So the vectorized process going on:
    if vector_flg:
        if anki_note_update.vector is None:
            logger.info(f"Generate vector of {anki_note_update.front}")
            vector = generate_vector(anki_note_update.front)
        else:
            vector = anki_note_update.vector
    else:
        vector = existing_card.vector

    # Back vector
    vector_flg = True if existing_card.back_vector is None else False
    # When the vector stored in db is None, the flag got turn on.
    # So the vectorized process going on:
    if vector_flg:
        if anki_note_update.back_vector is None:
            # If there isn't input value of back vector
            logger.info(f"Generate vector of {anki_note_update.back}")
            vector = generate_vector(anki_note_update.back)
        else:
            vector = anki_note_update.back_vector
    else:
        vector = existing_card.back_vector

    # Update the existing card:
    existing_card.back = back
    existing_card.audio = audio
    existing_card.vector = vector

    session.add(existing_card)
    await session.commit()
    await session.refresh(existing_card)
    return existing_card


async def create_card(
    session: AsyncSession, anki_note_create: KoVocSchema
) -> AnkiNoteModel:
    # Generate translated word:
    if anki_note_create.back is None:
        back = translate_to_jp(anki_note_create.front)
    else:
        back = anki_note_create.back

    # Generate Korean audio file
    if anki_note_create.audio is None:
        audio = create_audio(anki_note_create.front)
    else:
        audio = anki_note_create.audio

    # Generate embedding vector
    if anki_note_create.vector is None:
        vector = generate_vector(anki_note_create.front)
    else:
        vector = anki_note_create.vector

    anki_note = AnkiNoteModel(
        deck_name="korean",
        front=anki_note_create.front,
        back=back,
        sentence="",
        translated_sentence="",
        audio=audio,
        vector=vector,
    )

    # Logging the result
    # logger.info(f"{anki_note_create.front} is added successfully!")

    session.add(anki_note)
    await session.commit()
    await session.refresh(anki_note)
    return anki_note


async def delete_card(session: AsyncSession, front: str) -> bool:
    # Find the card first
    result = await session.execute(
        select(AnkiNoteModel).filter(AnkiNoteModel.front == front)
    )
    card = result.scalars().first()

    if card:
        await session.execute(delete(AnkiNoteModel).where(AnkiNoteModel.id == card.id))
        await session.commit()
        return True
    return False


async def get_all_similarities(
    session: AsyncSession, target_note: AnkiNoteModel
) -> List[Dict[str, str]]:
    result = await session.execute(select(AnkiNoteModel))
    all_cards = result.scalars().all()

    similarities = []
    target_vector = target_note.vector
    for card in all_cards:
        try:
            if card.front != target_note.front:
                # Create the array for the vector of an existing card
                vector = np.array(card.vector)

                # Create the array for the vector of the target card
                similarity = compute_cosine_similarity(
                    vector,
                    target_vector,
                )
                similarities.append({"word": card.front, "similarity": similarity})
        except ValueError:
            logger.warning(
                f"{card.front} is not included in cosine similarity calculation: vector: {vector}",
            )
            continue

    # Sort the similarities array:
    similarities.sort(key=lambda x: x["similarity"], reverse=True)

    # Only return the top 3 words
    return [item for item in similarities[0:3] if item["similarity"] > 0.5]


if __name__ == "__name__":
    print(create_card(session="", anki_note_create=KoVocSchema(front="방탄소년단")))
