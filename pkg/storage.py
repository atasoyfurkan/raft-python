from __future__ import annotations
import os

if os.environ.get("TYPE_CHECKING"):
    from pkg.log_entry import LogEntry


class Storage:
    def __init__(
        self,
        current_term: int,
        voted_for: str | None,
        commit_length: int,
        current_leader: str | None,
        log: list[LogEntry],
    ):
        self.current_term = current_term
        self.voted_for = voted_for
        self.commit_length = commit_length
        self.current_leader = current_leader
        self.log = log
