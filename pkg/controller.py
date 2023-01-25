from follower import Follower

class Controller:
    def __init__(self):
        self.node = Follower()
        # TODO: apply committed log while recovering
        pass

    def _listen_thread(self):
        raise NotImplementedError

    def handle_client_read_request(self):
        raise NotImplementedError

    def handle_client_write_request(self):
        raise NotImplementedError
