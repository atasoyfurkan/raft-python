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

    def _process_log_request(
        self,
        prefix_len: int,
        prefix_term: int,
        leader_commit: int,
        suffix: list[LogEntry],
    ):
        self._election_timeout_service.receive_heartbeat()

        log_ok = (len(self.storage.log) >= prefix_len) and (
            (prefix_len == 0) or (self.storage.log[prefix_len - 1].term == prefix_term)
        )

        if log_ok:
            """
            Raft ensures that if two nodes have the same term number at the same index of the log, then their logs are identical up to and including that index.
            Therefore, if the logOk variable is set to true, that means the follower’s first prefixLen log entries are identical to the corresponding log prefix on the leader.
            """
            self._append_entries(prefix_len=prefix_len, leader_commit=leader_commit, suffix=suffix)
            ack = prefix_len + len(suffix)
            self._send_log_response(ack=ack, success=True)
        else:
            self._send_log_response(ack=0, success=False)

    def _append_entries(self, prefix_len: int, leader_commit: int, suffix: list[LogEntry]):
        if len(suffix) > 0 and len(self.storage.log) > prefix_len:
            """If the follower's log already contains entries at log[prefixLen] and beyond, we need to check whether they match the log entries in suffix."""
            index = min(len(self.storage.log), prefix_len + len(suffix)) - 1
            if self.storage.log[index].term != suffix[index - prefix_len].term:
                """
                We have to truncate the log, keeping only the first prefixLen entries and discarding the rest.
                Such inconsistency could happen if the existing log entries came from a previous leader, which has now been superseded by a new leader.
                """
                self.storage.log = self.storage.log[0:prefix_len]

        if prefix_len + len(suffix) > len(self.storage.log):
            """Idempotent: If the follower's log is already as long as the leader's log, then the follower's log is already up-to-date."""
            for entry in suffix[len(self.storage.log) - prefix_len :]:
                self.storage.append_log_by_follower(entry)

        if leader_commit > self.storage.commit_length:
            # TODO: deliver log should be implemented
            """This means that new records are ready to be committed and delivered to the application"""
            for i in range(self.storage.commit_length, leader_commit):
                self._deliver_log_entry(log_entry=self.storage.log[i], log_index=i)
            self.storage.commit_length = leader_commit
