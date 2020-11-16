#!/usr/bin/python3

import getopt
import sys
import socket
import src
import multiprocessing
import signal
import secrets


def handle_close(s, frame) -> None:
    """
    Custom handler for a clean exit on SIGINT or Ctrl-C

    :param s: signum
    :param frame: current stack frame
    :return: None
    """
    print("Closing connections...")
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
        raise ConnectionRefusedError("You can't use reserved ports")
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
    print('\nGot a connection from', address)
    conn = src.Connection(client_socket, address, SESSION_TOKEN, transfers_port)
    conn.start()
    print(f"Client {address} disconnected")


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
    transfer = src.Transfer(client_socket, address, SESSION_TOKEN)
    transfer.begin()


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
    print(f"Listening for transfers on port {transfer_port}")
    while True:
        transfer_socket.listen(16)
        client_socket, address = transfer_socket.accept()
        p = multiprocessing.Process(target=attend_transfer, args=(client_socket, address, SESSION_TOKEN))
        p.start()
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
