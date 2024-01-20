from typing import List, Optional

from models import TranscriptFormatterRecord
from .vendor import (
    TranscriptFormatterRecordMongoStorage,
)


class TranscriptFormatterRecordStorage:
    def __init__(self):
        self._record_mongo_storage = TranscriptFormatterRecordMongoStorage()

    # ---- 增 ----
    def insert(self, record: TranscriptFormatterRecord) -> str:
        """
        Create a new repository record in the database.

        :return: the ID of the newly created repository
        """
        return self._record_mongo_storage.insert(record=record)

    # ---- 删 ----
    def delete(self, id: str) -> bool:
        """
        Delete a repository record from the database by its ID.
        """
        return self._record_mongo_storage.delete_if_exists(id=id)

    # ---- 查 ----
    def find(self, repo_id: str) -> Optional[TranscriptFormatterRecord]:
        """
        Find a repository from the database by its ID.
        """
        return self._repo_mongo_storage.find(repo_id)

    # ---- with management ----
    def __enter__(self):
        self._record_mongo_storage.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._record_mongo_storage.__exit__(exc_type, exc_val, exc_tb)


__all__ = [
    "TranscriptFormatterRecordStorage",
]
