from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
import logging
import json
import os
import settings
from pkg.network_service import NetworkService

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.storage import Storage


class Node(ABC):
    def __init__(self, controller: Controller, storage: Storage):
        self.controller = controller
        self.storage = storage
        self._other_node_hostnames = settings.OTHER_NODE_HOSTNAMES

    def _discover_new_term(self, received_term: int):
        logging.info(
            f"received_term > current_term ({received_term} > {self.storage.current_term}). Becoming follower..."
        )
        self.storage.current_term = received_term
        self.storage.voted_for = None
        self.controller.change_node_state("follower")

    # This function does all the necessary checks to decide if the node will vote for candidate and then
    # calls _send_vote_response function for sending response (Implementation of second page in slides)
    def receive_vote_request(
        self,
        candidate_hostname: str,
        candidate_term: int,
        candidate_log_length: int,
        candidate_log_term: int,
    ) -> bool:
        logging.info(f"Vote request is recieved from {candidate_hostname}")
        if candidate_term > self.storage.current_term:
            self._discover_new_term(candidate_term)

        last_term = 0
        if len(self.storage.log) > 0:
            last_term = self.storage.log[-1].term

        log_ok = (candidate_log_term > last_term) or (
            (candidate_log_term == last_term)
            and (candidate_log_length >= len(self.storage.log))
        )

        granted = False
        if (
            (candidate_term == self.storage.current_term)
            and log_ok
            and (
                self.storage.voted_for == None
                or self.storage.voted_for == candidate_hostname
            )
        ):
            self.storage.voted_for = candidate_hostname
            granted = True

        self._send_vote_response(granted=granted, candidate_hostname=candidate_hostname)
        return granted

    # granted is a boolean parameter and shows if the node will vote for candidate or not
    def _send_vote_response(self, granted: bool, candidate_hostname: str):
        message = {
            "method": "vote_response",
            "args": {
                "sender_node_hostname": settings.HOSTNAME,
                "voter_term": self.storage.current_term,
                "granted": str(granted),
            },
        }
        logging.info(f"Sending vote response to {candidate_hostname}")
        NetworkService.send_tcp_message(json.dumps(message), candidate_hostname)

    @abstractmethod
    def receive_vote_response(self, voter_hostname: str, granted: str, voter_term: int):
        pass

    # @abstractmethod
    def receive_log_request(self, leader_hostname: str, leader_term: int):
        logging.debug(f"Log request is received from {leader_hostname}")
        if leader_term > self.storage.current_term:
            self.storage.current_leader = leader_hostname
            self._discover_new_term(leader_term)
        self._election_timeout_service.receive_heartbeat()  # type: ignore

    @abstractmethod
    def _send_log_response(self):
        pass

    @abstractmethod
    def receive_client_request(self):
        pass
