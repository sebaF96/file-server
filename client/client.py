#!/usr/bin/python3

import getopt
import sys
import models
import socket
import ssl


def read_options() -> tuple:
    """
    Reads command-line options looking for address and port number to connect to, in case that one
    or both options are missing, it will print an error message and exit

    :return: a tuple with two values (the address and the port)
    """
    address = port = None
    (opt, arg) = getopt.getopt(sys.argv[1:], "a:p:", ["address=", "port="])

    if len(opt) != 2:
        print(models.Constants.OPT_LEN_ERROR)
        sys.exit(0)

    for (option, argument) in opt:
        if option == "-p" or option == "--port":
            port = int(argument)
            if port < 1024:
                raise ValueError(models.Constants.OPT_VALUE_ERROR)
        elif option == "-a" or option == "--address":
            address = argument

    assert port is not None and address is not None

    return address, port


def main() -> None:
    """
    Main client function, it will read command-line, create a models.Client instance
    and call its run() method.

    :return: None
    """
    address, port = read_options()
    context = ssl.create_default_context()
    try:
        context.load_verify_locations(models.Constants.PATH_TO_CERT)
    except FileNotFoundError:
        print(models.Constants.CERT_NOT_FOUND)
        exit()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((address, port))
    client_socket = context.wrap_socket(client_socket, server_hostname=models.Constants.SERVER_HOSTNAME)
    print(models.Constants.connected_message(address, port))

    client = models.Client(address, client_socket)
    client.run()


if __name__ == '__main__':
    try:
        main()
    except getopt.GetoptError as ge:
        print("Error:", ge)
    except AssertionError:
        print(models.Constants.OPT_LEN_ERROR)
    except ValueError as ve:
        print(ve)
    except ConnectionRefusedError:
        print(models.Constants.CONNECTION_REFUSED_ERROR)
    except OSError as oe:
        print(oe)
