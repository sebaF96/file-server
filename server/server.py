#!/usr/bin/python3

import getopt
import sys
import socket
import src


def read_port():
    (opt, arg) = getopt.getopt(sys.argv[1:], 'p:')
    if len(opt) != 1:
        raise getopt.GetoptError("Expected one option [-p] with its argument (port number)")

    port = int(opt[0][1])
    if port < 1:
        raise ValueError
    return port


if __name__ == '__main__':
    local_address = socket.gethostbyname(socket.getfqdn())
    port = read_port()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    print('Server started at', local_address, 'on port', port)
    print('Waiting for connections...')

    while True:
        server_socket.listen(16)
        client_socket, address = server_socket.accept()
        print('\nGot a connection from', address)
        conn = src.Connection(client_socket, address)
        conn.start()
