import os
import shelve

from settings.globconf import DB_DIR, DB_NAME, MAX_AGE


def dir_is_exists(db_path: str) -> bool:
    """Check db catalog is exists"""
    return os.path.isdir(db_path)


def file_is_exists(db_path: str) -> bool:
    """Check db file is exists."""
    return os.path.exists(db_path)


def create_db() -> None:
    """Create db dir and file in that dir."""
    db_path = DB_DIR
    filename: str = DB_NAME

    if not dir_is_exists(db_path):
        os.mkdir(db_path)

    with shelve.open(filename):
        pass


def get_db_filename() -> str:
    """Return db filename"""
    return DB_NAME


def get_expired_time() -> int:
    """Return expired time for id"""
    return MAX_AGE
