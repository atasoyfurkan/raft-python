import logging
import json
from pkg.states import Follower, Candidate, Leader
from pkg.models import Storage, LogEntry, StateMachine
from pkg.services import ListenService, NetworkService
from typing import cast, Optional


class Controller:
    def __init__(self):
        storage = Storage(commit_length=0, current_leader=None)
        self._node: Follower | Candidate | Leader = Follower(self, storage)
        self._state_machine = StateMachine(log=storage.log)
        self._listen_service = ListenService(self)

    def __del__(self):
        self._listen_service.stop()

    def handle_client_read_request(self, client_hostname: str, key: Optional[str] = None, value: Optional[str] = None):
        result = None
        if key is not None:
            result = self._state_machine.read_value_from_key(key=key)
        if value is not None:
            result = self._state_machine.read_key_from_value(value=value)

        success = True
        if result is None:
            success = False
            result = "No result"

        self._send_client_read_response(client_hostname=client_hostname, success=success, result=result)

    def _send_client_read_response(self, client_hostname: str, success: bool, result: str):
        message = {
            "method": "read_ack",
            "args": {
                "success": success,
                "result": result,
                "leader": self._node.storage.current_leader,
            },
        }
        logging.info(f"Sending client read response to {client_hostname} with result: {message['args']['result']}")

        NetworkService.send_tcp_message(message=json.dumps(message), receiver_host=client_hostname)

    def handle_client_write_request(
        self,
        client_hostname: str,
        msg: str,
    ):
        self._node.receive_client_write_request(client_hostname=client_hostname, msg=msg)

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
            logging.info(f"New type is {NewType.__name__}.")
            self._close_threads_while_converting()
            node = NewType(self, self._node.storage)
            self._node = node
        return self._node

    def _close_threads_while_converting(self):
        if type(self._node) is Follower or type(self._node) is Candidate:
            self._node._election_timeout_service.stop()
        elif type(self._node) is Leader:
            self._node._heartbeat_service.stop()
