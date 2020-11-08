#!/usr/bin/python3

import getopt
import sys
import controllers.Client as cl


def read_options():
    address: None
    address = port = None
    (opt, arg) = getopt.getopt(sys.argv[1:], 'a:p:l:')

    if len(opt) < 2:
        print(f"Error: Expected 2 options [-a | --address] and [-p | --port]")
        sys.exit(0)

    for (option, argument) in opt:
        if option == '-p':
            port = int(argument)
        elif option == '-a':
            address = argument

    assert port is not None and address is not None

    return address, port


if __name__ == '__main__':
    address, port = read_options()
    client = cl.Client(address, port)
    client.run()
