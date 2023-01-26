from abc import ABC, abstractmethod
import settings
from network_service import NetworkService
from controller import Controller
from log_entry import LogEntry
from typing import Any


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
        self._network_service = NetworkService(settings.HOSTNAME, settings.PORT)

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
        node_info_dict = self.__dict__

        # Delete implementation logic variables
        del node_info_dict["controller"]
        del node_info_dict["_other_node_hostnames"]
        del node_info_dict["_network_service"]

        return node_info_dict

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
