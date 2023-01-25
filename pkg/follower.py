from pkg.node import Node
from pkg.election_timeout_service import ElectionTimeoutService


class Follower(Node):
    def __init__(self):
        super().__init__()
        self.election_timeout_service = ElectionTimeoutService()

    def receive_vote_request(self):
        raise NotImplementedError

    def _send_vote_response(self):
        raise NotImplementedError

    def receive_log_request(self):
        raise NotImplementedError

    def _send_log_response(self):
        raise NotImplementedError

    def receive_client_request(self):
        raise NotImplementedError
