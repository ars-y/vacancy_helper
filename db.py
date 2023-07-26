import os

from settings.globconf import DB_DIR


def check_db_is_exist(db_path: str) -> bool:
    """Проверка существования каталога с БД."""
    return os.path.isdir(db_path)


def create_db() -> None:
    """Создание БД."""
    if not check_db_is_exist(DB_DIR):
        os.mkdir(DB_DIR)
