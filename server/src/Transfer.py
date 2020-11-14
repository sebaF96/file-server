import socket
import json


class Transfer:
    def __init__(self, transfer_socket, client_address, token):
        self.__transfer_socket = transfer_socket
        self.__client_address = client_address
        self.__token = token
        self.__transfer_socket.settimeout(120)

    def begin(self):
        try:
            transfer_request = json.loads(self.__transfer_socket.recv(1024).decode())
            if transfer_request["token"] == self.__token:
                if transfer_request["operation"] == "GET":
                    self.get(transfer_request)
                elif transfer_request["operation"] == "PUT":
                    self.put(transfer_request)
            else:
                self.__transfer_socket.close()
                return

        except socket.timeout:
            self.__transfer_socket.close()
            return
        except json.decoder.JSONDecodeError:
            self.__transfer_socket.close()
            return

    def get(self, transfer_request):
        file_path = transfer_request["absolute_path"]
        with open(file_path, "rb") as file:
            while True:
                bytes_read = file.read(4096)
                if not bytes_read:
                    print(f"File {file_path} successfully transmitted to {self.__client_address}")
                    self.__transfer_socket.close()
                    break
                self.__transfer_socket.sendall(bytes_read)

    def put(self, transfer_request):
        file_path = transfer_request["absolute_path"]
        with open(file_path, "wb") as file:
            while True:
                bytes_read = self.__transfer_socket.recv(4096)
                if not bytes_read:
                    print(f"Received {file_path} from {self.__client_address}")
                    self.__transfer_socket.close()
                    break
                file.write(bytes_read)

