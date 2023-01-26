import time
import random
from candidate import Candidate
from node import Node
import logging

ELECTION_TIMEOUT_INTERVAL_MS = [150, 300]
ITERATION_SLEEP_TIME_SEC = 0.001


class ElectionTimeoutService:
    def __init__(self, current_node: Node):
        self._current_node = current_node
        self._election_timeout_ms = self._generate_election_timeout()
        self._last_received_heartbeat_time_ms = self._get_current_time_ms()

        logging.info(
            "ElectionTimeoutService initialized with election_timeout_ms: {self._election_timeout_ms}} and last_received_heartbeat_time_ms: {self._last_received_heartbeat_time_ms}"
        )

    def _generate_election_timeout(self) -> int:
        return random.randint(*ELECTION_TIMEOUT_INTERVAL_MS)

    def _get_current_time_ms(self) -> int:
        return int(time.time() * 1000)

    def _election_timeout_thread(self):
        while True:
            current_time = self._get_current_time_ms()
            elapsed_time = current_time - self._last_received_heartbeat_time_ms
            if elapsed_time >= self._election_timeout_ms:
                logging.info("Election timeout reached. Starting election...")

                self._current_node.controller.start_election()
                return

            time.sleep(ITERATION_SLEEP_TIME_SEC)
