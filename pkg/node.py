from abc import ABC, abstractmethod
from typing import Any
import settings
from pkg.network_service import NetworkService
from pkg.log_entry import LogEntry
import logging
import json


class Node(ABC):
    def __init__(
        self,
        controller,
        current_term: int,
        voted_for: str | None,
        commit_length: int,
        current_leader: str | None,
        votes_received: list[int],
        sent_length: dict[str, int],
        acked_length: dict[str, int],
        log: list[LogEntry],
    ):
        # Implementation logic variables
        self.controller = controller
        self._other_node_hostnames = settings.OTHER_NODE_HOSTNAMES
        # self._network_service = NetworkService(settings.HOSTNAME, settings.PORT)

        # Raft state variables
        self._current_term = current_term
        self._voted_for = voted_for
        self._commit_length = commit_length
        self._current_leader = current_leader
        self._votes_received = votes_received
        self._sent_length = sent_length
        self._acked_length = acked_length
        self._log = log

    def get_current_state(self) -> dict[str, Any]:
        current_state = {}
        current_state["current_term"] = self._current_term
        current_state["voted_for"] = self._voted_for
        current_state["commit_length"] = self._commit_length
        current_state["current_leader"] = self._current_leader
        current_state["votes_received"] = self._votes_received
        current_state["sent_length"] = self._sent_length
        current_state["acked_length"] = self._acked_length
        current_state["log"] = self._log

        return current_state

    # This function does all the necessary checks to decide if the node will vote for candidate and then
    # calls _send_vote_response function for sending response (Implementation of second page in slides)
    def receive_vote_request(self,candidate_hostname,candidate_term,candidate_log_length,candidate_log_term):
        logging.info(f"Vote request is recieved from {candidate_hostname}")
        if candidate_term > self._current_term:
                self._current_term = candidate_term
                self._voted_for = None
                self.controller.change_node_state('follower')

        last_term = 0
        if len(self._log) > 0:
            last_term = self._log[-1].term

        log_ok = (candidate_log_term > last_term ) or ((candidate_log_term == last_term) and (candidate_log_length >= len(self._log)))

        if (candidate_term == self._current_term) and log_ok and (self._voted_for == None or self._voted_for == candidate_hostname):
            self._voted_for = candidate_hostname
            self._send_vote_response(True, candidate_hostname)
        else:
            self._send_vote_response(False, candidate_hostname)


    # granted is a boolean parameter and shows if the node will vote for candidate or not
    def _send_vote_response(self, granted: bool, candidate_hostname):
        message = {
                "method": "vote_response",
                "args": {
                    "sender_node_hostname": settings.HOSTNAME,
                    "voter_term": self._current_term,
                    "granted": str(granted),
                },
            }
        logging.info(f"Sending vote response from {settings.HOSTNAME} to {candidate_hostname}")
        NetworkService.send_tcp_message(json.dumps(message), candidate_hostname)


    # This function is the implementation of the third page in slides
    def receive_vote_response(self, voter_hostname,granted,voter_term):

        logging.info(f"Vote response is received from {voter_hostname}")

        if voter_term > self._current_term:
            self._current_term = voter_term
            self._voted_for = None
            self.controller.change_node_state('follower')
            # add stop election timer
            logging.info(f"Voter term is larger than current term. Voter_term:{voter_term} , current_term{self._current_term}")
        else:
            if (self.controller.state == 'candidate') and (voter_term == self._current_term) and (granted == "True"):
                self._votes_received.append(voter_hostname)
                logging.info(f"Vote is valid")
                if len(self._votes_received) > (len(self._other_node_hostnames) + 1) / 2:
                    self._current_leader = settings.HOSTNAME
                    self.controller.change_node_state('leader')
                    # add stop election timer
                for node in self._other_node_hostnames:
                    self._sent_length[node] = len(self._log)
                    self._acked_length[node] = 0
                    self.replicate_log(settings.HOSTNAME,node)                    


    def replicate_log(self,leader_hostname, follower_hostname):
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