import logging
import pkg.settings as settings  # load settings
from pkg.controller import Controller
from pkg.services import NetworkService


logging.debug("Executing main thread")

## instantiate the NetworkService class to make it garbage collectable when the program ends
## this is necessary because the socket might not be garbage collected automatically
NetworkService()

controller = Controller()

logging.debug("Finished main thread")
