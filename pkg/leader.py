from __future__ import annotations
import logging
import settings
import os
import json
from pkg.node import Node
from pkg.heartbeat_service import HeartbeatService
from pkg.network_service import NetworkService

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.storage import Storage


class Leader(Node):
    def __init__(self, controller: Controller, storage: Storage):
        super().__init__(controller=controller, storage=storage)

        self._sent_length = {}
        self._acked_length = {}

        self.storage.current_leader = settings.HOSTNAME
        self._broadcast_new_leader()
        self._heartbeat_service = HeartbeatService(self)

    def _broadcast_new_leader(self):
        logging.info("Acknowledging other nodes you are the new leader")
        for follower_hostname in self._other_node_hostnames:
            self._sent_length[follower_hostname] = len(self.storage.log)
            self._acked_length[follower_hostname] = 0
            self.replicate_log(follower_hostname)

    def receive_vote_response(self, voter_hostname: str, granted: str, voter_term: int):
        logging.debug(f"Vote response is received from {voter_hostname}")
        if voter_term > self.storage.current_term:
            self._discover_new_term(voter_term)

    def _send_client_response(self):
        raise NotImplementedError

    def _send_log_request(self, follower_hostname: str):
        message = {
            "method": "log_request",
            "args": {
                "sender_node_hostname": settings.HOSTNAME,
                "leader_term": self.storage.current_term,
            },
        }
        logging.debug(f"Sending log request to {follower_hostname}")
        NetworkService.send_tcp_message(json.dumps(message), follower_hostname)

    def receive_log_response(self):
        raise NotImplementedError

    def receive_log_request(self, leader_hostname: str, leader_term: int):
        logging.debug(f"Log request is received from {leader_hostname}")
        if leader_term > self.storage.current_term:
            self.storage.current_leader = leader_hostname
            self._discover_new_term(leader_term)

    def _send_log_response(self):
        raise NotImplementedError

    def receive_client_request(self):
        raise NotImplementedError

    def replicate_log(self, follower_hostname: str):
        self._send_log_request(follower_hostname)
