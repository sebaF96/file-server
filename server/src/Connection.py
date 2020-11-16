import os
import json
from .server_helper import Constants, print_colored


class Connection:
    """
    Class representing a connection with a client from the server point of view. An instance of this
    class is created each time a client connects to the main socket. It will change the current working directory
    to the one stored on the server's system $HOME environment variable and start receiving commands, executing them,
    and sending the answer, until the client is disconnected
    """
    def __init__(self, client_socket, client_address, SESSION_TOKEN, transfers_port):
        self.__client_socket = client_socket
        self.__client_address = client_address
        self.__secret_token = SESSION_TOKEN
        self.__transfers_port = transfers_port
        os.chdir(os.getenv("HOME", default="/home"))

        self.__COMMANDS = {'pwd': self.pwd, 'ls': self.ls}
        self.__COMMANDS_ARGS = {'cd': self.cd, 'ls': self.ls, 'mkdir': self.mkdir, 'get': self.get, 'put': self.put}

    def start(self) -> None:
        """
        Connection listen_for_ever method. It will receive commands from the client,
        execute them and sends answers

        :return: None
        """
        while True:
            client_datagram = self.__client_socket.recv(Constants.BUFFER_SIZE).decode()
            if not client_datagram:
                break
            try:
                client_json = json.loads(client_datagram)
                command, argument = client_json["command"], client_json["argument"]
            except json.decoder.JSONDecodeError:
                self.send_response(Constants.ERROR_STATUS_CODE, Constants.BAD_FORMED_MESSAGE)
                continue
            if command in self.__COMMANDS and argument is None:
                self.__COMMANDS[command]()
            elif command in self.__COMMANDS_ARGS and argument:
                self.__COMMANDS_ARGS[command](argument)
            else:
                self.send_response(Constants.ERROR_STATUS_CODE, Constants.INVALID_COMMAND)

    def send_response(self, status_code: int, status_message: str, content: str = None) -> None:
        """
        Sends a json-formatted answer to the client
        :param status_code: Integer representing the last command status code
        :param status_message: Descriptive message associated with the status code
        :param content: Standard output of the last executed command, if any, None otherwise

        :return: None
        """
        response = {
            "status_code": status_code,
            "status_message": status_message,
            "content": content
        }

        self.__client_socket.send(json.dumps(response).encode())

    def allow_transfer(self, operation: str, absolute_path: str, filesize: int = None):
        """
        Method called when a transfer request from the client is marked as valid by the server.
        It will send the transfer's metadata in a json-formatted message to the client

        :param operation: either 'put' or 'get' depending if the client wants to upload or to download a file
        :param absolute_path: absolute path to the file in server's system
        :param filesize: if the file is in server's system and client wants to download it, this field
        will represent the size of that file in bytes
        :return: None
        """
        response = {
            "status_code": 200,
            "operation": operation,
            "absolute_path": absolute_path,
            "filesize": filesize,
            "token": self.__secret_token,
            "transfer_port": self.__transfers_port
        }

        self.__client_socket.send(json.dumps(response).encode())

    def pwd(self) -> None:
        """
        Checks for server's current working directory and sends the output to the client in a json-formatted message

        :return: None
        """
        working_directory = os.getcwd()
        self.send_response(Constants.OK_STATUS_CODE, Constants.OK_STATUS_CODE, working_directory)

    def ls(self, directory=None):
        """
        Lists the given directory or the current directory if none is given,
        and sends the output to the client in a json-formatted message

        :param directory: String representing the directory to list. None by default
        :return: None
        """
        try:
            output = os.listdir(directory) if directory else os.listdir()
            content = None if len(output) == 0 else "\n".join(output)

            self.send_response(Constants.OK_STATUS_CODE, Constants.OK_MESSAGE, content)
        except FileNotFoundError:
            self.send_response(Constants.ERROR_STATUS_CODE, Constants.DIRECTORY_DOESNT_EXISTS)
        except NotADirectoryError:
            self.send_response(Constants.ERROR_STATUS_CODE, Constants.DIRECTORY_DOESNT_EXISTS)

    def cd(self, directory: str) -> None:
        """
        Changes the current working directory to the given one if exists,
        and sends the output to the client in a json-formatted message

        :param directory: String representing the directory name
        :return: None
        """
        if os.path.isdir(directory):
            os.chdir(directory)
            self.send_response(Constants.OK_STATUS_CODE, Constants.OK_MESSAGE)
        else:
            self.send_response(Constants.ERROR_STATUS_CODE, Constants.DIRECTORY_DOESNT_EXISTS)

    def mkdir(self, directory: str) -> None:
        """
        Creates a directory with the given name if that directory doesn't exists,
        and sends the output to the client in a json-formatted message

        :param directory: Name of the directory to create
        :return: None
        """
        try:
            os.mkdir(directory)
            self.send_response(Constants.OK_STATUS_CODE, Constants.OK_MESSAGE)
        except FileExistsError:
            self.send_response(Constants.ERROR_STATUS_CODE, Constants.DIRECTORY_EXISTS)

    def get(self, filename: str) -> None:
        """
        Handles a get request from the client. Checks if the requested file exists
        and sends the answer to the client in a json-formatted message

        :param filename: String representing the filename that client is asking for
        :return: None
        """
        if not os.path.isfile(filename):
            self.send_response(Constants.ERROR_STATUS_CODE, Constants.FILE_DOESNT_EXISTS)
        else:
            absolute_path = os.path.abspath(filename)
            filesize = os.path.getsize(filename)
            self.allow_transfer(operation="get", absolute_path=absolute_path, filesize=filesize)

    def put(self, filename: str) -> None:
        """
        Handles a put request from the client. Checks if the requested file doesn't exists
        and sends the answer to the client in a json-formatted message

        :param filename: String representing the filename that client wants to upload
        :return: None
        """
        if os.path.isfile(filename):
            self.send_response(Constants.ERROR_STATUS_CODE, Constants.FILE_EXISTS)
        else:
            absolute_path = f"{os.getcwd()}/{filename}"
            self.allow_transfer(operation="put", absolute_path=absolute_path)
