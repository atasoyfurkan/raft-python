import json
import logging
import time
import random
from pkg.services import NetworkService
import pkg.settings as settings

logging.info("Client is started")

counter = 0

while True:
    time.sleep(5)

    random_node_index = random.randint(0, settings.NUMBER_OF_NODES - 1)
    receiver_hostname = f"node{random_node_index}"
    message = {
        "method": "write",
        "args": {"msg": f"Message {counter}"},
    }

    logging.info(f"Client sending write to {receiver_hostname}")

    if NetworkService.send_tcp_message(json.dumps(message), receiver_hostname):
        counter += 1
    else:
        logging.error(f"Client failed to send write to {receiver_hostname}")
