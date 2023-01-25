from node import Node
from election_timeout_service import ElectionTimeoutService
import settings
import json

class Candidate(Node):


    def start_election(self):
        self.current_term += 1


    def _send_vote_request(self):
        self.current_term += 1
        for node_hostname in self.node_hostnames:
            message = {"method": 'vote_request', "args": {'candidate_ip': settings.HOSTNAME}}
            self.network_service.send_tcp_message(json.dumps(message).encode(), node_hostname)


    def receive_vote_response(self):
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