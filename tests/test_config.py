from pathlib import Path

from config import settings


def test_env_existing(root_dir_path: Path):
    """Test the existence of .env file"""
    env_path = root_dir_path / ".env"
    assert env_path.is_file()


def test_settings_env(root_dir_path: Path):
    # Read the env file directly from .env file
    env_path = root_dir_path / ".env"
    with open(env_path) as f:
        texts = f.readlines()
    env_values = {}
    for text in texts:
        text = text.replace("\n", "")
        key, value = text.split("=")[0], text.split("=")[1]
        env_values[key.lower()] = value

    # Compare with the values loaded in settings
    assert env_values["deck_name"] == settings.deck_name
    assert env_values["anki_db_path"] == settings.anki_db_path.__str__()
    assert env_values["openai_api_key"] == settings.openai_api_key

    # Test that if Path conversion doing well:
    assert isinstance(settings.anki_db_path_con, Path)

    # Test that if the .anki2 would be mapped really exist:
    assert settings.anki_db_path_con.is_file()
