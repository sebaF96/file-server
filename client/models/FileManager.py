import os
import json
import tqdm
from socket import timeout
from .client_helper import Constants, calculate_checksum


class FileManager:
    """
    Class representing a file transfer from the client point of view. An instance of this
    class is created each time that the client request for a file transfer. It will connect to the
    server's transfers socket, send the transfer metadata and start uploading/downloading the file
    """
    def __init__(self, transfer_socket, transfer_metadata):
        self.__transfer_socket = transfer_socket
        self.__transfer_metadata = transfer_metadata

    def begin(self) -> None:
        """
        Main class method, it will establish connection with the socket, and delegate the transfer
        to the send_file() or receive_file() method depending on transfer type.

        :return: None
        """
        if self.__transfer_metadata["operation"] == "put":
            self.__transfer_metadata["sha256sum"] = calculate_checksum(os.path.basename(self.__transfer_metadata["absolute_path"]))
            self.__transfer_socket.send(json.dumps(self.__transfer_metadata).encode())
            self.__transfer_socket.recv(8)
            self.send_file()
            print(Constants.FILE_UPLOADED)
        elif self.__transfer_metadata["operation"] == "get":
            self.__transfer_socket.send(json.dumps(self.__transfer_metadata).encode())
            self.get_file()

    def send_file(self):
        """
        Handles a file send to the server's transfers socket. It will open the file in binary-read mode,
        read chunks of 4096 bytes and send them to the server, while updating a progress bar on stdout.
        When it's done reading the file and sending it, it will close the connection and exit.
        This will send an EOF to the server side after he receives the last byte of the file.

        :return: None
        """
        filename = os.path.basename(self.__transfer_metadata["absolute_path"])
        filesize = os.path.getsize(filename)

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            while True:
                bytes_read = f.read(Constants.FILE_BUFFER_SIZE)
                if not bytes_read:
                    progress.close()
                    self.__transfer_socket.close()
                    break

                self.__transfer_socket.sendall(bytes_read)
                progress.update(len(bytes_read))

    def get_file(self) -> None:
        """
        Handles a file receive from the server's transfers socket. It will open the file in binary-write
        mode, read chunks of 4096 bytes from the server's socket and write them to the file while
        updating a progress bar on stdout. When EOF is reached (server is done transmitting)
        it will flush the file and exit

        :return: None
        """
        filesize = int(self.__transfer_metadata["filesize"])
        filename = os.path.basename(self.__transfer_metadata["absolute_path"])
        self.__transfer_socket.settimeout(Constants.TRANSFER_TIMEOUT_SECONDS)

        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as file:
            while True:
                try:
                    bytes_read = self.__transfer_socket.recv(Constants.FILE_BUFFER_SIZE)
                    if not bytes_read:
                        break
                    file.write(bytes_read)
                    progress.update(len(bytes_read))
                except timeout:
                    break
            progress.close()

        print(Constants.CALCULATING_CHECKSUM, end='')
        is_authentic = calculate_checksum(filename) == self.__transfer_metadata["sha256sum"]

        if is_authentic:
            print(Constants.OK_MESSAGE)
            print(Constants.FILE_DOWNLOADED)

        else:
            print(Constants.INVALID_CHECKSUM)
            os.remove(filename)
