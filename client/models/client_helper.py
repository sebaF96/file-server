

class Constants:
    OPT_LEN_ERROR = "Error: Expected 2 options [-a | --address] and [-p | --port]"
    OPT_VALUE_ERROR = "Error: Port must be an integer bigger than 1024"
    CONNECTION_REFUSED_ERROR = "There's not a file server in the given (address, port) pair"

    PROMPT_COLOR = "\033[1;36m"
    OK_COLOR = "\033[0;92m"
    ERROR_COLOR = "\033[1;31m"
    RESET_COLOR = "\033[0m"

    OK_STATUS_CODE = 200
    ERROR_STATUS_CODE = 500
    INVALID_COMMAND = "Command not recognized"

    BUFFER_SIZE = 2048
    FILE_BUFFER_SIZE = 4096
    FILE_UPLOADED = "File successfully uploaded"
    FILE_DOWNLOADED = "File successfully downloaded"

    FILE_NOT_FOUND = "No such file"
    DIRECTORY_NOT_FOUND = "No such directory"
    DIRECTORY_EXISTS = "Directory already exists"
    DISCONNECTED_MESSAGE = "Disconnected from file-server"

    @staticmethod
    def prompt(address):
        return f"{Constants.PROMPT_COLOR}file-server@{address}{Constants.RESET_COLOR}$ "

    @staticmethod
    def connected_message(address, port):
        return f"Connected to File Server at {address} on port {port}"

    @staticmethod
    def thread_name(operation, filename):
        return f"Thr[{operation}]-{filename}"   # Thr[put]-Rute.pdf
