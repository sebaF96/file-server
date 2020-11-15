#!/usr/bin/python3

import getopt
import sys
import models


def read_options() -> tuple:
    """
    Reads command-line options looking for address and port number to connect to, in case that one
    or both options are missing, it will print an error message and exit

    :return: a tuple with two values (the address and the port)
    """
    address = port = None
    (opt, arg) = getopt.getopt(sys.argv[1:], "a:p:", ["address=", "port="])

    if len(opt) != 2:
        print(f"Error: Expected 2 options [-a | --address] and [-p | --port]")
        sys.exit(0)

    for (option, argument) in opt:
        if option == "-p" or option == "--port":
            port = int(argument)
            if port < 1024:
                raise ValueError("Error: Port must be an integer bigger than 1024")
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
    client = models.Client(address, port)
    client.run()


if __name__ == '__main__':
    try:
        main()
    except getopt.GetoptError as ge:
        print("Error:", ge)
    except AssertionError:
        print("Error: Expected 2 options [-a | --address] and [-p | --port]")
    except ValueError as ve:
        print(ve)
