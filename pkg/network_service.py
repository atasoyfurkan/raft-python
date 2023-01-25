import socket
import logging


class NetworkService:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        logging.info(f"NetworkService initialized with host: {host} and port: {port}")

    def _listen_for_connection(self) -> socket.socket:
        logging.info(f"Listening on {self._host}:{self._port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))
            s.listen()
            client, address = s.accept()
            logging.info(f"Received connection from {address}")
            return client

    def listen_tcp_socket(self) -> str:
        with self._listen_for_connection() as s:
            data = s.recv(10240).decode("utf-8")

        logging.info(f"Received data: {data}")
        return data

    def send_tcp_message(self, message: str, receiver: str) -> None:
        logging.info(f"Sending data to {receiver}:{self._port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((receiver, self._port))
            client.sendall(str.encode(message))
        logging.info(f"Sent data: {message}")
