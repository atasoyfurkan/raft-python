import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Utility functions
def _getenv_required(key: str) -> str:
    value = os.getenv(key)
    assert value is not None, f"Please provide a valid {key}."

    logging.debug(f"Environment variable {key} = {value}")
    return value


def _get_other_node_hostnames(hostname, number_of_nodes) -> list[str]:
    node_hostnames = []
    for i in range(number_of_nodes):
        node_hostnames.append(f"node{i}")

    if hostname in node_hostnames:
        node_hostnames.remove(hostname)

    logging.debug(f"Other node hostnames: {node_hostnames}")
    return node_hostnames


# Environment variables
HOSTNAME = _getenv_required("HOSTNAME")
PORT = int(_getenv_required("PORT"))
NUMBER_OF_NODES = int(_getenv_required("NUMBER_OF_NODES"))
ELECTION_TIMEOUT_LOWER_MS = int(_getenv_required("ELECTION_TIMEOUT_LOWER_MS"))
ELECTION_TIMEOUT_UPPER_MS = int(_getenv_required("ELECTION_TIMEOUT_UPPER_MS"))
HEARTBEAT_TIMEOUT_MS = int(_getenv_required("HEARTBEAT_TIMEOUT_MS"))
ITERATION_SLEEP_TIME_MS = int(_getenv_required("ITERATION_SLEEP_TIME_MS"))

# Global variables
OTHER_NODE_HOSTNAMES = _get_other_node_hostnames(HOSTNAME, NUMBER_OF_NODES)
STORAGE_PATH = "/usr/src/storage"
