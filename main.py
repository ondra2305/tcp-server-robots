from config import *
from server import Server


def main():
    my_server = Server()
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    my_socket.bind(SERVER_ADDR)
    my_server.start_server(my_socket)


if __name__ == "__main__":
    main()
