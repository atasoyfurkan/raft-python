from __future__ import annotations
import os
import logging
from pkg.node import Node
from pkg.election_timeout_service import ElectionTimeoutService

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.storage import Storage


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

    def receive_vote_response(self, voter_hostname: str, granted: str, voter_term: int):
        logging.debug(f"Vote response is received from {voter_hostname}")
        if voter_term > self.storage.current_term:
            self._discover_new_term(voter_term)

    # def receive_log_request(self):
    #     raise NotImplementedError

    def _send_log_response(self):
        raise NotImplementedError

    def receive_client_request(self):
        raise NotImplementedError
