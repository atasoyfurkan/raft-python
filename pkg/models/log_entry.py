from typing import Optional


class LogEntry:
    def __init__(self, term: Optional[int] = None, msg: Optional[str] = None, log_entry_dict: Optional[dict] = None):
        if log_entry_dict:
            term = log_entry_dict["term"]
            msg = log_entry_dict["msg"]

        if term == None or msg == None:
            raise ValueError("Either term and msg or log_entry_dict must be provided")

        self.term = term
        self.msg = msg

    def __repr__(self):
        return f"LogEntry(term={self.term}, msg={self.msg})"
