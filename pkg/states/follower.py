from __future__ import annotations
import os
import logging
from pkg.states.node import Node
from pkg.services import ElectionTimeoutService
from pkg.models import LogEntry

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.models import Storage


class Follower(Node):
    def __init__(self, controller: Controller, storage: Storage):
        super().__init__(controller=controller, storage=storage)

        self._election_timeout_service = ElectionTimeoutService(self)

    def receive_vote_request(
            self,
            candidate_hostname: str,
            candidate_term: int,
            candidate_log_length: int,
            candidate_log_term: int,
    ) -> bool:
        """
        Override the receive_vote_request method to reset the election timeout when you vote for a candidate.
        """
        grant = super().receive_vote_request(
            candidate_hostname, candidate_term, candidate_log_length, candidate_log_term
        )
        if grant:
            self._election_timeout_service.receive_heartbeat()

        return grant

    # def receive_log_request(self):
    #     raise NotImplementedError

    # def _send_log_response(self):
    #    raise NotImplementedError

    def _append_entries(self, prefix_len, leader_commit, suffix):
        if len(suffix) > 0 and len(self.storage.log) > prefix_len:
            index = min(len(self.storage.log), prefix_len + len(suffix)) - 1
            logging.info(f"log is as follows: {self.storage.log}")
            if self.storage.log[index].term != suffix[index - prefix_len]["term"]:
                self.storage.log = self.storage.log[0:prefix_len]
        if prefix_len + len(suffix) > len(self.storage.log):
            for entry in suffix[len(self.storage.log) - prefix_len:]:
                self.storage.log.append(LogEntry(entry["term"], entry["msg"]))
        if leader_commit > self.storage.commit_length:
            for i in range(self.storage.commit_length, leader_commit):
                self._deliver_log_entry(log_entry=self.storage.log[i])
            self.storage.commit_length = leader_commit
