from collections import defaultdict
import datetime
import hashlib


class Constants:

    # Colors
    COLORS = defaultdict(None)
    COLORS["RED"] = "\033[1;31m"
    COLORS["YELLOW"] = "\033[1;33m"
    COLORS["PURPLE"] = "\033[1;35m"
    COLORS["GREEN"] = "\033[1;32m"
    COLORS["RESET"] = "\033[0m"

    # Connection
    OK_STATUS_CODE = 200
    ERROR_STATUS_CODE = 500
    OK_MESSAGE = "OK"
    DIRECTORY_EXISTS = "Directory already exists"
    DIRECTORY_DOESNT_EXISTS = "No such directory"
    FILE_EXISTS = "File already exists"
    FILE_DOESNT_EXISTS = "No such file"
    INVALID_COMMAND = "Invalid command or argument(s)"
    BAD_FORMED_MESSAGE = "Invalid command format, it doesn't respect the protocol"

    # Buffers
    BUFFER_SIZE = 2048
    FILE_BUFFER_SIZE = 4096

    # Main
    CERT_NOT_FOUND = "Certificate not found"
    MISSING_DOTENV = "Missing .env file with PATH_TO_CERT variable"
    INVALID_CERT_CHAIN = "SSL Error: Invalid cert chain"
    RESERVED_PORTS = "You can't use reserved ports"
    SERVED_STARTED = "File Server started at"
    LISTENING_MAIN = "Listening for connections at port"
    LISTENING_TRANSFERS = "Listening for transfers at port"
    EXITING = "Closing connections..."
    PORTS_VALUE_ERROR = "Ports must be positive integers"
    PORTS_ASSERTION_ERROR = "Main port and Transfer port can not be the same"

    READY_FLAG = b'10101010'
    TRANSFERS_TIMEOUT_SECONDS = 15
    HANDSHAKE_TIMEOUT_SECONDS = 10
    JOINER_INTERVAL_SECONDS = 60 * 5

    @staticmethod
    def date_time():
        now = datetime.datetime.now()
        year = '{:02d}'.format(now.year)
        month = '{:02d}'.format(now.month)
        day = '{:02d}'.format(now.day)
        hour = '{:02d}'.format(now.hour)
        minute = '{:02d}'.format(now.minute)

        # [16/11/2020 - 12:01]
        return f"[{day}/{month}/{year} - {hour}:{minute}]"


def print_colored(color: str, message: str):
    print(f"{Constants.COLORS[color.upper()]}{message}{Constants.COLORS['RESET']}")


def calculate_checksum(filepath):
    with open(filepath, 'rb') as file:
        checksum = hashlib.sha256(file.read())
        return checksum.hexdigest()
