from collections import defaultdict


class Constants:

    COLORS = defaultdict(None)
    COLORS["RED"] = "\033[1;31m"
    COLORS["YELLOW"] = "\033[1;33m"
    COLORS["PURPLE"] = "\033[1;35m"
    COLORS["GREEN"] = "\033[1;32m"
    COLORS["RESET"] = "\033[0m"

    OK_STATUS_CODE = 200
    ERROR_STATUS_CODE = 500
    OK_MESSAGE = "OK"
    DIRECTORY_EXISTS = "Directory already exists"
    DIRECTORY_DOESNT_EXISTS = "No such directory"
    FILE_EXISTS = "File already exists"
    FILE_DOESNT_EXISTS = "No such file"
    INVALID_COMMAND = "Invalid command or argument(s)"
    BAD_FORMED_MESSAGE = "Invalid command format, it doesn't respect the protocol"

    BUFFER_SIZE = 2048
    FILE_BUFFER_SIZE = 4096


def print_colored(color: str, message: str):
    print(f"{Constants.COLORS[color.upper()]}{message}{Constants.COLORS['RESET']}")


if __name__ == '__main__':
    print(Constants.OK_MESSAGE)
    print(Constants.OK_STATUS_CODE)