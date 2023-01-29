from pkg.models import LogEntry


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

    def append_log(self, msg: str):
        self.log.append(LogEntry(term=self.current_term, msg=msg))
