import socket
import os
import json
import tqdm


class FileManager:
    def __init__(self, transfer_address, transfer_metadata):
        print(transfer_address)
        self.__transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__transfer_address = transfer_address
        self.__transfer_metadata = transfer_metadata

    def begin(self):
        self.__transfer_socket.connect((self.__transfer_address, self.__transfer_metadata["transfer_port"]))
        self.__transfer_socket.send(json.dumps(self.__transfer_metadata).encode())
        if self.__transfer_metadata["operation"] == "put":
            self.send_file()
        elif self.__transfer_metadata["operation"] == "get":
            self.get_file()

    def send_file(self):
        filename = os.path.basename(self.__transfer_metadata["absolute_path"])
        filesize = os.path.getsize(filename)

        progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "rb") as f:
            for _ in progress:
                bytes_read = f.read(4096)
                if not bytes_read:
                    progress.close()
                    print("Done!")
                    self.__transfer_socket.close()
                    break

                self.__transfer_socket.sendall(bytes_read)
                progress.update(len(bytes_read))

    def get_file(self):
        filesize = int(self.__transfer_metadata["filesize"])
        filename = os.path.basename(self.__transfer_metadata["absolute_path"])

        #progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as file:
            while True:
                print("Recibiendo...")
                bytes_read = self.__transfer_socket.recv(1024)
                if not bytes_read:
                    break
                file.write(bytes_read)
                print("Escritos")
                # progress.update(len(bytes_read))
                print("Updateado")
            # progress.close()

            print("Done(?")
