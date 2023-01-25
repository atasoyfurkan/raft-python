from abc import ABC, abstractmethod
import settings
from network_service import NetworkService

class Node(ABC):

    def __init__(self,current_term =0, voted_for = None, commit_length = 0, current_leader = None, votes_received = [],
            sent_length = {}, acked_length = {}, log = []):
        self.current_term = current_term
        self.voted_for = voted_for
        self.commit_length = commit_length
        self.current_leader = current_leader
        self.votes_received = votes_received
        self.sent_length = sent_length
        self.acked_length = acked_length
        self.node_hostnames = settings.NODE_HOSTNAMES
        self.network_service = NetworkService(settings.HOSTNAME, settings.PORT)
        self.log = log

    @staticmethod
    def get_node_info():
        node_info_dict = __dict__
        del node_info_dict['node_hostnames'] 
        del node_info_dict['network_service'] 
        return node_info_dict

    # return True if votes for the candidate_hostname else returns false
    @abstractmethod
    def receive_vote_request(self, candidate_hostname, candidate_term, candidate_log_length, candidate_log_term):
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
