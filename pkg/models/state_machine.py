from __future__ import annotations
import os
import logging

if os.environ.get("TYPE_CHECKING"):
    from pkg.models import LogEntry


class StateMachine:
    def __init__(self, log: list[LogEntry]):
        logging.debug(f"Initializing state machine with log: {log}")

        self.states = {}
        self.index_structure = {}

    def apply_log_entry(self, log_entry: LogEntry):
        logging.debug(f"Applying log entry: {log_entry}")
        raise NotImplementedError
