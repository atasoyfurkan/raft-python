import socket
import logging
from settings import HOSTNAME, PORT
import json


class NetworkService:
    @classmethod
    def listen_tcp_socket(cls) -> str:
        logging.info(f"Listening on {HOSTNAME}:{PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOSTNAME, PORT))
            s.listen()
            conn, address = s.accept()
            logging.info(f"Received connection from {address}")

            with conn:
                data = conn.recv(10240).decode("utf-8")

        logging.info(f"Received data: {data}")
        return json.loads(data)

    @classmethod
    def send_tcp_message(cls, message: str, receiver_host: str) -> None:
        logging.info(f"Sending data to {receiver_host}:{PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((receiver_host, PORT))
            s.sendall(str.encode(message))
        logging.info(f"Sent data: {message}")
