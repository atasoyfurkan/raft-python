from abc import ABC, abstractmethod
import settings
from network_service import NetworkService

class Node(ABC):

    def __init__(self):
        self.current_term = 0
        self.voted_for = None
        self.commit_length = 0
        self.current_leader = None
        self.votes_recieved = []
        self.sent_length = {}
        self.acked_length = {}
        self.node_hostnames = settings.NODE_HOSTNAMES
        self.network_service = NetworkService(settings.HOSTNAME, settings.PORT)

    @abstractmethod
    def receive_vote_request(self):
        pass

    @abstractmethod
    def _send_vote_response(self):
        pass

    @abstractmethod
    def receive_log_request(self):
        pass

    @abstractmethod
    def _send_log_response(self):
        pass

    @abstractmethod
    def receive_client_request(self):
        pass
