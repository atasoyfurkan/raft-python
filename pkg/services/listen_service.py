from __future__ import annotations
import logging
import threading
import json
import os
from pkg.models import LogEntry
from pkg.services import NetworkService


if os.environ.get("TYPE_CHECKING"):
    from pkg.controller import Controller


class ListenService:
    def __init__(self, controller: Controller):
        self._controller = controller
        self._stop_thread = False

        threading.Thread(target=self._listen_thread).start()

        logging.debug(f"ListenService initialized")

    def stop(self):
        self._stop_thread = True

    def _listen_thread(self):
        logging.debug("Listen thread started.")

        while not self._stop_thread:
            received_data = NetworkService.listen_tcp_socket()
            if received_data is None:
                logging.error("Received data is None")

            message = json.loads(received_data)
            method = message["method"]
            args = message["args"]

            node = self._controller._node

            # Internal requests
            if method == "vote_request":
                node.receive_vote_request(
                    candidate_hostname=args["sender_node_hostname"],
                    candidate_term=args["current_term"],
                    candidate_log_length=args["log_length"],
                    candidate_log_term=args["last_term"],
                )

            elif method == "vote_response":
                node.receive_vote_response(
                    voter_hostname=args["sender_node_hostname"],
                    granted=args["granted"],
                    voter_term=args["voter_term"],
                )

            elif method == "log_request":
                node.receive_log_request(
                    leader_hostname=args["leader_hostname"],
                    leader_term=args["leader_term"],
                    prefix_len=args["prefix_len"],
                    prefix_term=args["prefix_term"],
                    leader_commit=args["leader_commit"],
                    suffix=[LogEntry.from_dict(log_entry_dict=log_entry_dict) for log_entry_dict in args["suffix"]],
                )
            elif method == "log_response":
                node.receive_log_response(
                    follower_hostname=args["sender_node_hostname"],
                    term=args["current_term"],
                    ack=args["ack"],
                    success=args["success"],
                )

            # Client requests
            elif method == "write":
                self._controller.handle_client_write_request(client_hostname=args["hostname"], msg=args["msg"])

            elif method == "read_value_from_key":
                self._controller.handle_client_read_request(client_hostname=args["hostname"], key=args["key"])

            elif method == "read_key_from_value":
                self._controller.handle_client_read_request(client_hostname=args["hostname"], value=args["value"])
