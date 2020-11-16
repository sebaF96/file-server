# File server
#### Python client-server program that allows you to send and receive files to and from the server

- Communications over TCP using Python's low-level networking interface [socket][socket]
- Remote commands runs in server side and its output is sent to the client
- Server will always answer a status code with a message, and the standard output (if any)
- Server is able to attend multiple clients at the same time using multiprocessing
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
To install and run this program you'll need python3, pip3, python3-venv and a couple of dependencies.

Install python3, pip3 and python3-venv

```shell
$ sudo apt install python3 pip3 python3-venv git
```

Clone the project and generate a python venv

```shell
$ git clone https://github.com/sebaF96/file-server.git file-server
$ cd file-server && python3 -m venv venv
```

Finally, using your recently created venv, install the project dependencies

```shell
$ source venv/bin/activate
(venv) $ pip3 install -r requirements.txt
```

You're good to go now.

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

### Sending and receiving files


------------



[socket]: https://docs.python.org/3.8/library/socket.html "socket"