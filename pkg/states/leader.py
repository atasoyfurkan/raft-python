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

    def receive_client_write_request(self, msg: str):
        logging.info(f"Client write request is received: {msg} by the leader node.")
        self.storage.append_log_by_leader(msg)
        self._acked_length[settings.HOSTNAME] = len(self.storage.log)

        for follower_hostname in self._other_node_hostnames:
            self.replicate_log(follower_hostname=follower_hostname)

    def _send_client_response(self):
        raise NotImplementedError

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

    def receive_log_response(self, follower_hostname: str, term: int, ack: int, success: bool):
        logging.debug(
            f"Log response received from: {follower_hostname}, current state is leader, received data -> term: {term}, ack: {ack}, success: {success}"
        )

        if term == self.storage.current_term:
            if success and ack >= self._acked_length[follower_hostname]:
                self._sent_length[follower_hostname] = ack
                self._acked_length[follower_hostname] = ack
                self._commit_log_entries()

            elif self._sent_length[follower_hostname] > 0:
                self._sent_length[follower_hostname] -= 1
                self.replicate_log(follower_hostname=follower_hostname)

        elif term > self.storage.current_term:
            self._discover_new_term(term)

    def _commit_log_entries(self):
        min_acks = settings.NUMBER_OF_NODES / 2 + 1

        """List of log prefix lengths that are ready to commit, and if ready is nonempty, max(ready) is the maximum log prefix length that we can commit."""
        ready = [
            i
            for i in range(1, len(self.storage.log) + 1)
            if self._get_number_of_nodes_with_larger_ack_len(given_ack_len=i) >= min_acks
        ]
        if (
            ready != []
            and (max(ready) > self.storage.commit_length)
            and (self.storage.log[max(ready) - 1].term == self.storage.current_term)
        ):
            logging.info("Committing log entries")
            for i in range(self.storage.commit_length, max(ready)):
                self._deliver_log_entry(self.storage.log[i], log_index=i)
            self.storage.commit_length = max(ready)

    def _get_number_of_nodes_with_larger_ack_len(self, given_ack_len: int) -> int:
        return sum([1 for ack_length in self._acked_length.values() if ack_length >= given_ack_len])
