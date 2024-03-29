#!/usr/bin/python3

import getopt
import sys
import models
import socket
import ssl
import os
from dotenv import load_dotenv


def load_cert() -> None:
    """
    First function called on client run. It would search for a .env file containing
    the path to a SSL cert-chain file. If the file is missing, program will end

    :return: None
    """
    load_dotenv()
    if os.getenv("PATH_TO_CERT") is None:
        print(models.Constants.MISSING_DOTENV)
        exit()
    elif not os.path.isfile(os.getenv("PATH_TO_CERT")):
        print(models.Constants.CERT_NOT_FOUND)
        exit()


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
    context.check_hostname = False
    context.load_verify_locations(os.getenv("PATH_TO_CERT"))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((address, port))
    client_socket = context.wrap_socket(client_socket)
    print(models.Constants.connected_message(address, port))

    client = models.Client(address, client_socket, context)
    client.run()


if __name__ == '__main__':
    load_cert()
    try:
        main()
    except ConnectionRefusedError:
        print(models.Constants.CONNECTION_REFUSED_ERROR)
    except AssertionError:
        print(models.Constants.OPT_LEN_ERROR)
    except (getopt.GetoptError, ValueError, OSError, Exception) as e:
        print("Error:", e)

