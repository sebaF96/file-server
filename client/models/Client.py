import socket
import os


class Client:
    def __init__(self, address, port):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((address, port))
        print(f"Connected to File Server at {address} on port {port}")

        self.__COMMANDS = {'pwd': self.pwd, 'lpwd': self.lpwd}
        self.__COMMANDS_ARGS = {'lcd': self.lcd}

    def run(self):
        while True:
            user_input = input("> ").split()

            if user_input[0] not in self.__COMMANDS and user_input[0] not in self.__COMMANDS_ARGS:
                print("Command not recognized")
                continue

            elif user_input[0] in self.__COMMANDS:
                self.__COMMANDS[user_input[0]]()

            elif user_input[0] in self.__COMMANDS_ARGS:
                self.__COMMANDS_ARGS[user_input[0]](user_input[1])

    @property
    def socket(self):
        return self.__socket

    @staticmethod
    def lpwd():
        print(os.getcwd())

    @staticmethod
    def lcd(route):
        os.chdir(route)

    def pwd(self):
        self.__socket.send('pwd'.encode())
        answer = self.__socket.recv(1024).decode()
        print(answer)

    def cd(self, route):
        self.__socket.send(f'cd {route}'.encode())
        answer = self.__socket.recv(1024).decode()
        print(answer)
