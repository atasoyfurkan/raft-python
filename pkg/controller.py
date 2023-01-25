from pkg.network_service import NetworkService
import settings


class Controller:
    def __init__(self):
        # TODO: apply committed log while recovering
        self._network_service = NetworkService(settings.HOSTNAME, settings.PORT)
        pass

    def _listen_thread(self):
        received_data = self._network_service.listen_tcp_socket()

    def handle_client_read_request(self):
        raise NotImplementedError

    def handle_client_write_request(self):
        raise NotImplementedError
