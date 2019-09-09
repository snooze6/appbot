# Apps
import logging

from bot import Appbot

appbot = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = Appbot(time=86400, handle=True)
    # bot = Appbot(time=None, handle=True)
