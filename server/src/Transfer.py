import socket
import json


class Transfer:
    def __init__(self, transfer_socket, client_address, token):
        self.__transfer_socket = transfer_socket
        self.__client_address = client_address
        self.__token = token
        # self.__transfer_socket.settimeout(120)
        print("Client connected")

    def begin(self):
        try:
            transfer_request = json.loads(self.__transfer_socket.recv(2048).decode())
            print("Reading client stuff")
            if transfer_request["token"] == self.__token:
                print("Token correct!")
                print(transfer_request["token"])
                if transfer_request["operation"] == "get":
                    print("get")
                    self.send_file(transfer_request)
                elif transfer_request["operation"] == "put":
                    print("Put")
                    self.receive_file(transfer_request)
            else:
                print("TOken incorrect")
                self.__transfer_socket.close()
                return

        except socket.timeout:
            self.__transfer_socket.close()
            return
        except json.decoder.JSONDecodeError:
            self.__transfer_socket.close()
            return

    def send_file(self, transfer_request):
        file_path = transfer_request["absolute_path"]
        with open(file_path, "rb") as file:
            while True:
                bytes_read = file.read(4096)
                if not bytes_read:
                    break

                self.__transfer_socket.sendall(bytes_read)

        print(f"File {file_path} successfully transmitted to {self.__client_address}")
        self.__transfer_socket.close()
        print("Socket closed")
        exit(0)

    def receive_file(self, transfer_request):
        file_path = transfer_request["absolute_path"]
        with open(file_path, "wb") as file:
            while True:
                bytes_read = self.__transfer_socket.recv(4096)
                if not bytes_read:
                    break
                file.write(bytes_read)

            print(f"Received {file_path} from {self.__client_address}")
            exit(0)
