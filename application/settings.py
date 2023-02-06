import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Utility functions
def _getenv_required(key: str) -> str:
    value = os.getenv(key)
    assert value is not None, f"Please provide a valid {key}."

    logging.debug(f"Environment variable {key} = {value}")
    return value


# Environment variables
HOSTNAME = _getenv_required("HOSTNAME")
PORT = int(_getenv_required("PORT"))
NUMBER_OF_NODES = int(_getenv_required("NUMBER_OF_NODES"))
CLIENT_RETRY_TIMEOUT_MS = int(_getenv_required("CLIENT_RETRY_TIMEOUT_MS"))

# Global variables
NODE_HOSTNAMES = [f"node{i}" for i in range(NUMBER_OF_NODES)]
