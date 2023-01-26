from pkg.network_service import NetworkService
import settings
from follower import Follower
from candidate import Candidate


class Controller:
    def __init__(self):
        # TODO: apply committed log while recovering
        # TODO: recover persistent variables from files
        self._network_service = NetworkService(settings.HOSTNAME, settings.PORT)
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

    def _listen_thread(self):
        received_data = self._network_service.listen_tcp_socket()

    def handle_client_read_request(self):
        raise NotImplementedError

    def handle_client_write_request(self):
        raise NotImplementedError

    def start_election(self):
        current_state = self._node.get_current_state()
        current_state["current_term"] += 1
        current_state["voted_for"] = settings.HOSTNAME
        current_state["votes_received"] = [settings.HOSTNAME]

        self._node = Candidate(self, **current_state)

        last_term = 0
        if len(current_state["log"]) > 0:
            last_term = current_state["log"][-1].term

        self._node._send_vote_request(last_term)
