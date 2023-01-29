from __future__ import annotations
import logging
import pkg.settings as settings
import os
import json
from pkg.states.node import Node
from pkg.services import HeartbeatService, NetworkService

if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller
    from pkg.models import Storage, LogEntry


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

    def receive_vote_response(self, voter_hostname: str, granted: bool, voter_term: int):
        logging.info(f"Vote response is received from {voter_hostname}")
        if voter_term > self.storage.current_term:
            self._discover_new_term(voter_term)

    def _send_client_response(self):
        raise NotImplementedError

    def _send_log_request(self, follower_hostname: str, prefix_len: int, prefix_term: int, suffix: list[LogEntry]):
        message = {
            "method": "log_request",
            "args": {
                "leader_hostname": settings.HOSTNAME,
                "leader_term": self.storage.current_term,
                "prefix_len": prefix_len,
                "prefix_term": prefix_term,
                "leader_commit": self.storage.commit_length,
                "suffix": [log_entry.__dict__ for log_entry in suffix],
            },
        }
        if len(suffix) > 0:
            logging.info(
                f"Sending log request to {follower_hostname} with leader_term: {message['args']['leader_term']} and suffix: {message['args']['suffix']}"
            )
        else:
            logging.debug(f"Sending log request (serves as heartbeat) to {follower_hostname}")

        NetworkService.send_tcp_message(json.dumps(message), follower_hostname)

    def receive_log_response(self):
        raise NotImplementedError

    def receive_log_request(
        self,
        leader_hostname: str,
        leader_term: int,
        prefix_len: int,
        prefix_term: int,
        leader_commit: int,
        suffix: list[LogEntry],
    ):
        logging.debug(f"Log request is received from {leader_hostname}")
        if leader_term > self.storage.current_term:
            self.storage.current_leader = leader_hostname
            self._discover_new_term(leader_term)

    def _send_log_response(self):
        raise NotImplementedError

    def receive_client_request(self, msg: str):
        logging.info(f"Client request is received: {msg} by the leader node.")
        self.storage.append_log(msg)
        self._acked_length[settings.HOSTNAME] = len(self.storage.log)

        for follower_hostname in self._other_node_hostnames:
            self.replicate_log(follower_hostname)

    def replicate_log(self, follower_hostname: str):
        prefix_len = self._sent_length[follower_hostname]

        suffix: list[LogEntry] = []
        for log_entry in self.storage.log[prefix_len:]:
            suffix.append(log_entry)

        prefix_term = 0
        if prefix_len > 0:
            prefix_term = self.storage.log[prefix_len - 1].term

        self._send_log_request(
            follower_hostname=follower_hostname, prefix_len=prefix_len, prefix_term=prefix_term, suffix=suffix
        )
