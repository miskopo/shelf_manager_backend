import logging
from logging import getLogger


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = getLogger("pantry")