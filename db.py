import os
import shelve

from settings.globconf import DB_DIR, DB_NAME


def check_db_is_exist(db_path: str) -> bool:
    """Проверка существования каталога с БД."""
    return os.path.isdir(db_path)


def create_db() -> None:
    """Создание каталога с БД."""
    db_path = DB_DIR
    filename: str = DB_NAME

    if not check_db_is_exist(db_path):
        os.mkdir(db_path)

    with shelve.open(filename):
        pass
