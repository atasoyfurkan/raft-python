from __future__ import annotations
import threading
import pkg.settings as settings
import logging
import time
import os

if os.environ.get("TYPE_CHECKING"):
    from pkg.states import Leader


class HeartbeatService:
    def __init__(self, leader: Leader):
        self._leader = leader
        self._stop_thread = False

        threading.Thread(target=self._heartbeat_thread).start()

        logging.debug(f"HearbeatService initialized")

    def stop(self):
        self._stop_thread = True

    def _convert_ms_to_sec(self, ms: int) -> float:
        return float(ms) / 1000

    def _heartbeat_thread(self):
        logging.debug("Heartbeat thread started.")

        while not self._stop_thread:
            for follower_hostname in settings.OTHER_NODE_HOSTNAMES:
                self._leader.replicate_log(follower_hostname)

            time.sleep(self._convert_ms_to_sec(settings.HEARTBEAT_TIMEOUT_MS))
