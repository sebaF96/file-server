#!/usr/bin/python3

import getopt
import sys
import socket
import src
import os
import multiprocessing
import threading
import signal
import secrets
import ssl
from dotenv import load_dotenv
import time


PROCESSES_LIST = []


def load_cert() -> None:
    """
    First function called on server run. It would search for a .env file containing
    the path to a SSL cert-chain file. If the file is missing, program will end

    :return: None
    """
    load_dotenv()
    if os.getenv("PATH_TO_CERT") is None:
        print(src.Constants.MISSING_DOTENV)
        exit()
    elif not os.path.isfile(os.getenv("PATH_TO_CERT")):
        print(src.Constants.CERT_NOT_FOUND)
        exit()


def handle_close(s, frame) -> None:
    """
    Custom handler for a clean exit on SIGINT or Ctrl-C

    :param s: signum
    :param frame: current stack frame
    :return: None
    """
    print(src.Constants.EXITING)
    exit(0)


def joiner() -> None:
    """
    Recurrent background task dedicated to join finished processes
    """
    while True:
        time.sleep(src.Constants.JOINER_INTERVAL_SECONDS)
        global PROCESSES_LIST
        for p in PROCESSES_LIST:
            if p.is_alive():
                continue
            p.join()
            PROCESSES_LIST.remove(p)


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


def perform_handshake(accepted_socket: ssl.SSLSocket) -> None:
    """
    Tries to perform a TLS handshake, if handshake don't succeed in 10 seconds, it closes the
    connection

    :param accepted_socket: SSLSocket object wrapping an accepted client socket
    :return: None
    """
    accepted_socket.settimeout(src.Constants.HANDSHAKE_TIMEOUT_SECONDS)
    try:
        accepted_socket.do_handshake()
        accepted_socket.settimeout(None)
    except (socket.timeout, ssl.SSLError, OSError):
        accepted_socket.close()
        exit(0)


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
    perform_handshake(client_socket)
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
    perform_handshake(client_socket)
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
        try:
            client_socket, address = transfer_socket.accept()
            thr = threading.Thread(target=attend_transfer, args=(client_socket, address, SESSION_TOKEN))
            thr.start()
            del client_socket
        except (ssl.SSLError, OSError, Exception):
            continue


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
        context.load_cert_chain(os.getenv("PATH_TO_CERT"))
    except ssl.SSLError:
        print(src.Constants.INVALID_CERT_CHAIN)
        exit()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', main_port))
    server_socket = context.wrap_socket(server_socket, server_side=True, do_handshake_on_connect=False)

    transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transfer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transfer_socket.bind(('', transfer_port))
    transfer_socket = context.wrap_socket(transfer_socket, server_side=True, do_handshake_on_connect=False)

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
            PROCESSES_LIST.append(process)
            del client_socket
        except (ssl.SSLError, OSError, Exception):
            continue


if __name__ == '__main__':
    load_cert()
    signal.signal(signal.SIGINT, handle_close)
    threading.Thread(target=joiner, daemon=True).start()
    try:
        main()
    except (getopt.GetoptError, ConnectionResetError, OSError, Exception) as e:
        print("Error:", e)
    except ValueError:
        print(src.Constants.PORTS_VALUE_ERROR)
    except AssertionError:
        print(src.Constants.PORTS_ASSERTION_ERROR)
