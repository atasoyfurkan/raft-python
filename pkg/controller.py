import settings
import logging
import threading
import json
from pkg.network_service import NetworkService
from pkg.follower import Follower
from pkg.candidate import Candidate
from pkg.leader import Leader


class Controller:
    def __init__(self):
        # TODO: apply committed log while recovering
        # TODO: recover persistent variables from files
        self._node = Follower(
            self,
            current_term=0,
            voted_for=None,
            commit_length=0,
            current_leader=None,
            votes_received=[],
            sent_length={},
            acked_length={},
            log=[],
        )
        self.state = "follower"

        # Start listen thread
        threading.Thread(target=self._listen_thread).start()

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

    def handle_client_read_request(self):
        raise NotImplementedError

    def handle_client_write_request(self):
        raise NotImplementedError

    def start_election(self):
        current_state = self._node.get_current_state()
        current_state["current_term"] += 1
        current_state["voted_for"] = settings.HOSTNAME
        current_state["votes_received"] = [settings.HOSTNAME]

        self.state = "candidate"
        self._node = Candidate(self, **current_state)

        last_term = 0
        if len(current_state["log"]) > 0:
            last_term = current_state["log"][-1].term

        self._node._send_vote_request(last_term)

    def change_node_state(self, new_state: str):
        if new_state == self.state:
            return
        current_state = self._node.get_current_state()
        if new_state == "follower":
            self._node = Follower(self, **current_state)
        if new_state == "candidate":
            self._node = Candidate(self, **current_state)
        if new_state == "leader":
            self._node = Leader(self, **current_state)
        self.state = new_state

        logging.debug(f"New state is {new_state}")
