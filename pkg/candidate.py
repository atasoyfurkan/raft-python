from __future__ import annotations
import settings
import json
import logging
import os
from pkg.node import Node
from pkg.election_timeout_service import ElectionTimeoutService
from pkg.log_entry import LogEntry
from pkg.network_service import NetworkService

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.log_entry import LogEntry


class Candidate(Node):
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
        super().__init__(
            controller=controller,
            current_term=current_term,
            voted_for=voted_for,
            commit_length=commit_length,
            current_leader=current_leader,
            votes_received=votes_received,
            sent_length=sent_length,
            acked_length=acked_length,
            log=log,
        )

        self._election_timeout_service = ElectionTimeoutService(self)

    def _send_vote_request(self, last_term):
        for receiver_node_hostname in self._other_node_hostnames:
            message = {
                "method": "vote_request",
                "args": {
                    "sender_node_hostname": settings.HOSTNAME,
                    "current_term": self._current_term,
                    "log_length": len(self._log),
                    "last_term": last_term,
                },
            }
            logging.info(f"Sending vote request to {receiver_node_hostname}")
            NetworkService.send_tcp_message(json.dumps(message), receiver_node_hostname)

    def receive_vote_response(self):
        raise NotImplementedError

    def receive_vote_request(self, candidate_hostname):
        return False

    def _send_vote_response(self):
        raise NotImplementedError

    def receive_log_request(self):
        raise NotImplementedError

    def _send_log_response(self):
        raise NotImplementedError

    def receive_client_request(self):
        raise NotImplementedError
