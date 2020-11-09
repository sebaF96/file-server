import socket
import os
import json


class Client:
    def __init__(self, address, port):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((address, port))
        print(f"Connected to File Server at {address} on port {port}")
        self.__prompt = f"\033[1;34mfile-server@{address}$\033[0m "

        self.__REMOTE_COMMANDS = ['pwd', 'cd', 'ls']
        self.__COMMANDS = {'lpwd': self.lpwd, 'lls': self.lls, 'exit': self.disconnect, 'help': self.show_help}
        self.__COMMANDS_ARGS = {'lcd': self.lcd, 'lls': self.lls}

    def run(self):
        while True:
            user_input = input(self.__prompt).split()
            has_argument = len(user_input) == 2
            command = user_input[0]
            argument = user_input[1] if has_argument else None

            if command in self.__REMOTE_COMMANDS:
                self.communicate(command, argument)

            elif command in self.__COMMANDS and argument is None:
                self.__COMMANDS[command]()

            elif command in self.__COMMANDS_ARGS and argument:
                self.__COMMANDS_ARGS[command](argument)

            else:
                print("Command not recognized")

    def communicate(self, command, argument):
        data = {"command": command, "argument": argument}
        self.__socket.send(json.dumps(data).encode())
        response = json.loads(self.__socket.recv(2048).decode())
        self.show_response(response)

    @staticmethod
    def show_response(response: dict):
        end_color = "\033[0m"
        if int(response['status_code']) == 200:
            color = "\033[0;92m"  # Green
        else:
            color = "\033[1;31m"  # Red

        print(f"{color}{response['status_code']}: {response['status_message']}{end_color}\n")
        if response['content']:
            print(response['content'])

    """Local commands"""
    @staticmethod
    def lpwd():
        print(os.getcwd())

    @staticmethod
    def lcd(directory):
        try:
            os.chdir(directory)
        except FileNotFoundError:
            print("No such directory")

    @staticmethod
    def lls(directory=None):
        try:
            output = os.listdir(directory) if directory else os.listdir()
            content = None if len(output) == 0 else "\n".join(output)
            print(content)
        except FileNotFoundError:
            print("No such directory")

    def disconnect(self):
        self.__socket.close()
        print("Disconnected from file-server")
        exit(0)

    @staticmethod
    def show_help():
        ...
