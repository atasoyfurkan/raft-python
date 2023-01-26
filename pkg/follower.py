from pkg.node import Node
from pkg.election_timeout_service import ElectionTimeoutService
from controller import Controller
from log_entry import LogEntry


class Follower(Node):
    def __init__(
        self,
        controller: Controller,
        current_term: int,
        voted_for: str | None,
        commit_length: int,
        current_leader: str | None,
        votes_received: list[int],
        sent_length: dict[str, int],
        acked_length: dict[str, int],
        log: list[LogEntry],
    ):
        super().__init__(
            controller=controller,
            current_term=current_term,
            voted_for=voted_for,
            commit_length=commit_length,
            current_leader=current_leader,
            votes_received=votes_received,
            sent_length=sent_length,
            acked_length=acked_length,
            log=log,
        )

        self._election_timeout_service = ElectionTimeoutService(self)

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
