#!/usr/bin/python3

import getopt
import sys
import socket
import src
import multiprocessing
import os
import threading
import signal
import secrets
import ssl


def handle_close(s, frame) -> None:
    """
    Custom handler for a clean exit on SIGINT or Ctrl-C

    :param s: signum
    :param frame: current stack frame
    :return: None
    """
    print(src.Constants.EXITING)
    exit(0)


def read_ports() -> tuple:
    """
    Reads command-line options looking for ports numbers to run the server in, in case that one
    or both ports are missing, it will use default ones (8080 for main connection and 3000 for transfers)

    :return: a tuple with two integer values (the main port and the transfer port)
    """
    (opt, arg) = getopt.getopt(sys.argv[1:], 'p:t:', ['port=', 'transfer-port='])
    port, transfer_port = 8080, 3000

    for (option, argument) in opt:
        if option == '-p' or option == '--port':
            port = int(argument)
        elif option == '-t' or option == '--transfer-port':
            transfer_port = int(argument)

    if port < 1024 or transfer_port < 1024:
        raise ConnectionRefusedError(src.Constants.RESERVED_PORTS)

    assert port != transfer_port
    return port, transfer_port


def attend_client(client_socket, address: str, SESSION_TOKEN: str, transfers_port: int) -> None:
    """
    Handler for a client connection to the main port. It creates a Connection instance and call
    its start() method

    :param client_socket: socket object returned by accept() method of server main socket
    :param address: tuple representing client's address and port, also returned by accept() method
    :param SESSION_TOKEN: server security token. Client needs it to request file transfers
    :param transfers_port: port number where server is listening for transfers. Client needs it to request
    file transfers
    :return: None
    """
    src.print_colored(color="GREEN", message=f"{src.Constants.date_time()} Got a connection from {address}")
    conn = src.Connection(client_socket, address, SESSION_TOKEN, transfers_port)
    try:
        conn.start()
    except ConnectionResetError:
        pass
    src.print_colored(color="RED", message=f"{src.Constants.date_time()} Client {address} disconnected")


def attend_transfer(client_socket, address: str, SESSION_TOKEN: str) -> None:
    """
    Handler for a client connection to the transfer port. It creates a Transfer instance and call
    its begin method. This function ends when said transfer is done

    :param client_socket: socket object returned by accept() method of server transfer socket
    :param address: tuple representing client's address and port, also returned by accept() method
    :param SESSION_TOKEN: Server security token. Transfer instance will request the client for a
    token and compare it with this one before sending or receiving any file
    :return: None
    """
    try:
        transfer = src.Transfer(client_socket, address, SESSION_TOKEN)
        transfer.begin()
    except ConnectionResetError:
        pass


def listen_for_transfers(transfer_socket, transfer_port: int, SESSION_TOKEN: str) -> None:
    """
    Server's listen_for_ever method for file transfers. When a Client is connected, it delegates
    the job to the attend_transfer method

    :param transfer_socket: socket object where the server is going to listen for transfers
    :param transfer_port: port number of associated with the given socket.
    :param SESSION_TOKEN: Server security token. It needs to be passed to the connection handler,
    in this case, attend_transfer()
    :return: None
    """
    print(f"{src.Constants.LISTENING_TRANSFERS} {transfer_port}")
    transfer_socket.listen(5)
    while True:
        client_socket, address = transfer_socket.accept()
        thr = threading.Thread(target=attend_transfer, args=(client_socket, address, SESSION_TOKEN))
        thr.start()
        del client_socket


def main() -> None:
    """
    Main server function, it will:
    - create both main and transfers sockets
    - generate a random security token
    - delegate the transfer's server_for_ever to listen_for_transfers() function
    - act as a listen_for_ever for server's main socket.

    :return: None
    """
    local_address = socket.gethostbyname(socket.getfqdn() + ".local")
    main_port, transfer_port = read_ports()
    SESSION_TOKEN = secrets.token_urlsafe(64)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        context.load_cert_chain(src.Constants.PATH_TO_CERT)
    except OSError:
        print(src.Constants.CERT_NOT_FOUND)
        exit()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', main_port))
    server_socket = context.wrap_socket(server_socket, server_side=True)

    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.bind(('', transfer_port))
    transfer_socket = context.wrap_socket(transfer_socket, server_side=True)

    print(f"{src.Constants.SERVED_STARTED} {local_address}")
    print(f"{src.Constants.LISTENING_MAIN} {main_port}")
    threading.Thread(target=listen_for_transfers, args=(transfer_socket, transfer_port, SESSION_TOKEN), daemon=True).start()
    print('Waiting for connections...')
    server_socket.listen(5)

    while True:
        try:
            client_socket, address = server_socket.accept()
            process = multiprocessing.Process(target=attend_client, args=(client_socket, address, SESSION_TOKEN, transfer_port))
            process.start()
        except ssl.SSLError:
            continue


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_close)
    try:
        main()
    except getopt.GetoptError as ge:
        print("Error:", ge)
    except ConnectionRefusedError as cre:
        print("Error:", cre)
    except ValueError:
        print(src.Constants.PORTS_VALUE_ERROR)
    except OSError as oe:
        print(oe)
    except AssertionError:
        print(src.Constants.PORTS_ASSERTION_ERROR)
