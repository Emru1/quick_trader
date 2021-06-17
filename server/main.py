from config import Config
from database import DatabaseHandler
from network import Server
from router import Router
from app import App

import queue
import threading


def main():
    print("Quick Trader server daemon\n\n")
    print("Loading config...")

    inqueue = queue.Queue()
    outqueue = queue.Queue()

    config = Config()
    config.print_config()
    database = DatabaseHandler()
    server = Server(inqueue, outqueue)
    routes = Router()
    app = App(inqueue, outqueue, routes)

    network_thread = threading.Thread(target=server.run)
    app_thread = threading.Thread(target=app.run)
    #    app_thread
    network_thread.start()
    app_thread.start()
    server.handle_auction()


if __name__ == '__main__':
    main()
