from pkg.network_service import NetworkService
import settings
from time import sleep

network_service = NetworkService(settings.HOSTNAME, settings.PORT)

sleep(2)

network_service.send_tcp_message("Hello World!", "app2")
