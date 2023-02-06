from __future__ import annotations
import os
import logging
import json

if os.environ.get("TYPE_CHECKING"):
    from pkg.models import LogEntry


class StateMachine:
    def __init__(self, log: list[LogEntry]):
        logging.debug(f"Initializing state machine with log: {log}")

        self._key_value_storage = {}
        self._index_structure = {}

        for log_entry in log:
            self.apply_log_entry(log_entry)

    def _decode_msg(self, msg: str):
        logging.debug(f"Decoding message: {msg}")
        return json.loads(msg)

    def apply_log_entry(self, log_entry: LogEntry):
        logging.info(f"Applying log entry: {log_entry}")

        decoded_msg = self._decode_msg(log_entry.msg)
        key = str(decoded_msg["key"])
        value = str(decoded_msg["value"])

        logging.debug(f"Adding key-value pair: {key} - {value} to the key-value storage.")
        if key in self._key_value_storage:
            logging.debug(
                f"Key {key} already exists in the key-value storage with value {self._key_value_storage[key]}. Replacing..."
            )
            old_value = self._key_value_storage[key]
            del self._index_structure[old_value]

        self._key_value_storage[key] = value
        self._index_structure[value] = key

        logging.debug(f"Key-value storage: {self._key_value_storage} and index structure: {self._index_structure}")

    def read_value_from_key(self, key: str):
        logging.debug(f"Reading value from key: {key}")
        if key in self._key_value_storage:
            return self._key_value_storage[key]
        else:
            return None

    def read_key_from_value(self, value: str):
        logging.debug(f"Reading key from value: {value}")
        if value in self._index_structure:
            return self._index_structure[value]
        else:
            return None
