import os
from pkg.models import LogEntry
from pkg.settings import STORAGE_PATH


class Storage:
    def __init__(
        self,
        commit_length: int,
        current_leader: str | None,
    ):
        current_term: int = 0
        voted_for: str | None = None
        log: list[LogEntry] = []

        if self._is_file_exists("current_term"):
            current_term = self._read_current_term()
        if self._is_file_exists("voted_for"):
            voted_for = self._read_voted_for()
        if self._is_file_exists("log"):
            log = self._read_log()

        self.commit_length = commit_length
        self.current_leader = current_leader
        self._current_term = current_term
        self._voted_for = voted_for
        self._log = log

    def append_log_by_leader(self, msg: str):
        self._append_log(LogEntry(term=self.current_term, msg=msg))

    def append_log_by_follower(self, log_entry: LogEntry):
        self._append_log(log_entry)

    def _is_file_exists(self, relative_path: str) -> bool:
        path = os.path.join(STORAGE_PATH, relative_path)
        return os.path.isfile(path)

    def _read_current_term(self) -> int:
        with open(os.path.join(STORAGE_PATH, "current_term"), "r") as f:
            return int(f.read())

    def _read_voted_for(self) -> str | None:
        with open(os.path.join(STORAGE_PATH, "voted_for"), "r") as f:
            return f.read()

    def _read_log(self) -> list[LogEntry]:
        with open(os.path.join(STORAGE_PATH, "log"), "r") as f:
            return [LogEntry.from_json(log_entry_json=line) for line in f.readlines()]

    def _write_current_term(self, current_term: int):
        with open(os.path.join(STORAGE_PATH, "current_term"), "w") as f:
            f.write(str(current_term))

    def _write_voted_for(self, voted_for: str | None):
        with open(os.path.join(STORAGE_PATH, "voted_for"), "w") as f:
            if voted_for is not None:
                f.write(voted_for)

    def _write_log(self, log: list[LogEntry]):
        with open(os.path.join(STORAGE_PATH, "log"), "w") as f:
            for log_entry in log:
                f.write(f"{log_entry.to_json()}\n")

    def _file_append_log(self, log_entry: LogEntry):
        with open(os.path.join(STORAGE_PATH, "log"), "a") as f:
            f.write(f"{log_entry.to_json()}\n")

    @property
    def current_term(self) -> int:
        return self._current_term

    @property
    def voted_for(self) -> str | None:
        return self._voted_for

    @property
    def log(self) -> list[LogEntry]:
        return self._log

    @current_term.setter
    def current_term(self, current_term: int):
        self._write_current_term(current_term=current_term)
        self._current_term = current_term

    @voted_for.setter
    def voted_for(self, voted_for: str | None):
        self._write_voted_for(voted_for=voted_for)
        self._voted_for = voted_for

    @log.setter
    def log(self, log: list[LogEntry]):
        self._write_log(log=log)
        self._log = log

    def _append_log(self, log_entry: LogEntry):
        self._file_append_log(log_entry=log_entry)
        self._log.append(log_entry)
