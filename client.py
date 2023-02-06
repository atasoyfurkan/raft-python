import json
import logging
import time
import random
import threading
from pkg.services import NetworkService
import pkg.settings as settings

logging.info("Client is started")


def listen_thread():
    logging.info("Client is listening")
    while True:
        received_data = NetworkService.listen_tcp_socket()
        if received_data is None:
            logging.error("Received data is None")

        message = json.loads(received_data)
        logging.info(f"Client received message: {message}")


def send_read_request(hostname: str, receiver_hostname: str, value: str):
    message = {
        "method": "read_key_from_value",
        "args": {"hostname": hostname, "value": value},
    }
    logging.info(f"Client sending read to {receiver_hostname} for value {value}")

    NetworkService.send_tcp_message(json.dumps(message), receiver_hostname)


threading.Thread(target=listen_thread).start()

counter = 0
while True:
    time.sleep(5)

    random_node_index = random.randint(0, settings.NUMBER_OF_NODES - 1)
    receiver_hostname = f"node{random_node_index}"

    key = counter
    value = f"google.com/{key}"
    msg = json.dumps({"key": key, "value": value})
    message = {
        "method": "write",
        "args": {"hostname": settings.HOSTNAME, "msg": msg},
    }

    logging.info(f"Client sending write to {receiver_hostname}")

    if NetworkService.send_tcp_message(json.dumps(message), receiver_hostname):
        counter += 1
        time.sleep(3)
        send_read_request(hostname=settings.HOSTNAME, receiver_hostname=receiver_hostname, value=value)
    else:
        logging.error(f"Client failed to send write to {receiver_hostname}")
