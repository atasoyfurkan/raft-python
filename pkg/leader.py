from pkg.node import Node


class Leader(Node):
    def __init__(self):
        pass

    def _send_client_response(self):
        raise NotImplementedError

    def _send_log_request(self):
        raise NotImplementedError

    def receive_log_response(self):
        raise NotImplementedError

    def _heartbeat_thread(self):
        raise NotImplementedError

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
