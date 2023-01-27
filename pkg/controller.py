import settings
import logging
import threading
from pkg.network_service import NetworkService
from pkg.follower import Follower
from pkg.candidate import Candidate
from pkg.leader import Leader



class Controller:
    def __init__(self):
        # TODO: apply committed log while recovering
        # TODO: recover persistent variables from files
        # self._network_service = NetworkService(settings.HOSTNAME, settings.PORT)
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
        self.state = 'follower'

        # Start listen thread
        threading.Thread(target=self._listen_thread).start()

    def _listen_thread(self):
        while True:
            received_data = NetworkService.listen_tcp_socket()
            if received_data is None:
                continue
            elif received_data["method"] == "vote_request":
                self._node.receive_vote_request(
                    received_data["args"]["sender_node_hostname"],
                    received_data["args"]["current_term"],
                    received_data["args"]["log_length"],
                    received_data["args"]["last_term"],
                )
            elif received_data["method"] == "vote_response":
                self._node.receive_vote_response(
                    received_data["args"]["sender_node_hostname"],
                    received_data["args"]["granted"],
                    received_data["args"]["voter_term"]
                )
            else:
                pass


    def handle_client_read_request(self):
        raise NotImplementedError

    def handle_client_write_request(self):
        raise NotImplementedError

    def start_election(self):
        current_state = self._node.get_current_state()
        current_state["current_term"] += 1
        current_state["voted_for"] = settings.HOSTNAME
        current_state["votes_received"] = [settings.HOSTNAME]

        self.state = 'candidate'
        self._node = Candidate(self, **current_state)

        last_term = 0
        if len(current_state["log"]) > 0:
            last_term = current_state["log"][-1].term

        self._node._send_vote_request(last_term)

    
    def change_node_state(self,new_state: str):
        if new_state == self.state:
            return
        current_state = self._node.get_current_state()
        if new_state == 'follower':
            self._node = Follower(self, **current_state)
        if new_state == 'candidate':
            self._node = Candidate(self, **current_state)
        if new_state == 'leader':
            self._node = Leader(self, **current_state)
        self.state = new_state

        logging.info(f"New state is {new_state}")