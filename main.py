import logging
from pkg.controller import Controller
import settings  # load settings
from pkg.network_service import NetworkService


logging.debug("Executing main thread")

## instantiate the NetworkService class to make it garbage collectable when the program ends
## this is necessary because the socket might not be garbage collected automatically
NetworkService()

controller = Controller()

logging.debug("Finished main thread")
