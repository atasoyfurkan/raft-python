from __future__ import annotations
from abc import ABC, abstractmethod
import logging
import json
import os
import time
import pkg.settings as settings
from pkg.services import NetworkService


if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.models import Storage, LogEntry


class Node(ABC):
    def __init__(self, controller: Controller, storage: Storage):
        self.controller = controller
        self.storage = storage
        self._other_node_hostnames = settings.OTHER_NODE_HOSTNAMES

    def receive_vote_request(
        self,
        candidate_hostname: str,
        candidate_term: int,
        candidate_log_length: int,
        candidate_log_term: int,
    ) -> bool:
        """
        This function does all the necessary checks to decide if the node will vote for candidate and then
        calls _send_vote_response function for sending response (Implementation of second page in slides)
        """
        logging.info(f"Vote request is recieved from {candidate_hostname}")
        if candidate_term > self.storage.current_term:
            self._discover_new_term(candidate_term)

        last_term = 0
        if len(self.storage.log) > 0:
            last_term = self.storage.log[-1].term

        log_ok = (candidate_log_term > last_term) or (
            (candidate_log_term == last_term) and (candidate_log_length >= len(self.storage.log))
        )

        granted = False
        if (
            (candidate_term == self.storage.current_term)
            and log_ok
            and (self.storage.voted_for == None or self.storage.voted_for == candidate_hostname)
        ):
            self.storage.voted_for = candidate_hostname
            granted = True

        self._send_vote_response(granted=granted, candidate_hostname=candidate_hostname)
        return granted

    def _send_vote_response(self, granted: bool, candidate_hostname: str):
        message = {
            "method": "vote_response",
            "args": {
                "sender_node_hostname": settings.HOSTNAME,
                "voter_term": self.storage.current_term,
                "granted": granted,
            },
        }
        logging.info(f"Sending vote response to {candidate_hostname}")
        NetworkService.send_tcp_message(json.dumps(message), candidate_hostname)

    def receive_vote_response(self, voter_hostname: str, granted: bool, voter_term: int):
        logging.info(f"Vote response is received from {voter_hostname}")
        if voter_term > self.storage.current_term:
            self._discover_new_term(voter_term)

    # TODO: implement this function properly (Implementation of sixth page in slides). This implementation is just for testing
    # TODO: it might be required to implement this function in follower and candidate classes seperately (leader implementation is already done)
    # @abstractmethod
    def receive_log_request(
        self,
        leader_hostname: str,
        leader_term: int,
        prefix_len: int,
        prefix_term: int,
        leader_commit: int,
        suffix: list[LogEntry],
    ):
        if len(suffix) > 0:
            logging.info(
                f"Log request is received from {leader_hostname} with leader_term: {leader_term} and suffix: {suffix}"
            )
        else:
            logging.debug(f"Log request is received from {leader_hostname} (serves as heartbeat)")

        if leader_term > self.storage.current_term:
            self.storage.current_leader = leader_hostname
            self._discover_new_term(leader_term)

        self.storage.current_leader = leader_hostname
        self._election_timeout_service.receive_heartbeat()  # type: ignore

    def receive_client_request(self, msg: str):
        logging.info(
            f"Client request is received: {msg} by a non-leader node. Forwarding to the leader {self.storage.current_leader}..."
        )

        message = {"method": "write", "args": {"msg": msg}}
        forwarded_node_hostname = self.storage.current_leader

        if forwarded_node_hostname == None:
            """If there is no leader, wait for 0.5 seconds and send the message to yourself."""
            time.sleep(0.5)
            forwarded_node_hostname = settings.HOSTNAME

        success = NetworkService.send_tcp_message(json.dumps(message), forwarded_node_hostname)

        if not success:
            """If the message is not sent successfully, wait for 0.5 seconds and send the message to yourself."""
            time.sleep(0.5)
            forwarded_node_hostname = settings.HOSTNAME
            NetworkService.send_tcp_message(json.dumps(message), settings.HOSTNAME)

    def _discover_new_term(self, received_term: int):
        logging.info(
            f"received_term > current_term ({received_term} > {self.storage.current_term}). Becoming follower..."
        )
        self.storage.current_term = received_term
        self.storage.voted_for = None
        self.controller.change_node_state("follower")
