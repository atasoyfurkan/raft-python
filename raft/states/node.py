from __future__ import annotations
from abc import ABC
import logging
import json
import os
import settings
from services import NetworkService

if os.environ.get("TYPE_CHECKING"):
    from controller import Controller
    from models import Storage, LogEntry


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

        if leader_term >= self.storage.current_term:
            if leader_term > self.storage.current_term:
                """update current term to leader term"""
                self._discover_new_term(leader_term)

            self.storage.current_leader = leader_hostname
            follower = self.controller.convert_to_follower()
            follower._process_log_request(
                prefix_len=prefix_len,
                prefix_term=prefix_term,
                leader_commit=leader_commit,
                suffix=suffix,
            )
        else:
            self._send_log_response(ack=0, success=False)

    def _send_log_response(self, ack: int, success: bool):
        message = {
            "method": "log_response",
            "args": {
                "sender_node_hostname": settings.HOSTNAME,
                "current_term": self.storage.current_term,
                "ack": ack,
                "success": success,
            },
        }
        logging.debug(f"Sending log response to {self.storage.current_leader} with ack: {ack} and success: {success}")

        if self.storage.current_leader:
            NetworkService.send_tcp_message(json.dumps(message), self.storage.current_leader)
        else:
            logging.error("There is no 'current_leader' to send log response")

    def receive_client_write_request(self, client_hostname: str, request_id: str, msg: str):
        logging.info(
            f"Client write request is received: {msg} by a non-leader node. Leader hostname {self.storage.current_leader} is forwarding to the clients..."
        )
        message = {
            "method": "write_ack",
            "args": {"success": False, "log_entry": {}, "leader": self.storage.current_leader},
            "request_id": request_id,
        }

        NetworkService.send_tcp_message(message=json.dumps(message), receiver_host=client_hostname)

    def _discover_new_term(self, received_term: int):
        logging.info(
            f"received_term > current_term ({received_term} > {self.storage.current_term}). Becoming follower..."
        )
        self.storage.current_term = received_term
        self.storage.voted_for = None
        self.controller.convert_to_follower()

    def receive_log_response(self, follower_hostname: str, term: int, ack: int, success: bool):
        logging.debug(f"Log response is received from {follower_hostname} with ack: {ack} and success: {success}")

        if term > self.storage.current_term:
            self._discover_new_term(term)
