# File server

#### Python client-server program that allows you to send and receive files to and from the server

- :electric_plug: Communications over TCP using Python's low-level networking interface [socket][socket]
- :closed_lock_with_key: Secure and encrypted communications using TLS protocol
- :heavy_check_mark: Both Server and Client will verify the checksum of a received file to make sure is not corrupted
- :satellite: Remote commands runs in Server side and its output is sent to the Client
- :ok: Server will always answer a status code with a message, and the standard output (if any)
- :octopus: Server is able to attend multiple Clients at the same time using multiprocessing
------------


1. [Install](https://github.com/sebaF96/file-server#install)
2. [Usage](https://github.com/sebaF96/file-server#usage)
	- [Server](https://github.com/sebaF96/file-server#server)
	- [Client](https://github.com/sebaF96/file-server#client)
3. [Protocol](https://github.com/sebaF96/file-server#protocol)
	- [Communication](https://github.com/sebaF96/file-server#communication)
	- [Sending and receiving files](https://github.com/sebaF96/file-server#sending-and-receiving-files)

------------

## Install
To install and run this program you'll need python3, pip3, python3-venv and a couple of dependencies. You'll also need
OpenSSL version 1.0.1 or higher, but it comes pre-installed on all modern Unix systems, Windows, Mac OS X, and probably additional platforms.
This installation guide assumes that you already have it.

Install python3, pip3 and python3-venv

```shell
$ sudo apt install python3 pip3 python3-venv git
```

Clone the project and generate a python venv

```shell
$ git clone https://github.com/sebaF96/file-server.git file-server
$ cd file-server && python3 -m venv venv
```

Next, using your recently created venv, install the project dependencies

```shell
$ source venv/bin/activate
(venv) $ pip3 install -r requirements.txt
```

File Server is ready to run now. However, if you're using v2.0 or higher, you'll need an SSL Certificate and a Private Key
in server side, stored in the same file. This .pem file should look like this

```
-----BEGIN RSA PRIVATE KEY-----
... (private key in base64 encoding) ...
-----END RSA PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
... (certificate in base64 PEM encoding) ...
-----END CERTIFICATE-----
```

You can work with self-signed certificates as well. If you dont have a certificate, you can generate
one very quickly using OpenSSL. The command to create a self-signed certificate is the following:

```shell
$ openssl req -new -x509 -days 365 -nodes -out file-server-cert.pem -keyout file-server-cert.pem
```

It will then prompt you for information like "Country Name", you can fill this information or just press Enter and accept the defaults.

We recommend you to read [OpenSSL Documentation][openssldocs]

Once you've got your Certificate and Private Key stored in a .pem file, you have to load the path
to said file in an .env file. This file should be in the root-level of the project and should look like this:

```shell
PATH_TO_CERT=/absolute/path/to/cert.pem
```

If you're using a self-signed Certificate, you have to provide the Client(s) with said certificate as well,
and also generate a .env file with the path to it.


At this point, you're good to go.

------------

## Usage

### Server
Server will listen in two ports, the main one, where it will be expecting connections to trade commands and responses with the client, and a second one that's dedicated just to send and receive files. You can specify what ports server will use for both cases, and if you don't, it will use default ones (8080 for main connections and 3000 for transfers)

- To specify main port, use options **-p** or **--port**
- To specify transfer port, use options **-t** or **--transfer-port**

An example server launch specifying two ports will be like this

```shell
$ python server/server.py -p 5000 -t 5001
```
or
```shell
$ python server/server.py --port 5000 --transfer-port 5001
```
or
```shell
$ python server/server.py --port 5000 -t 5001
```

Again, you can specify one port, both of them or none.

### Client
For the client to connect, you must specify the server address and main port.

- To specify server IPv4 address use option **-a** or **--address**
- To specify server main port use option **-p** or **--port**

An example of server launch will be like this

```shell
$ python client/client.py -a 192.168.0.110 -p 5000
```

or

```shell
$ python client/client.py --address 192.168.0.110 --port 5000
```

If there's a **file-server** in the given address listening for main connections at that port, client will connect to it and show you a prompt, where you can enter the following known commands.

| Command  | Type   | Description   |
| ------------ | ------------ | ------------ |
|   pwd | remote   | show server's current working directory  |
|  cd /route | remote  | change server's current working directory to the given route, if exists  |
|  ls  | remote  | list files and directories in server's current working directory   |
| ls /route  |  remote  |  list files and directories server's given directory, if exists |
|  mkdir dirname | remote   | creates dirname directory in server's current working directory  |
|  lpwd  | local  | show your current working directory  |
| lcd /route  | local  |  change your current working directory to the given route, if exists |
| lmkdir dirname  | local  |  creates dirname directory in your current working directory |
|  lls | local  | list files and directories in your current working directory  |
|  lls /route | local  | list files and directories in the given route, if exists  |
|  help  | local  | shows the client's known commands and their descriptions  |
|  exit  | local  | closes the connection and exits  |
| get filename | remote  | downloads given filename from the server, and saves it in your current working directory  |
| put filename  | remote  | uploads given filename to the server, and saves it in server's current working directory  |


------------

## Protocol

### Communication


Client and Server main communications are through json formatted messages, and this messages will be utf-8 encoded.

#### Sending messages to the server

 The format to **send messages to the server** is the following:

```json
{
  "command": "ls",
  "argument": "/home/server"
}
```

It doesn't matters that your command has no argument, the previous format must be respected or server will answer a **500** error message letting you know that your message is bad formed. In the case that your command has no argument, your message should be like this:

```json
{
  "command": "ls",
  "argument": null
}
```

#### Receiving server responses

Server will always answer a json formatted message containing a status code, a message and content if your command has any output. Examples shown below:


- You send (json formatted) **pwd** to the server, server answer will be like this
```json
{
  "status_code": 200,
  "status_message": "OK",
  "content": "/home/server/Documents"
}
```

- You send (json formatted) **mkdir pdf-files** to the server, server answer will be like this
```json
{
  "status_code": 200,
  "status_message": "OK",
  "content": null
}
```

- You send (json formatted) **cd /homeee** to the server, server answer will be like this
```json
{
  "status_code": 500,
  "status_message": "No such directory",
  "content": null
}
```

- You send (NOT json formatted) **pwd** to the server, server answer will be like this
```json
{
  "status_code": 500,
  "status_message": "Invalid command format, it doesn't respect the protocol",
  "content": null
}
```

------------

### Sending and receiving files

File transfers will happen through a dedicated connection between the server and the client. As previously said, server will be listening in a second port for transfer requests. However, clients must ask the server through their main connection before a transfer can happen.  This will be done with the previously mentioned json-formatted message from the client to the server, where "command" value will be "put" or "get", depending if the client needs to upload or download a file, and the "argument" value will be the name of the file (can be relative path or absolute path). Below are two examples of transfer requests:


Here, client asks to download the file Rute.pdf of the server's current working directory
```json
{
  "command": "get",
  "argument": "Rute.pdf"
}
```


In this second example, clients asks to upload apuntes.txt file located in client's current working directory

```json
{
  "command": "put",
  "argument": "apuntes.txt"
}
```


The server will answer with a json-formatted message and here are two possible scenarios:

##### Transfer can not happen
If client wants to upload a file that already exists in server's system or download a file that does not exist in server's system, server will reject said transfer request and answer a message like the one below:

```json
{
  "status_code": 500,
  "status_message": "No such file",
  "content": null
}
```
Here, server is rejecting the transfer because doesn't have the file that the client asked for.

##### Transfer can happen
If the server allows the transfer, it will answer a json-formatted message with all the metadata that client needs to connect to the transfer port, including a 200 status code. An example would be like the following one:

```json
{
  "status_code": 200,
  "operation": "get",
  "absolute_path": "home/server/Documents/Rute.pdf",
  "filesize": 5378210,
  "token": "eoyBUrfKYGrwQOqVCxeXQTwwuPeBiCVLe_AZ56f1...",
  "transfer_port": 3000
}
```

Things to notice here:
- **Absolute path**: Server shows client the absolut path to the file to upload/download in server's system
- **File size**: If the client wants to download a file, server will inform you how big that file is
- **Token**: Token is a 64 bytes url-safe string that is randomly generated by the server, the point of this is to make sure that all the transfer requests landing in transfer port are previously allowed by the server through the main connection. The first thing that the transfer socket is gonna ask when a client connects to it, is that token. If the token isn't the same that the one that the server generated, it will immediately close the connection. This has 4 main advantages:
	- If we need to authenticate clients with an username and password, we just have to do it in the main connection.
	- No one will be able to connect directly to the transfer port and ask for a file if the server is not aware of that transfer and has previously accepted it.
	- If we need to log information about who uploads and downloads what, we can generate a different token for each client and use it for that purpose.
	- If we need to give different permissions or protect directories in the future, we can use this tokens to check if a client is allowed or not to download x file.

    At the moment, this token is the same for every client and will be the same for all the server's lifecycle. But again, this can change with minimum logic.

- **Transfer port**: Server will let the client know where to ask for that transfer, this way, client doesn't need to know both ports that the server are listening to, but just the main one. The transfer port is communicated just when needed.


------------

Assuming that the server allowed the transfer, clients just need to take that json-formatted message with the transfer metadata and connect to the given transfer port. Once the connection is established, the server's transfer manager will ask for that metadata. The client has 60 seconds to send it or the server is going to close the connection. 
When the client sends the metadata, server will check if the token is valid. If not, it will close the connection. If it's, transfer will begin

#### Transfer protocol
Transfer protocol is quite simple once we are in this step, but it's slightly different depending if the client wants to upload or download a file.

#### Download (get)

If the client needs to download a file, server will read his transfer request (metadata) and assuming the token is valid, it will immediately start sending the file. When is done, it will close the connection. This will send an EOF to the client side of the socket but he's going to reach it just after he'd read the last byte of the file. This way, client will know when the transfer is over.


#### Upload (put)

If the client needs to upload a file, server will read his transfer request (metadata) and assuming the token is valid, it will send an 8 bytes start flag (**b'10101010'**). This is to let the client know that the server is ready to receive the file. Here, the client can start sending it. If the client start sending the file before he receives this flag, the json-formatted metadata could be mixed with the first chunk of the file, and if the server is busy enough to not read the transfer request immediately, this would make it not json-decodable and the server will close the connection. The server will continue reading from the socket and writing the file, until an EOF is reached. That means that when the client is done sending the file, he should close the connection, the same way server does when he is the one sending the file. Again, server will not wait forever, assuming the client doesn't send an EOF but neither sends file information in 60 seconds, server will close the connection.


[socket]: https://docs.python.org/3.8/library/socket.html "socket"
[openssldocs]: https://www.openssl.org/docs/ "openssldocs"
