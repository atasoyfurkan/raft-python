import logging
import threading
import json
from pkg.states import Follower, Candidate, Leader
from pkg.models import Storage
from pkg.services import NetworkService


class Controller:
    def __init__(self):
        # TODO: apply committed log while recovering
        # TODO: recover persistent variables from files

        storage = Storage(
            current_term=0,
            voted_for=None,
            commit_length=0,
            current_leader=None,
            log=[],
        )
        self._node: Follower | Candidate | Leader = Follower(self, storage)

        # Start listen thread
        threading.Thread(target=self._listen_thread).start()

    @property
    def state(self):
        if isinstance(self._node, Follower):
            return "follower"
        elif isinstance(self._node, Candidate):
            return "candidate"
        elif isinstance(self._node, Leader):
            return "leader"

    def _listen_thread(self):
        while True:
            received_data = NetworkService.listen_tcp_socket()
            if received_data is None:
                logging.error("Received data is None")

            message = json.loads(received_data)
            method = message["method"]
            args = message["args"]

            if method == "vote_request":
                self._node.receive_vote_request(
                    candidate_hostname=args["sender_node_hostname"],
                    candidate_term=args["current_term"],
                    candidate_log_length=args["log_length"],
                    candidate_log_term=args["last_term"],
                )

            elif method == "vote_response":
                self._node.receive_vote_response(
                    voter_hostname=args["sender_node_hostname"],
                    granted=args["granted"],
                    voter_term=args["voter_term"],
                )

            elif method == "log_request":
                self._node.receive_log_request(
                    leader_hostname=args["sender_node_hostname"],
                    leader_term=args["leader_term"],
                )

    def handle_client_read_request(self):
        raise NotImplementedError

    def handle_client_write_request(self):
        raise NotImplementedError

    def _close_threads_while_changing_state(self):
        if self.state == "follower" or self.state == "candidate":
            self._node._election_timeout_service.stop()  # type: ignore
        elif self.state == "leader":
            self._node._heartbeat_service.stop()  # type: ignore

    def change_node_state(self, new_state: str) -> Follower | Candidate | Leader:
        if new_state == self.state:
            logging.debug(
                f"New state ({new_state}) is same as current state ({self.state}). No change."
            )
        else:
            self._close_threads_while_changing_state()

            storage = self._node.storage
            if new_state == "follower":
                self._node = Follower(self, storage)
            elif new_state == "candidate":
                self._node = Candidate(self, storage)
            elif new_state == "leader":
                self._node = Leader(self, storage)
            logging.debug(f"New state is {new_state}")

        return self._node
