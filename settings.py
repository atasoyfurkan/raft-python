import os
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

# Utility functions
def _getenv_required(key: str) -> str:
    value = os.getenv(key)
    assert value is not None, f"Please provide a valid {key}."

    logging.info(f"Environment variable {key} = {value}")
    return value


def _get_other_node_hostnames(hostname, number_of_nodes) -> list[str]:
    node_hostnames = []
    for i in range(number_of_nodes):
        node_hostnames.append(f"node{i}")
    node_hostnames.remove(hostname)

    logging.info(f"Other node hostnames: {node_hostnames}")
    return node_hostnames


# Environment variables
HOSTNAME = _getenv_required("HOSTNAME")
PORT = int(_getenv_required("PORT"))
NUMBER_OF_NODES = int(_getenv_required("NUMBER_OF_NODES"))


# Global variables
OTHER_NODE_HOSTNAMES = _get_other_node_hostnames(HOSTNAME, NUMBER_OF_NODES)
