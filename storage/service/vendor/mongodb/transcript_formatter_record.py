import json
from typing import Optional, List

from models import TranscriptFormatterRecord
from storage.vendor import MongoBasedStorage


def serialize(record: TranscriptFormatterRecord) -> dict:
    serialized_data = json.loads(record.model_dump_json())
    serialized_data['_id'] = serialized_data.pop('id')
    return serialized_data

def deserialize(serialized_data: dict) -> TranscriptFormatterRecord:
    if '_id' in serialized_data:
        serialized_data['id'] = serialized_data.pop('_id')
    return TranscriptFormatterRecord(**serialized_data)


class TranscriptFormatterRecordMongoStorage(MongoBasedStorage):
    collection_name = "transcript_formatter_record"

    # ---- 增 ----
    def insert(self, record: TranscriptFormatterRecord) -> str:
        """
        Create a new package record in the database.

        :return: the ID of the newly created record
        """
        serialized_data = serialize(record)
        result = self.collection.insert_one(serialized_data)
        return str(result.inserted_id)

    # ---- 删 ----
    def delete_if_exists(self, id: str) -> bool:
        """
        Delete a package record from the database by its ID.
        """
        result = self.collection.delete_one({"_id": id})
        return result.deleted_count > 0

    # ---- 查 ----
    def find(self, id: str) -> Optional[TranscriptFormatterRecord]:
        """
        Find a package from the database by its ID.
        """
        result_dict: dict = self.collection.find_one({"_id": id})
        if result_dict:
            return deserialize(result_dict)
        return None


__all__ = [
    'TranscriptFormatterRecordMongoStorage',
]
