import logging
import settings  # load settings
from client import Client
from services import NetworkService

logging.debug("Executing main thread")

"""
Instantiate the NetworkService class to make it garbage collectable when the program ends.
This is necessary because the socket might not be garbage collected automatically.
"""
NetworkService()

client = Client()
client.main()
