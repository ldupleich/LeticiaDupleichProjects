import socket
import select
import datetime
import sys
import argparse

"""
Lab 2 - Multiple Sockets / Chat Room (Server)
NAME: Leticia Dupleich Smith
STUDENT ID: 15048748
DESCRIPTION:
This program implements a very simple chat room that allows clients connected
to a server to communicate with each other. It does this using a client-server
architecture and sockets. The server can handle multiple clients at once, and
supports multiple commands that allow them to perform different actions:
/nick, /say, /whisper, /list, /help, /whois, and /kick. These commands
allow the clients to communicate with each other by either broadcasting to
all connected clients, or whispering to a specific client. Functionalities
also allow the clients to get information about the other clients, and even
kick them out of the server.The server will first
open a socket which listens to incoming connections from clients. Clients
can join the server through this socket and communicate with each other.

I chose to implement this program with object-oriented programming (OOP)
instead of isolated functions to enhance functionality and make sure that
certain variables and other attributes were accessible all throughout
the class and thereby can be used in many methods.
"""


class ChatServer:
    """
    ChatServer with attributes:
    - port (int): Port number to listen on
    - server_socket (socket.socket): Server's main socket
    - clients (dict): Maps client's socket to their data
    """
    def __init__(self, port):
        """
        This method initializes the ChatServer with one argument:
        - port: Port number that the server will bind to
        """
        self.port = port
        self.server_socket = None

        # Of the form {"nick": str, "addr": (ip, port)}
        self.clients = {}

    def start(self):
        """
        This methods creates the server socket and then calls
        the main run loop to start the client connections
        """
        # Create a normal TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to all interfaces on the specified port
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(5)

        # Start the main loop to handle clients
        self.run()

    def run(self):
        """
        This methos is the main loop that is used to handle multiple clients
        simultaneously. Uses the select.select() module in order to be able
        to deal with multiple sockets. Once a connection with a client
        is made, this will be broadcasted onto the server for other
        clients to see. Then the clients can send messages which will be
        handled with the commands method.
        """
        # Listen on all sockets for any incoming connections
        inputs = [self.server_socket]

        while True:

            # Select.select for multiple connections
            readable, _, exceptional = select.select(inputs, [], inputs)

            # For every socket in the list of all readable sockets
            for s in readable:

                # If server socket then a new client is trying to connect
                if s is self.server_socket:
                    client_socket, addr = self.server_socket.accept()
                    self.clients[client_socket] = {
                        "nick": f"user{len(self.clients)+1}",
                        "addr": addr
                    }

                    inputs.append(client_socket)

                    # Broadcast connections
                    self.broadcast(
                        f"{addr} connected with name "
                        f"{self.clients[client_socket]['nick']}"
                    )

                # Now we have to handle messages from existing clients
                else:
                    try:
                        data = s.recv(1024).decode().strip()

                        # recv returns no data (empty string), disconnect
                        if not data:
                            self.disconnect(s, inputs)

                        # If we do have data, send it to the commands method
                        else:
                            self.commands(s, data, inputs)
                    except ConnectionResetError:
                        self.disconnect(s, inputs)

            # This means that the client has an error
            for s in exceptional:
                self.disconnect(s, inputs)

    def commands(self, socket, message, inputs):
        """
        This method is what processes the client's commands and then prints
        the correct "responses" onto the terminal server.
        """
        nick = self.clients[socket]["nick"]

        # Command /nick to change nickname
        if message.startswith("/nick "):
            new_nick = message.split(" ", 1)[1]

            nickname_used = False

            # Check if the nickname already exists
            for n in self.clients.values():
                if n["nick"] == new_nick:
                    nickname_used = True
                    break

            # If the nickname exists, failure, else success
            if nickname_used:
                self.send(socket, f"username {new_nick} already in use")
            else:
                old = self.clients[socket]["nick"]
                self.clients[socket]["nick"] = new_nick
                self.broadcast(f"user {old} changed name to {new_nick}")

        # Command /say or blank to send broadcast messages
        elif message.startswith("/say ") or not message.startswith("/"):
            if message.startswith("/say"):
                text = message[5:]
            else:
                text = message

            self.broadcast(f"{nick}: {text}")

        # Command /whisper to send a message to a specific client
        elif message.startswith("/whisper "):
            parts = message.split(" ", 2)
            target_nick, text = parts[1], parts[2]
            target = self.find_by_nick(target_nick)

            if target:
                self.send(socket, f"whisper to {target_nick}: {text}")
                self.send(target, f"{nick} whispers: {text}")
            else:
                self.send(socket, f"user {target_nick} not found")

        # Command /list to print all existing clients connected to the server
        elif message.startswith("/list"):
            for n in self.clients.values():
                self.send(socket, f"{n['nick']} {n['addr']}")

        # Command /whois to print information on a specific client
        elif message.startswith("/whois "):
            target_nick = message.split(" ", 1)[1].strip()
            target = self.find_by_nick(target_nick)

            if target:
                self.send(
                    socket,
                    f"{target_nick} has address "
                    f"{self.clients[target]['addr']}"
                    )
            else:
                self.send(socket, f"user {target_nick} not found")

        # Command /kick to remove a client from the server
        elif message.startswith("/kick "):
            target_nick = message.split(" ", 1)[1]
            target = self.find_by_nick(target_nick)

            # Kick message and also call disconnect function for removal
            if target:
                self.broadcast(f"{target_nick} has been kicked by {nick}")
                self.disconnect(target, inputs)

            else:
                self.send(socket, f"user {target_nick} not found")

        # Command /help or / to print all possible commands
        elif message.startswith("/help") or message.startswith("/"):
            help_message = (
                "/nick <new_nick>\n"
                "/say <text> or just <text>\n"
                "/whisper <nick> <text>\n"
                "/list\n"
                "/whois <nick>\n"
                "/kick <nick>\n"
            )
            self.send(socket, help_message)

    def send(self, sock, msg):
        """
        This method is used to send a message to a specific client.
        This message is of the form [13:37:05] W_Petri whispers: YEEHAH!
        """
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        try:
            sock.sendall(f"{timestamp} {msg}\n".encode())
        except Exception:
            pass

    def broadcast(self, msg):
        """
        This method is used to send a message to all clients that are
        connected to the server.
        """
        for sock in list(self.clients.keys()):
            self.send(sock, msg)

    def disconnect(self, sock, inputs):
        """
        This method is used to properly disconnect and remove clients from the
        server and print a disconnect message.
        """
        if sock in self.clients:
            nick = self.clients[sock]["nick"]
            self.broadcast(f"{nick} disconnected")
            del self.clients[sock]

            if sock in inputs:
                inputs.remove(sock)
                sock.close()

    def find_by_nick(self, nick):
        """
        This method is used to find a client socket by using their nickname,
        it is especially used when we have to send a message to a specific
        client with the /whisper command.
        """
        for n, info in self.clients.items():
            if info["nick"] == nick:
                return n
        return None


def serve(port, cert, key):
    server = ChatServer(port)
    server.start()


# Command line parser
if __name__ == "__main__":

    p = argparse.ArgumentParser()
    p.add_argument("--port", help="port to listen on", default=12345, type=int)
    p.add_argument(
        "--cert",
        help="server public cert",
        default="public_html/cert.pem")
    p.add_argument("--key", help="server private key", default="key.pem")
    args = p.parse_args(sys.argv[1:])
    serve(args.port, args.cert, args.key)
