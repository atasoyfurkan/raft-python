import logging
from pkg.states import Follower, Candidate, Leader
from pkg.models import Storage, LogEntry, StateMachine
from pkg.services import ListenService
from typing import cast


class Controller:
    def __init__(self):
        # TODO: apply committed log while recovering
        # TODO: recover persistent variables from files

        storage = Storage(
            current_term=0,
            voted_for=None,
            commit_length=0,
            current_leader=None,
            log=[],
        )
        self._node: Follower | Candidate | Leader = Follower(self, storage)
        self._state_machine = StateMachine(log=storage.log)
        self._listen_service = ListenService(self)

    def __del__(self):
        self._listen_service.stop()

    def handle_client_read_request(self):
        raise NotImplementedError

    def handle_client_write_request(self, msg: str, client_hostname: str):
        self._node.receive_client_write_request(msg=msg, client_hostname=client_hostname)

    def apply_log_entry(self, log_entry: LogEntry):
        self._state_machine.apply_log_entry(log_entry=log_entry)

    def convert_to_follower(self) -> Follower:
        return cast(Follower, self._convert(Follower))

    def convert_to_candidate(self) -> Candidate:
        return cast(Candidate, self._convert(Candidate))

    def convert_to_leader(self) -> Leader:
        return cast(Leader, self._convert(Leader))

    def _convert(self, NewType: type[Follower | Candidate | Leader]) -> Follower | Candidate | Leader:
        if type(self._node) is not NewType:
            logging.info(f"New type is {NewType}.")
            self._close_threads_while_converting()
            node = NewType(self, self._node.storage)
            self._node = node
        return self._node

    def _close_threads_while_converting(self):
        if type(self._node) is Follower or type(self._node) is Candidate:
            self._node._election_timeout_service.stop()
        elif type(self._node) is Leader:
            self._node._heartbeat_service.stop()
