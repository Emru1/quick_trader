from config import Config
from database import DatabaseHandler
from network import Server
import queue


def main():
    print("Quick Trader server daemon\n\n")
    print("Loading config...")

    inqueue = queue.Queue()
    outqueue = queue.Queue()

    config = Config()
    config.print_config()
    database = DatabaseHandler()
    server = Server(inqueue, outqueue)

    while True:
        server.handle_network()


if __name__ == '__main__':
    main()
