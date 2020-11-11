#!/usr/bin/python3

import getopt
import sys
import socket
import src
import multiprocessing
import threading
import signal


def handle_close(s, frame) -> None:
    print("Closing connections...")
    sys.exit(0)


def read_ports() -> tuple:
    (opt, arg) = getopt.getopt(sys.argv[1:], 'p:t:', ['port=', 'transfer-port='])
    port, transfer_port = 8080, 3000

    for (option, argument) in opt:
        if option == '-p' or option == '--port':
            port = int(argument)
        elif option == '-t' or option == '--transfer-port':
            transfer_port = int(argument)

    if port < 1024 or transfer_port < 1024:
        raise ConnectionRefusedError("You can't use reserved ports")
    return port, transfer_port


def attend_client(client_socket, address) -> None:
    print('\nGot a connection from', address)
    conn = src.Connection(client_socket, address)
    conn.start()
    print(f"Client {address} disconnected")


def listen_for_transfers(transfer_socket: socket.socket, transfer_port: int) -> None:
    print(f"Listening for transfers on port {transfer_port}")
    while True:
        transfer_socket.listen(16)
        client_socket, address = transfer_socket.accept()
        th = multiprocessing.Process(target=attend_client, args=(client_socket, address))
        th.start()


def main() -> None:
    local_address = socket.gethostbyname(socket.getfqdn() + ".local")
    main_port, transfer_port = read_ports()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', main_port))
    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.bind(('', transfer_port))

    print(f"Server started at {local_address}")
    print(f"Listening for connections at port {main_port}")
    threading.Thread(target=listen_for_transfers, args=(transfer_socket, transfer_port), daemon=True).start()
    print('Waiting for connections...')

    while True:
        server_socket.listen(16)
        client_socket, address = server_socket.accept()
        th = multiprocessing.Process(target=attend_client, args=(client_socket, address))
        th.start()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_close)
    try:
        main()
    except getopt.GetoptError as ge:
        print("Error:", ge)
    except ConnectionRefusedError as cre:
        print("Error:", cre)
    except ValueError:
        print("Ports must be positive integers")
    except OSError as oe:
        print(oe)
