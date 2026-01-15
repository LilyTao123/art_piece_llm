import hashlib
import re

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text

def artwork_key(title, artist, year):
    return f"{normalize(title)}|{normalize(artist)}|{year}"


def generate_artwork_id(title, artist, year):
    key = artwork_key(title, artist, year)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
