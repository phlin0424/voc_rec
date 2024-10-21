from typing import Dict, List, Optional

from config import settings
from langdetect import detect
from pydantic import BaseModel, ConfigDict, model_validator

"""
Schemas for inserting a new card with manually specifying all the fields

router: 
    /insert_korean_card

"""


class AnkiNoteModel(BaseModel):
    """Basic Anki note model"""

    deck_name: str = settings.deck_name
    front: str
    back: str = None
    sentence: str | None = None
    translated_sentence: Optional[str] = None
    audio: Optional[str] = None
    tags: Optional[List[str]] = []
    description: Optional[str] = None


class KoNoteSchema(AnkiNoteModel):
    """Anki note for korean vocabulary"""

    frontLang: str = "ko"  # Default expected language for the 'front' field

    @model_validator(mode="after")
    def check_languages(self):
        # Detect languages of the `front` field
        detected_front_lang = detect(self.front)

        # Validate detected languages against expected languages
        if detected_front_lang != self.frontLang:
            raise ValueError(
                f"Expected language for 'front' field is '{self.frontLang}', but detected '{detected_front_lang}'."
            )
        return self


class KoNoteResponseSchema(KoNoteSchema):
    """Anki note for korean vocabulary post response"""

    id: int

    model_config = ConfigDict(from_attributes=True)


"""
Schemas for creating a new card with only front word is necessary. 
The fields without input will be filled in automatically.

router: 
    /create_korean_card
    /upload_csv
"""


class KoVocSchema(BaseModel):
    front: str
    back: Optional[str] = None
    vector: Optional[List[float]] = None
    back_vector: Optional[List[float]] = None
    audio: Optional[str] = None

    @model_validator(mode="after")
    def check_languages(self):
        # Detect languages of the `front` field
        detected_front_lang = detect(self.front)

        # Validate detected languages against expected languages
        if detected_front_lang != "ko":
            raise ValueError(
                f"Expected language for 'front' field is 'Korean', but detected '{detected_front_lang}'."
            )
        return self


class KoVocResponseSchema(KoVocSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


"""
KoRecomWordResponseSchema: 
retrieve words that are similar to a specified word 

An example input: 
KoRecomWordResponseSchema.recommendation
[
    {'word': '저게', 'similarity': 0.730678141117096}, 
    {'word': '저건', 'similarity': 0.7266739173725906}, 
    {'word': '저 사람', 'similarity': 0.6876391172409058}
]
    
"""


class KoRecomWordResponseSchema(BaseModel):
    recommendation: List[Dict[str, str | float]] | None = None


if __name__ == "__main__":
    # To see if the variables loaded properly:
    print(settings.openai_api_key)
    print(settings.deck_name)

    print(
        KoNoteSchema(
            front="방탄소년단",
            back="BTS",
            tags=["korean"],
        )
    )
    print(
        KoNoteResponseSchema(
            id=1,
            front="방탄소년단",
            back="BTS",
            tags=["korean"],
        )
    )

    print(KoVocSchema(front="방탄소년단"))
    card = {
        "front": "좀",
        "back": "少し",
        "audio": "naver_387e5fde-abab-46e8-958c-05ef6ed5eb0c.mp3",
    }
    print(KoNoteSchema(**card))

    recommendation = [
        {"word": "저게", "similarity": 0.730678141117096},
        {"word": "저건", "similarity": 0.7266739173725906},
        {"word": "저 사람", "similarity": 0.6876391172409058},
    ]
    print(KoRecomWordResponseSchema(recommendation=recommendation))
