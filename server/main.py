from config import Config
from database import DatabaseHandler
from network import Server


def main():
    print("Quick Trader server daemon\n\n")
    print("Loading config...")

    config = Config()
    config.print_config()
    database = DatabaseHandler()
    server = Server()

    while True:
        server.handle_network()


if __name__ == '__main__':
    main()
