import socket
import os


class Client:
    def __init__(self, address, port):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((address, port))
        print(f"Connected to File Server at {address} on port {port}")

    @property
    def socket(self):
        return self.__socket

    @staticmethod
    def lpwd():
        print(os.curdir)

    @staticmethod
    def lcd(route):
        os.chdir(route)

    def pwd(self):
        self.__socket.send('pwd'.encode())
        answer = self.__socket.recv(1024)
        print(answer)

    def cd(self, route):
        self.__socket.send(f'cd {route}'.encode())
        answer = self.__socket.recv(1024)
        print(answer)
