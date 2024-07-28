import uuid
from pathlib import Path
from typing import Union

from config import settings
from deep_translator import GoogleTranslator
from navertts import NaverTTS

MP3_PATH = settings.mp3_path


def translate_to_jp(front_text) -> Union[str]:
    # Initialize the translator with target language and optional source language
    translator = GoogleTranslator(source="ko", target="ja")

    # Translate text (translated from Korean)
    try:
        translation = translator.translate(front_text)
        return translation
    except Exception as e:
        print(f"An error occurred: {e}")


def create_audio(text: str, path: Union[Path, str] = MP3_PATH) -> str:
    """Create an audio file (.mp3) for the input korean word. Based on Naver TTS API.

    Args:
        text (str): Korean word.
        path (Union[Path, str], optional): _description_. Defaults to MP3_PATH.

    Returns:
        Union[Path, str]: The path of the output audio file.
    """
    # texts = [note.front for note in self._anki_notes]
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    tts = NaverTTS(text)
    audio_filename = path / f"naver_{uuid.uuid4()}.mp3"
    tts.save(audio_filename)
    return str(audio_filename)


if __name__ == "__main__":
    print(translate_to_jp("안녕하세요?"))
    print(translate_to_jp("아내"))
    print(translate_to_jp("회사원"))
    print(translate_to_jp("학교"))
    print(translate_to_jp("일본대사관"))
    # print(create_audio("안녕하세요?"))

    # print(create_audio("아메리카노"))
