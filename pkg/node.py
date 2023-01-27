from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
import settings
import os

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.log_entry import LogEntry


class Node(ABC):
    def __init__(
        self,
        controller: Controller,
        current_term: int,
        voted_for: str | None,
        commit_length: int,
        current_leader: str | None,
        votes_received: list[int],
        sent_length: dict[str, int],
        acked_length: dict[str, int],
        log: list[LogEntry],
    ):
        # Implementation logic variables
        self.controller = controller
        self._other_node_hostnames = settings.OTHER_NODE_HOSTNAMES

        # Raft state variables
        self._current_term = current_term
        self._voted_for = voted_for
        self._commit_length = commit_length
        self._current_leader = current_leader
        self._votes_received = votes_received
        self._sent_length = sent_length
        self._acked_length = acked_length
        self._log = log

    def get_current_state(self) -> dict[str, Any]:
        current_state = {}
        current_state["current_term"] = self._current_term
        current_state["voted_for"] = self._voted_for
        current_state["commit_length"] = self._commit_length
        current_state["current_leader"] = self._current_leader
        current_state["votes_received"] = self._votes_received
        current_state["sent_length"] = self._sent_length
        current_state["acked_length"] = self._acked_length
        current_state["log"] = self._log

        return current_state

    # return True if votes for the candidate_hostname else returns false
    @abstractmethod
    def receive_vote_request(
        self,
        candidate_hostname,
        candidate_term,
        candidate_log_length,
        candidate_log_term,
    ):
        pass

    @abstractmethod
    def _send_vote_response(self):
        pass

    @abstractmethod
    def receive_log_request(self):
        pass

    @abstractmethod
    def _send_log_response(self):
        pass

    @abstractmethod
    def receive_client_request(self):
        pass
