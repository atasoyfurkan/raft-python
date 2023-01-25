from pkg.network_service import NetworkService
import settings

network_service = NetworkService(settings.HOSTNAME, settings.PORT)

data = network_service.listen_tcp_socket()
