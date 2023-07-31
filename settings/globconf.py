from pathlib import Path


BASE_DIR: Path = Path(__file__).resolve().parent.parent

DB_DIR: Path = BASE_DIR / 'database'

DB_NAME: str = str(DB_DIR / 'db.vacancies')

MAX_AGE: int = 7

HH_REQUEST_DELAY: float | int = 0.2
