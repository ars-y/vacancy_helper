from pathlib import Path


BASE_DIR: Path = Path(__file__).resolve().parent

DB_DIR: Path = BASE_DIR / 'database'

DB_NAME: str = str(DB_DIR / 'db.vacancies')

MAX_AGE: int = 7

HH_REQUEST_DELAY: float | int = 0.2

TAG_PATTERN: str = '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});'

URL_PATTERN: str = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
