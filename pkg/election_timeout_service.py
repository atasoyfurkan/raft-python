import time
import random
from controller import Controller
from candidate import Candidate
from datetime import timedelta


ELECTION_TIMEOUT_INTERVAL_MS = [150, 300]


class ElectionTimeoutService:
    def __init__(self):
        super().__init__()
        self.controller = Controller()
        self._election_timeout_ms = self._generate_election_timeout()
        self._last_received_heartbeat_time_ms = int(time.time() * 1000)

    def _generate_election_timeout(self):
        return random.randint(*ELECTION_TIMEOUT_INTERVAL_MS)

    def _election_timeout_thread(self):
        while True:
            current_time = int(time.time() * 1000)
            elapsed_time = current_time - self._last_received_heartbeat_time_ms
            if elapsed_time >= self._election_timeout_ms:
                self.controller.node = Candidate()
                self.controller.node.start_election()
                return
        
        time.sleep(timedelta(milliseconds=self._election_timeout_ms))


