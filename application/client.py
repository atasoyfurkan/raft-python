import json
import logging
import time
import random
import threading
from services import NetworkService
import settings


class Client:
    def __init__(self):
        logging.debug("Client is started")

        self.requests = {}
        self.current_leader = self.choose_random_node()

        threading.Thread(target=self.listen_thread).start()

    def listen_thread(self):
        logging.debug("Client is listening")

        while True:
            received_data = NetworkService.receive_tcp_message()

            if received_data is None:
                logging.error("Received data is None")

            message = json.loads(received_data)
            logging.debug(f"Client received message: {message}")

            method = message["method"]
            args = message["args"]

            if method == "write_ack":
                self.receive_write_ack(
                    success=args["success"],
                    log_entry=args["log_entry"],
                    leader_hostname=args["leader"],
                    request_id=args["request_id"],
                )
            elif method == "read_ack":
                self.receive_read_ack(
                    success=args["success"],
                    result=args["result"],
                    leader_hostname=args["leader"],
                    sender_hostname=args["sender_hostname"],
                    request_id=args["request_id"],
                )

    def main(self):
        counter = 0
        while True:
            time.sleep(5)

            key = str(counter)
            value = f"google.com/{key}"

            success = self.send_write_request(receiver_hostname=self.current_leader, key=key, value=value)

            if success:
                time.sleep(2)
                self.send_read_request(value=value)
            else:
                logging.error(
                    f"Client failed to send write to leader {self.current_leader}. Retrying with a random node."
                )
                self.current_leader = self.choose_random_node()

            counter += 1

    def choose_random_node(self) -> str:
        random_node_index = random.randint(0, settings.NUMBER_OF_NODES - 1)
        return settings.NODE_HOSTNAMES[random_node_index]

    def send_write_request(self, receiver_hostname: str, key: str, value: str) -> bool:
        msg = json.dumps({"key": key, "value": value})
        request_id = f"{settings.HOSTNAME}-{time.time_ns()}"
        message = {
            "method": "write",
            "args": {"hostname": settings.HOSTNAME, "request_id": request_id, "msg": msg},
        }
        self.requests[request_id] = {
            "message": message,
            "ack_count": 0,
        }

        logging.info(f"Client sending write to {receiver_hostname}")
        return NetworkService.send_tcp_message(json.dumps(message), receiver_hostname)

    def send_read_request(self, value: str):
        request_id = f"{settings.HOSTNAME}-{time.time_ns()}"
        message = {
            "method": "read_key_from_value",
            "args": {"hostname": settings.HOSTNAME, "request_id": request_id, "value": value},
        }
        self.requests[request_id] = {
            "message": message,
            "ack_count": 0,
        }

        for node_hostname in settings.NODE_HOSTNAMES:
            logging.info(f"Client sending read to {node_hostname} for value {value}")
            NetworkService.send_tcp_message(json.dumps(message), node_hostname)

    def receive_write_ack(self, success: bool, log_entry: dict, leader_hostname: str, request_id: str):
        if request_id not in self.requests:
            logging.error("Client received write ack for unknown request")
            return

        if success:
            logging.info(f"Client received write ack for {log_entry}")
            self.current_leader = leader_hostname
            del self.requests[request_id]
        else:
            logging.info(f"Client send write to wrong leader. Redirecting to leader: {leader_hostname}...")
            if not leader_hostname:
                logging.info(
                    f"Client received write ack without leader. Waiting {settings.CLIENT_RETRY_TIMEOUT_MS} ms and randomly choosing a node..."
                )
                time.sleep(float(settings.CLIENT_RETRY_TIMEOUT_MS) / 1000)
                leader_hostname = self.choose_random_node()

            msg = json.loads(self.requests[request_id]["message"]["args"]["msg"])
            key = msg["key"]
            value = msg["value"]

            self.send_write_request(receiver_hostname=leader_hostname, key=key, value=value)

    def receive_read_ack(
        self, success: bool, result: str, leader_hostname: str, sender_hostname: str, request_id: str
    ):
        if request_id not in self.requests:
            logging.debug("Client received read ack for already processed request (quorum reached))")
            return

        logging.info(f"Client received read ack for {result}")

        self.requests[request_id]["ack_count"] += 1

        if success:
            logging.debug(f"Client received non-empty read ack from {sender_hostname}, result: {result}")
            self.requests[request_id]["result"] = result

        if self.requests[request_id]["ack_count"] > settings.NUMBER_OF_NODES / 2:
            logging.info(f"Client received read ack from quorum of nodes")
            logging.info(
                f"Received URL: {self.requests[request_id]['result'] or 'No result'} for id: {self.requests[request_id]['message']['args']['value']}"
            )
            del self.requests[request_id]
