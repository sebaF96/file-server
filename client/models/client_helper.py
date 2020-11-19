import hashlib
import os


class Constants:
    OPT_LEN_ERROR = "Error: Expected 2 options [-a | --address] and [-p | --port]"
    OPT_VALUE_ERROR = "Error: Port must be an integer bigger than 1024"
    CONNECTION_REFUSED_ERROR = "There's not a file server in the given (address, port) pair"
    CERT_NOT_FOUND = "Certificate not found"
    MISSING_DOTENV = "Missing .env file with PATH_TO_CERT and HOST_NAME variables"

    PROMPT_COLOR = "\033[1;36m"
    OK_COLOR = "\033[0;92m"
    ERROR_COLOR = "\033[1;31m"
    BOLD_COLOR = "\033[1;37m"
    RESET_COLOR = "\033[0m"

    OK_STATUS_CODE = 200
    ERROR_STATUS_CODE = 500
    INVALID_COMMAND = "Command not recognized. Use 'help' to show available commands"

    BUFFER_SIZE = 2048
    FILE_BUFFER_SIZE = 4096
    FILE_UPLOADED = "File successfully uploaded"
    FILE_DOWNLOADED = "File successfully downloaded"

    FILE_NOT_FOUND = "No such file"
    DIRECTORY_NOT_FOUND = "No such directory"
    DIRECTORY_EXISTS = "Directory already exists"
    DISCONNECTED_MESSAGE = "Disconnected from file-server"
    HELP_COMMANDS = {
        "help": "show this message",
        "pwd": "show server's current working directory (remote)",
        "lpwd": "show your current working directory (local)",
        "ls     <route>": "list files and directories (remote)",
        "lls    <route>": "list files and directories (local)",
        "cd     [route]": "change server's current working directory (remote)",
        "lcd    [route]": "change your current working directory (local)",
        "get    [filename]": "download [filename] from the server (remote)",
        "put    [filename]": "upload [filename] to the server (remote)",
        "lmkdir [dirname]": "create a directory (local)",
        "mkdir  [dirname]": "create a directory (remote)",
        "exit": "close the connection and leave the program"
    }

    @staticmethod
    def prompt(address):
        return f"{Constants.PROMPT_COLOR}file-server@{address}{Constants.RESET_COLOR}$ "

    @staticmethod
    def show_help():
        print(f"{Constants.BOLD_COLOR}\nUSAGE\n{Constants.RESET_COLOR}")
        print("$ command")
        print("$ command [mandatory_arg]")
        print("$ command <optional_arg>")
        print(f"{Constants.BOLD_COLOR}\nCOMMANDS\n{Constants.RESET_COLOR}")
        for command, description in Constants.HELP_COMMANDS.items():
            print('{:<25s}{:<50s}'.format(command, description))
        print("")

    @staticmethod
    def connected_message(address, port):
        return f"Connected to File Server at {address} on port {port}"

    @staticmethod
    def thread_name(operation, filename):
        return f"Thr[{operation}]-{filename}"   # Thr[put]-Rute.pdf


def calculate_checksum(filepath):
    with open(filepath, 'rb') as file:
        checksum = hashlib.sha256(file.read())
        return checksum.hexdigest()
