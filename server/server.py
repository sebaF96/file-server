#!/usr/bin/python3

import getopt
import sys
import socket
import src
import multiprocessing
import signal
import secrets


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


def attend_client(client_socket, address: str, SESSION_TOKEN: str, transfers_port: int) -> None:
    print('\nGot a connection from', address)
    conn = src.Connection(client_socket, address, SESSION_TOKEN, transfers_port)
    conn.start()
    print(f"Client {address} disconnected")


def attend_transfer(client_socket, address: str, SESSION_TOKEN: str) -> None:
    transfer = src.Transfer(client_socket, address, SESSION_TOKEN)
    transfer.begin()


def listen_for_transfers(transfer_socket, transfer_port: int, SESSION_TOKEN: str) -> None:
    print(f"Listening for transfers on port {transfer_port}")
    while True:
        transfer_socket.listen(16)
        client_socket, address = transfer_socket.accept()
        p = multiprocessing.Process(target=attend_transfer, args=(client_socket, address, SESSION_TOKEN))
        p.start()
        del client_socket


def main() -> None:
    local_address = socket.gethostbyname(socket.getfqdn() + ".local")
    main_port, transfer_port = read_ports()
    SESSION_TOKEN = secrets.token_hex(64)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', main_port))
    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.bind(('', transfer_port))

    print(f"Server started at {local_address}")
    print(f"Listening for connections at port {main_port}")
    multiprocessing.Process(target=listen_for_transfers, args=(transfer_socket, transfer_port, SESSION_TOKEN)).start()
    print('Waiting for connections...')

    while True:
        server_socket.listen(16)
        client_socket, address = server_socket.accept()
        th = multiprocessing.Process(target=attend_client, args=(client_socket, address, SESSION_TOKEN, transfer_port))
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
