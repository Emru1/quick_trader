from config import Config
from database import DatabaseHandler


def main():
    print("Quick Trader server daemon\n\n")
    print("Loading config...")

    config = Config()
    config.print_config()
    database = DatabaseHandler()


if __name__ == '__main__':
    main()
