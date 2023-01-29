from __future__ import annotations
import time
import random
import logging
import threading
import os
import pkg.settings as settings

if os.environ.get("TYPE_CHECKING"):
    from pkg.states import Follower, Leader, Candidate


class ElectionTimeoutService:
    def __init__(self, current_node: Follower | Candidate | Leader):
        self._current_node = current_node
        self._election_timeout_ms = self._generate_election_timeout()
        self._last_received_heartbeat_time_ms = self._get_current_time_ms()
        self._stop_thread = False

        threading.Thread(target=self._election_timeout_thread).start()

        logging.debug(
            f"ElectionTimeoutService initialized with election_timeout_ms: {self._election_timeout_ms} and last_received_heartbeat_time_ms: {self._last_received_heartbeat_time_ms}"
        )

    def stop(self):
        self._stop_thread = True

    def receive_heartbeat(self):
        self._last_received_heartbeat_time_ms = self._get_current_time_ms()

    def _generate_election_timeout(self) -> int:
        return random.randint(
            settings.ELECTION_TIMEOUT_LOWER_MS, settings.ELECTION_TIMEOUT_UPPER_MS
        )

    def _get_current_time_ms(self) -> int:
        return int(time.time() * 1000)

    def _convert_ms_to_sec(self, ms: int) -> float:
        return float(ms) / 1000

    def _election_timeout_thread(self):
        logging.debug("Election timeout thread started.")

        while not self._stop_thread:
            current_time = self._get_current_time_ms()
            elapsed_time = current_time - self._last_received_heartbeat_time_ms
            if elapsed_time >= self._election_timeout_ms:
                logging.info("Election timeout reached. Starting election...")

                controller = self._current_node.controller
                self._current_node = controller.change_node_state("candidate")
                self._current_node.start_election()  # type: ignore

                self._election_timeout_ms = self._generate_election_timeout()
                self.receive_heartbeat()

            time.sleep(self._convert_ms_to_sec(settings.ITERATION_SLEEP_TIME_MS))

        logging.debug("Election timeout thread stopped")
