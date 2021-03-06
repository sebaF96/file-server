import socket
import os
import json
import threading
from .FileManager import FileManager
from .client_helper import Constants


class Client:
    """
    Class representing a Client connected to the main socket of a file server
    """
    def __init__(self, address, client_socket, context):
        self.__socket = client_socket
        self.__server_address = address
        self.__context = context
        self.__prompt = Constants.prompt(address)
        if os.name == 'posix':
            os.chdir(os.getenv("HOME", default="/"))

        self.__REMOTE_COMMANDS = ['pwd', 'cd', 'ls', 'mkdir']
        self.__COMMANDS = {'lpwd': self.lpwd, 'lls': self.lls, 'help': self.show_help, 'clear': self.clear,
                           'c': self.clear, 'exit': self.disconnect, 'x': self.disconnect}
        self.__COMMANDS_ARGS = {'lcd': self.lcd, 'lls': self.lls, 'lmkdir': self.lmkdir, 'get': self.get, 'put': self.put}

    def run(self) -> None:
        """
        Client's main method, it reads stdin, execute local commands and send remote commands
        to the server, then it reads the answer and prints it to stdout. Client will be in
        this loop until he uses the 'exit' command

        :return: None
        """
        while True:
            user_input = input(self.__prompt).split()
            if not user_input:
                continue
            has_argument = len(user_input) >= 2
            command = user_input[0]
            argument = " ".join(user_input[1:]) if has_argument else None

            if command in self.__REMOTE_COMMANDS:
                self.communicate(command, argument)
            elif command in self.__COMMANDS and argument is None:
                self.__COMMANDS[command]()
            elif command in self.__COMMANDS_ARGS and argument:
                self.__COMMANDS_ARGS[command](argument)
            else:
                print(Constants.INVALID_COMMAND)

    def communicate(self, command: str, argument: str) -> None:
        """
        Sends a json-formatted message to the server and waits for an answer

        :param command: String representing the command to send
        :param argument: String representing the argument of said command, can be None
        :return: None
        """
        data = {"command": command, "argument": argument}
        self.__socket.send(json.dumps(data).encode())
        response = json.loads(self.__socket.recv(Constants.BUFFER_SIZE).decode())
        self.show_response(response)

    @staticmethod
    def show_response(response: dict) -> None:
        """
        Prints server's response to stdout

        :param response: Dictionary representing the json-formatted message from the server
        :return: None
        """
        end_color = Constants.RESET_COLOR
        if int(response['status_code']) == Constants.OK_STATUS_CODE:
            color = Constants.OK_COLOR
        else:
            color = Constants.ERROR_COLOR

        print(f"{color}{response['status_code']}: {response['status_message']}{end_color}\n")
        if response['content']:
            print(response['content'])

    def transfer(self, request: dict) -> None:
        """
        Sends a transfer request to the server. If the answer has a 200 status code,
        it creates a FileManager instance and delegates the transfer to it, otherwise
        prints the answer to stdout

        :param request: Dictionary representing the json-formatted message to send
        :return: None
        """
        self.__socket.send(json.dumps(request).encode())
        response = json.loads(self.__socket.recv(Constants.BUFFER_SIZE).decode())

        if int(response["status_code"]) == Constants.ERROR_STATUS_CODE:
            self.show_response(response)
        elif int(response["status_code"]) == Constants.OK_STATUS_CODE:
            transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transfer_socket = self.__context.wrap_socket(transfer_socket)
            transfer_socket.connect((self.__server_address, response["transfer_port"]))
            transfer = FileManager(transfer_socket, response)
            thread_name = Constants.thread_name(operation=request['command'], filename=request['argument'])
            thread = threading.Thread(target=transfer.begin, name=thread_name)
            thread.start()
            thread.join()

    def get(self, filename: str) -> None:
        """
        Formats a json message of a get request, and calls transfer() method with it

        :param filename: String representing the base name of the file to download
        :return: None
        """
        request = {"command": "get", "argument": filename}
        self.transfer(request)

    def put(self, filename: str) -> None:
        """
        Formats a json message of a put request, and calls transfer() method with it

        :param filename: String representing the base name of the file to upload
        :return: None
        """
        if os.path.isfile(filename):
            request = {"command": "put", "argument": filename}
            self.transfer(request)
        else:
            print(Constants.FILE_NOT_FOUND)

    """Local commands"""
    @staticmethod
    def lpwd() -> None:
        """
        Prints the current working directory (client) to stdout

        :return: None
        """
        print(os.getcwd())

    @staticmethod
    def lcd(directory: str) -> None:
        """
        Changes the current working directory to the given one, if exists

        :param directory: String representing the directory name
        :return: None
        """
        if os.path.isdir(directory):
            os.chdir(directory)
        else:
            print(Constants.DIRECTORY_NOT_FOUND)

    @staticmethod
    def lls(directory: str = None) -> None:
        """
        List the given directory or the current directory if None is given,
        and prints it to stdout

        :param directory: String representing the directory to list. None by default
        :return: None
        """
        try:
            output = os.listdir(directory) if directory else os.listdir()
            content = None if len(output) == 0 else "\n".join(output)
            print(content)
        except (FileNotFoundError, NotADirectoryError):
            print(Constants.DIRECTORY_NOT_FOUND)

    @staticmethod
    def lmkdir(directory: str) -> None:
        """
        Creates a directory with the given name if that directory doesn't exists

        :param directory: Name of the directory to create
        :return: None
        """
        try:
            os.mkdir(directory)
        except FileExistsError:
            print(Constants.DIRECTORY_EXISTS)

    @staticmethod
    def clear() -> None:
        """
        Clears the command line

        :return: None
        """
        os.system("clear")

    def disconnect(self) -> None:
        """
        Closes the connection with the server and leaves the program

        :return: None
        """
        self.__socket.close()
        print(Constants.DISCONNECTED_MESSAGE)
        exit(0)

    @staticmethod
    def show_help() -> None:
        """
        Prints to stdout a list of the known local and remote commands with a short description
        :return: None
        """
        Constants.show_help()
