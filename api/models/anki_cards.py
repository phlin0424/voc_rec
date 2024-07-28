from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Create a table Model which inherit from Base
class AnkiNoteModel(Base):
    """Create a table based on the specified model as follows:"""

    __tablename__ = "anki_cards"

    id = Column(Integer, primary_key=True)
    deck_name = Column(String, index=True)
    front = Column(String, nullable=False)
    back = Column(String)
    sentence = Column(String)
    translated_sentence = Column(String)
    audio = Column(String)
    vector = Column(Vector(dim=1536))  # Example vector column with dimension 300
