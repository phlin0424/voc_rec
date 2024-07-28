from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DIR_PATH = Path(__file__).resolve().parent.parent


class SettingsEnv(BaseSettings):
    """Environment variables from .env file"""

    deck_name: str
    anki_db_path: Path
    openai_api_key: str
    model_config = SettingsConfigDict(
        env_file=DIR_PATH / ".env", env_file_encoding="utf-8"
    )


class Settings(SettingsEnv):
    """Paths inside container"""

    dir_path: Path = DIR_PATH
    mp3_path: Path = DIR_PATH / "api" / "data"
    anki_db_path_con: Path = DIR_PATH / "api" / "data" / "collection.anki2"


settings = Settings()


if __name__ == "__main__":
    print(DIR_PATH)
    # settings = Settings()
    print(settings.dir_path)
    print(settings.openai_api_key)
    print(settings.deck_name)
    print("anki_db_path:", settings.anki_db_path_con)
