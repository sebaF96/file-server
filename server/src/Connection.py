import os
import json


class Connection:
    def __init__(self, client_socket, client_address, SESSION_TOKEN, transfers_port):
        self.__client_socket = client_socket
        self.__client_address = client_address
        self.__secret_token = SESSION_TOKEN
        self.__transfers_port = transfers_port
        os.chdir(os.getenv("HOME", default="/home"))

        self.__COMMANDS = {'pwd': self.pwd, 'ls': self.ls}
        self.__COMMANDS_ARGS = {'cd': self.cd, 'ls': self.ls, 'mkdir': self.mkdir, 'get': self.get, 'put': self.put}

    def start(self):
        while True:
            client_datagram = self.__client_socket.recv(2048).decode()
            if not client_datagram:
                break

            try:
                client_json = json.loads(client_datagram)
                command, argument = client_json["command"], client_json["argument"]
            except json.decoder.JSONDecodeError:
                self.send_response(500, "Invalid command format, it doesn't respect the protocol")
                continue

            if command in self.__COMMANDS and argument is None:
                self.__COMMANDS[command]()

            elif command in self.__COMMANDS_ARGS and argument:
                self.__COMMANDS_ARGS[command](argument)

            else:
                self.send_response(500, "Invalid command or argument(s)")

    def send_response(self, status_code, status_message, content=None):
        response = {
            "status_code": status_code,
            "status_message": status_message,
            "content": content
        }

        self.__client_socket.send(json.dumps(response).encode())

    def allow_transfer(self, operation, absolute_path, filesize=None):
        response = {
            "status_code": 200,
            "operation": operation,
            "absolute_path": absolute_path,
            "filesize": filesize,
            "token": self.__secret_token,
            "transfer_port": self.__transfers_port
        }

        self.__client_socket.send(json.dumps(response).encode())

    def pwd(self):
        working_directory = os.getcwd()
        self.send_response(200, "OK", working_directory)

    def ls(self, directory=None):
        try:
            output = os.listdir(directory) if directory else os.listdir()
            content = None if len(output) == 0 else "\n".join(output)

            self.send_response(200, "OK", content)
        except FileNotFoundError:
            self.send_response(500, "No such directory")

    def cd(self, directory: str):
        try:
            os.chdir(directory)
            self.send_response(200, "OK")
        except FileNotFoundError:
            self.send_response(500, "No such directory")

    def mkdir(self, directory: str):
        try:
            os.mkdir(directory)
            self.send_response(200, "OK")
        except FileExistsError:
            self.send_response(500, "Directory already exists")

    def get(self, filename: str):
        if not os.path.isfile(filename):
            self.send_response(500, "No such file")
        else:
            absolute_path = os.path.abspath(filename)
            filesize = os.path.getsize(filename)
            self.allow_transfer(operation="get", absolute_path=absolute_path, filesize=filesize)

    def put(self, filename: str):
        if os.path.isfile(filename):
            self.send_response(500, "File already exists")
        else:
            absolute_path = f"{os.getcwd()}/{filename}"
            self.allow_transfer(operation="put", absolute_path=absolute_path)
