import json


class LogEntry:
    def __init__(self, term: int, msg: str):
        self.term = term
        self.msg = msg

    @classmethod
    def from_dict(cls, log_entry_dict: dict):
        return cls(term=log_entry_dict["term"], msg=log_entry_dict["msg"])

    @classmethod
    def from_json(cls, log_entry_json: str):
        return cls.from_dict(json.loads(log_entry_json))

    def to_dict(self) -> dict:
        return {"term": self.term, "msg": self.msg}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __repr__(self):
        return f"LogEntry(term={self.term}, msg={self.msg})"
