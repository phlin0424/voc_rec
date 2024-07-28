import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from config import settings
from utils.tools import extract_audio_path, extract_korean, remove_html_tags


def invoke(action: str, **params: Dict[str, Any]) -> Dict[str, Any]:
    request = {
        "action": action,
        "version": 6,
        "params": params,
    }

    response = requests.post(
        settings.connector_url,
        json.dumps(request),
    )

    if "error" in response and response["error"] is not None:
        raise Exception(response["error"])
    else:
        return response.json()["result"]


def extract_all_cards(deck_name: str = settings.deck_name) -> List[Dict[str, str]]:
    """A function to retrieve the cards in my Anki DB.

    Args:
        deck_name (str, optional): _description_. Defaults to settings.deck_name.

    Returns:
        List[Dict[str, str]]: A list of retrieved cards which are in Dict type.
    """
    # Retrieve the notes from the deck in anki db
    note_ids: List[int] = invoke("findNotes", query=f"deck:{deck_name}")
    notes_infor: List[Dict[str, Any]] = invoke("notesInfo", notes=note_ids)

    # Fill the retrieved nots into AnkiNoteModel, preparing for updating our DB
    cards = []
    for note in notes_infor:
        # Iterate each fields of a given card:
        for item in note["fields"].values():
            if item["order"] == 0:
                front_txt = item["value"]
            elif item["order"] == 1:
                back_txt = item["value"]

        created_card = {
            "front": remove_html_tags(extract_korean(front_txt)),
            "back": remove_html_tags(back_txt),
            "audio": extract_audio_path(front_txt),
            "deck_name": deck_name,
        }

        if front_txt != "":
            cards.append(created_card)
    return cards


def create_csv(output_path: Path = settings.mp3_path, filename: str = None) -> Path:
    if isinstance(output_path, str):
        output_path = Path(output_path)

    currentdate = datetime.now().strftime("%y%m%d")
    cards = extract_all_cards()
    with open(output_path / f"cardlist_{currentdate}.csv", "w") as f:
        f.write("front,back,audio")
        for card in cards:
            f.write(
                "\n{},{},{}".format(
                    remove_html_tags(card["front"]),
                    remove_html_tags(card["back"]),
                    card["audio"],
                ),
            )

    if filename is None:
        filename = f"cardlist_{currentdate}.csv"

    return output_path / filename


def extract_all_cards_from_anki2() -> list[tuple[Any]]:
    """Extract all the flashcards in .anki2 db by a specified deck name.

    Returns:
        list[dict[str, str]]: _description_
    """
    # Path to the mounted .anki2 file
    anki_db_path = settings.anki_db_path_con
    deck_name = settings.deck_name

    # Connect to the Anki SQLite database
    conn = sqlite3.connect(anki_db_path)
    cursor = conn.cursor()

    # Get the deck id of the specified deck_name in settings
    cursor.execute(
        f"SELECT id, name FROM decks WHERE name = '{deck_name}' COLLATE NOCASE"
    )
    deck_info = cursor.fetchall()
    deck_id = deck_info[0][0]

    # Execute a query to fetch all cards
    with open(settings.dir_path / "api" / "sql" / "get_korean_deck_data.sql") as f:
        query = f.read()

    query = query.format(deck_id=deck_id)
    cursor.execute(query)

    # Fetch all results
    cards = cursor.fetchall()

    return cards


def split_field(fetch_values: tuple[str]) -> dict[str, str]:
    """split the results that fetched from the db.

    Args:
        fetch_values (tuple[str]): each item fetched from .anki2
    """
    values = fetch_values[0].split("\x1f")
    front = values[0]
    back = values[1]

    return {"front": front, "back": back}


def prase_card(card: dict[str, str]) -> dict[str, str]:
    """Clean the html tag and extract the audio information from the card directly fetched from db
    Args:
        card (dict[str, str]): which contains two fields:
        {front: str, back: str}

    Returns:
        dict[str, str]: {
            front: str,
            back: str,
            audio: str
        }
    """
    front_txt = card["front"]
    back_txt = card["back"]
    deck_name = settings.deck_name
    created_card = {
        "front": remove_html_tags(extract_korean(front_txt)),
        "back": remove_html_tags(back_txt),
        "audio": extract_audio_path(front_txt),
        "deck_name": deck_name,
    }
    return created_card


if __name__ == "__main__":
    # print(f"extract all the card from deck: {settings.deck_name}")
    # cards = extract_all_cards()
    # print(cards[0:10])

    # Testing outputting mp3
    # create_csv()
    cards = extract_all_cards_from_anki2()
    results = []
    for card in cards:
        results.append(split_field(card))
    for result in results:
        print(prase_card(result))
