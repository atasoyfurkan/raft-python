from node import Node
from election_timeout_service import ElectionTimeoutService
import settings
import json


class Candidate(Node):

    def __init__(self,current_term =0, voted_for = None, commit_length = 0, current_leader = None, votes_received = [],
            sent_length = {}, acked_length = {}, log = []):
        super.__init(self,current_term =0, voted_for = None, commit_length = 0, current_leader = None, votes_received = [],
            sent_length = {}, acked_length = {}, log = [])

    def start_election(self):
        self.current_term += 1
        self.voted_for = settings.HOSTNAME
        self.votes_received = [settings.HOSTNAME]
        last_term = 0
        if len(self.log) != 0 :
            last_term = self.log[-1].term
        self._send_vote_request(last_term)


    def _send_vote_request(self,last_term):
        self.current_term += 1
        for node_hostname in self.node_hostnames:
            message = {"method": 'vote_request', "args": {'Hostname': settings.HOSTNAME,'current_term': self.current_term,
            'log_length':len(self.log), 'last_term':last_term}}
            self.network_service.send_tcp_message(json.dumps(message), node_hostname)


    def receive_vote_response(self):
        raise NotImplementedError

    def receive_vote_request(self,candidate_hostname):
        return False

    def _send_vote_response(self):
        raise NotImplementedError

    def receive_log_request(self):
        raise NotImplementedError

    def _send_log_response(self):
        raise NotImplementedError

    def receive_client_request(self):
        raise NotImplementedError
