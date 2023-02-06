import logging
import settings  # load settings
from controller import Controller
from services import NetworkService


logging.debug("Executing main thread")

"""
Instantiate the NetworkService class to make it garbage collectable when the program ends.
This is necessary because the socket might not be garbage collected automatically.
"""
NetworkService()

controller = Controller()

logging.debug("Finished main thread")
