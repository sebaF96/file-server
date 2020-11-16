import socket
import os
import json
import tqdm


class FileManager:
    """
    Class representing a file transfer from the client point of view. An instance of this
    class is created each time that the client request for a file transfer. It will connect to the
    server's transfers socket, send the transfer metadata and start uploading/downloading the file
    """
    def __init__(self, transfer_address, transfer_metadata):
        self.__transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__transfer_address = transfer_address
        self.__transfer_metadata = transfer_metadata

    def begin(self) -> None:
        """
        Main class method, it will establish connection with the socket, and delegate the transfer
        to the send_file() or receive_file() method depending on transfer type.

        :return: None
        """
        self.__transfer_socket.connect((self.__transfer_address, self.__transfer_metadata["transfer_port"]))
        self.__transfer_socket.send(json.dumps(self.__transfer_metadata).encode())
        if self.__transfer_metadata["operation"] == "put":
            self.__transfer_socket.recv(8)
            self.send_file()
            print("File successfully uploaded")
        elif self.__transfer_metadata["operation"] == "get":
            self.get_file()
            print("File successfully downloaded")

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
                bytes_read = f.read(4096)
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

        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as file:
            while True:
                bytes_read = self.__transfer_socket.recv(4096)
                if not bytes_read:
                    break
                file.write(bytes_read)
                progress.update(len(bytes_read))

            progress.close()
