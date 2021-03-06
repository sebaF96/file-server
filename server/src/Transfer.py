import socket
import json
import os
from .server_helper import print_colored, Constants, calculate_checksum


class Transfer:
    """
    Class representing a file transfer from the server point of view. An instance of this
    class is created each time a client connects to the transfers socket. It will check if
    the transfer is valid and can happen, and if everything is ok, send or receive the file.

    """
    def __init__(self, transfer_socket, client_address, token):
        self.__transfer_socket = transfer_socket
        self.__client_address = client_address
        self.__token = token
        self.__transfer_socket.settimeout(Constants.TRANSFERS_TIMEOUT_SECONDS)

    def begin(self) -> None:
        """
        Main Transfer method. It will check the security token, and if valid, delegates
        the transfer to send_file() or receive_file() depending on what client is asking to do.
        If token is not valid, it will immediately close the connection and exit
        :return:
        """
        try:
            transfer_request = json.loads(self.__transfer_socket.recv(Constants.BUFFER_SIZE).decode())
            if not transfer_request["token"] == self.__token:
                self.__transfer_socket.close()
                return
            elif transfer_request["operation"] == "get":
                self.send_file(transfer_request)
            elif transfer_request["operation"] == "put":
                self.__transfer_socket.send(Constants.READY_FLAG)
                self.receive_file(transfer_request)
        except (socket.timeout, json.decoder.JSONDecodeError):
            self.__transfer_socket.close()
            return

    def send_file(self, transfer_request: dict) -> None:
        """
        Handles a file send to the associated client's socket. It will open the file in binary-read mode,
        read chunks of 4096 bytes and send them to the client. When it's done reading the file and sending
        it, it will close the connection and exit. This will send an EOF to the client side
        after he receives the last byte of the file.

        :param transfer_request: Dictionary with all the transfer's metadata
        :return: None
        """
        file_path = transfer_request["absolute_path"]
        with open(file_path, "rb") as file:
            while True:
                bytes_read = file.read(Constants.FILE_BUFFER_SIZE)
                if not bytes_read:
                    break
                self.__transfer_socket.sendall(bytes_read)

        print_colored(color="PURPLE", message=f"{Constants.date_time()} TRANSMITTED {file_path} to {self.__client_address}")
        self.__transfer_socket.close()

    def receive_file(self, transfer_request: dict) -> None:
        """
        Handles a file receive from the associated client's socket. It will open the file in binary-write
        mode, read chunks of 4096 bytes from the client's socket and write them to the file.
        When EOF is reached (client done transmitting), it will flush the file and exit

        :param transfer_request: Dictionary with all the transfer's metadata
        :return: None
        """
        file_path = transfer_request["absolute_path"]
        with open(file_path, "wb") as file:
            while True:
                bytes_read = self.__transfer_socket.recv(Constants.FILE_BUFFER_SIZE)
                if not bytes_read:
                    break
                file.write(bytes_read)

        is_authentic = calculate_checksum(file_path) == transfer_request["sha256sum"]
        if is_authentic:
            print_colored(color="YELLOW", message=f"{Constants.date_time()} RECEIVED {file_path} from {self.__client_address}")
        else:
            os.remove(file_path)


