import os


class Connection:
    def __init__(self, client_socket, client_address):
        self.__client_socket = client_socket
        self.__client_address = client_address
        self.__COMMANDS = {'pwd': self.pwd, 'ls': self.ls}

    def start(self):
        while True:
            client_command = self.__client_socket.recv(1024).decode()
            if client_command not in self.__COMMANDS:
                continue

            self.__COMMANDS[client_command]()

    def send(self, content):
        self.__client_socket.send(content.encode())

    def pwd(self):
        output = os.getcwd()
        self.send(output)

    def ls(self):
        output = os.listdir()
        self.send("\n".join(output))
