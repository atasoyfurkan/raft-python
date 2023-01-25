import os
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")


def getenv_required(key: str) -> str:
    value = os.getenv(key)
    assert value is not None, f"Please provide a valid {key}."
    return value


HOSTNAME = getenv_required("HOSTNAME")
PORT = int(getenv_required("PORT"))
