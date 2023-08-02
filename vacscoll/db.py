import datetime as dt
import os
import shelve

from .constants import DB_DIR, DB_NAME, MAX_AGE


class VIDStorage:
    """Vacancies ID database."""

    def __init__(self) -> None:
        self._db_path = DB_DIR
        self._db_name = DB_NAME
        self._max_age = MAX_AGE

        self._prepare_database()

    def _create_db(self) -> None:
        """Create db dir and file in that dir."""
        if not self._dir_is_exists():
            os.mkdir(self._db_path)

        with shelve.open(self._db_name):
            pass

    def _dir_is_exists(self) -> bool:
        """Check db catalog is exists"""
        return os.path.isdir(self._db_path)

    def _file_is_exists(self) -> bool:
        """Check db file is exists."""
        return os.path.exists(self._db_path)

    def _prepare_database(self) -> None:
        """Creating database if it isn't exists."""
        if not self._file_is_exists():
            self._create_db()

    def save(self, vacancies_id: list) -> None:
        """Save vacancies id in db with timestamp."""
        with shelve.open(self._db_name) as vdb:
            for vid in vacancies_id:
                if vid not in vdb:
                    current_time = dt.datetime.now()
                    vdb[vid] = dt.datetime.timestamp(current_time)

    def load(self) -> set:
        """Loading set of vacancies id. Remove id if expired."""
        vacancies_id: set = {}
        time_delta = dt.timedelta(self._max_age)
        expired_ids: list = []

        with shelve.open(self._db_name) as vdb:
            vacancies_id = set(vdb.keys())

            for vid in vdb:
                pub_date = dt.datetime.fromtimestamp(vdb[vid])
                current_date = dt.datetime.now()
                if pub_date + time_delta < current_date:
                    expired_ids.append(vid)

            if expired_ids:
                for vid in expired_ids:
                    vdb.pop(vid)

        return vacancies_id
