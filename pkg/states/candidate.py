from __future__ import annotations
import pkg.settings as settings
import json
import logging
import os
from pkg.states.node import Node
from pkg.services import NetworkService, ElectionTimeoutService

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.models import Storage


class Candidate(Node):
    def __init__(self, controller: Controller, storage: Storage):
        super().__init__(controller=controller, storage=storage)

        self._votes_received = set()
        self._election_timeout_service = ElectionTimeoutService(self)

    def start_election(self):
        self.storage.current_term += 1
        self.storage.voted_for = settings.HOSTNAME
        self._votes_received = set([settings.HOSTNAME])

        last_term = 0
        if len(self.storage.log) > 0:
            last_term = self.storage.log[-1].term

        logging.info(f"Election is started for term: {self.storage.current_term}")
        self._send_vote_request(last_term)

    def _send_vote_request(self, last_term: int):
        for receiver_node_hostname in self._other_node_hostnames:
            message = {
                "method": "vote_request",
                "args": {
                    "sender_node_hostname": settings.HOSTNAME,
                    "current_term": self.storage.current_term,
                    "log_length": len(self.storage.log),
                    "last_term": last_term,
                },
            }
            logging.info(f"Sending vote request to {receiver_node_hostname}")
            NetworkService.send_tcp_message(json.dumps(message), receiver_node_hostname)

    # This function is the implementation of the third page in slides
    def receive_vote_response(self, voter_hostname: str, granted: bool, voter_term: int):
        logging.info(f"Vote response is received from {voter_hostname}")

        if voter_term == self.storage.current_term and granted:
            self._votes_received.add(voter_hostname)
            logging.info(f"Vote is valid. Current votes: {self._votes_received}")
            if len(self._votes_received) > (settings.NUMBER_OF_NODES) / 2:
                logging.info(
                    f"Leader is elected. Total votes: {len(self._votes_received)} / {settings.NUMBER_OF_NODES}"
                )
                self.controller.change_node_state("leader")

        elif voter_term > self.storage.current_term:
            self._discover_new_term(voter_term)

    # def receive_log_request(self):
    #     raise NotImplementedError

    def _send_log_response(self):
        raise NotImplementedError

    def receive_client_request(self):
        raise NotImplementedError
