import time
import random

ELECTION_TIMEOUT_INTERVAL_MS = [150, 300]


class ElectionTimeoutService:
    def __init__(self):
        super().__init__()
        self._election_timeout_ms = self._generate_election_timeout()
        self._last_received_heartbeat_time_ms = int(time.time() * 1000)

    def _generate_election_timeout(self):
        return random.randint(*ELECTION_TIMEOUT_INTERVAL_MS)

    def _election_timeout_thread(self):
        raise NotImplementedError
