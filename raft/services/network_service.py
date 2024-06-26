import socket
from socket import error as socket_error
import logging
from settings import HOSTNAME, PORT


class NetworkService:
    serversocket = None

    def __init__(self):
        """initialize the serversocket"""
        self._get_serversocket()

    def __del__(self):
        NetworkService.close_serversocket()

    @classmethod
    def _get_serversocket(cls) -> socket.socket:
        if cls.serversocket is None:
            logging.debug(f"Initializing listener on {HOSTNAME}:{PORT}")
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind((HOSTNAME, PORT))
            serversocket.listen(100)
            cls.serversocket = serversocket

        return cls.serversocket

    @classmethod
    def close_serversocket(cls):
        if cls.serversocket is not None:
            cls.serversocket.close()
            cls.serversocket = None

    @classmethod
    def _listen_tcp_socket(cls) -> socket.socket:
        logging.debug(f"Accepting connections on {HOSTNAME}:{PORT}")
        serversocket = cls._get_serversocket()

        clientsocket, address = serversocket.accept()
        logging.debug(f"Received connection from {address}")

        return clientsocket

    @classmethod
    def receive_tcp_message(cls) -> str:
        clientsocket = cls._listen_tcp_socket()

        with clientsocket:
            data = clientsocket.recv(10240).decode("utf-8")

        logging.debug(f"Received data: {data}")
        return data

    @classmethod
    def send_tcp_message(cls, message: str, receiver_host: str) -> bool:
        logging.debug(f"Sending data to {receiver_host}:{PORT}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
                clientsocket.connect((receiver_host, PORT))
                clientsocket.sendall(str.encode(message))
            logging.debug(f"Sent data: {message}")
            return True
        except (socket.gaierror or ConnectionRefusedError or TimeoutError or socket_error) as exception:
            if type(exception) is socket.gaierror or type(exception) is ConnectionRefusedError:
                logging.debug(f"Connection to {receiver_host} refused")
            elif type(exception) is TimeoutError:
                logging.debug(f"Connection to {receiver_host} timed out")
            return False
