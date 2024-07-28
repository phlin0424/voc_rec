import csv
import re
from io import StringIO
from typing import List

import numpy as np
from bs4 import BeautifulSoup
from scipy.spatial.distance import cosine


def extract_korean(text: str):
    # Define the regex pattern for Korean characters
    korean_pattern = re.compile(r"[\uac00-\ud7a3]+")
    # Find all Korean characters in the text
    korean_text = korean_pattern.findall(text)
    # Join all found Korean parts into a single string
    return " ".join(korean_text)


def extract_audio_path(text: str):
    # Define the regex pattern to match the sound filename inside the brackets
    pattern = r"\[sound:(.*?)\]"
    match = re.search(pattern, text)
    if match:
        # Return the matched group (the filename)
        return match.group(1)
    return None


def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def parse_csv(file_content: str) -> List[dict]:
    csv_reader = csv.DictReader(StringIO(file_content))
    return [row for row in csv_reader]


def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return 1 - cosine(vec1, vec2)


if __name__ == "__main__":
    # test_string = (
    #     "아메리카노 [sound:naver-67b3cdf1-6bdaad9a-5f48a925-a17b5d40-b728cd2d.mp3]"
    # )

    # korean_only = extract_korean(test_string)
    # print(korean_only)

    with open("../data/cardlist_240611.csv", "r") as f:
        contents = f.read()
    card_data_list = parse_csv(contents)
    # print(card_data_list)
    # {'front': '좀', 'back': '少し', 'audio': 'naver_387e5fde-abab-46e8-958c-05ef6ed5eb0c.mp3'}
    print(card_data_list[0]["front"])
