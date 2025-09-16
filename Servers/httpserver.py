import socket
import os
import mimetypes
import datetime
import sys
import argparse

"""
Lab 2 - Single Socket / HTTP Server
NAME: Leticia Dupleich Smith
STUDENT ID: 15048748
DESCRIPTION:
This program implements a simple web server, called LeticiaServer that handles
one client at a time. The server works through a TCP socket that is bound to
a specific port that listens for any incoming requests. The first step when a
client sends an HTTP request to the server is parsing the request. Since this
simple server can only handle requests with the method GET, the program first
makes sure that the method is appropriate before processing it. If the method
is not GET then the server will throw a 501 Not Implemented error. Then, the
server will attempt to locate the requested file. If the file is not found,
the server responds with a 404 Not Found error. If the file is found, the
server returns a 200 OK message and with response headers: connection,
content-type,content-length, date, and server.

The server also manages cookies, or a counter of the number of HTML pages
visited by the client. Every time the client sends a request, the number
of cookies (page_count) is incremented. If the client has visited at least
one page, then the response header set-cookies will be appended to the
response header.

I chose to implement this server using object-oriented programming by
creating an HTTPServer class because it provides a cleaner and more
organized structure compared to using only isolated functions. By
encapsulating both the server’s data (such as the port and web root) and
its behavior (such as handling clients or sending responses) within a
single class, I was able to keep related functionality together and make
the code easier to follow.
"""


class HTTPServer:
    """
    HTTPServer class with attributes:
    - port (int): Port number to listen on.
    - web_root (str): Path to the directory to serve files from.
    - server_name (str): Name of the server sent in HTTP headers.
    """
    def __init__(self, port, web_root):
        """
        This method initializes the HTTPServer using two arguments:
        - port: The port number to bind to the server socket
        - web_root: Where to start looking for files (directory)
        """
        self.port = port
        self.web_root = web_root
        self.server_name = "LeticiaServer"

    def serve(self):
        """
        This method starts the server. It creates a server socket (TCP),
        which binds to a specific port, then listens to a connection
        from a client. Once a connection has been made, it calls the method
        handle_client. This method was implemented to handle one client
        at a time.
        """
        # Using IPv4 and TCP
        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:
            # Make server socket that can be reused with SO_REUSEADDR
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind the socket
            server_socket.bind(('0.0.0.0', self.port))

            # Listen for incoming client connections
            server_socket.listen(1)

            while True:
                client_socket, client_address = server_socket.accept()

                # If connection is found, call handle_client
                try:
                    self.handle_client(client_socket)
                finally:

                    # Close socket after ONE CLIENT
                    client_socket.close()
        finally:
            server_socket.close()

    def handle_client(self, client_socket):
        """
        This method handles a single client's HTTP request. Reads
        the request until the end of the headers, then parses it.
        If the request line starts with anything other than GET
        raise 501 Not Implemented error. If the file does not exist
        raise 404 File Not Found Error. Otherwise, call the
        send_response method with 200 OK.

        This method also tracks the number of cookies, or the pages
        that the client has visited by calling cookie_count.
        """
        request = b""

        # Read until the end of the header
        while b"\r\n\r\n" not in request:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            request += chunk

        request_text = request.decode('utf-8', errors='ignore')

        if not request_text:
            return

        # Example: GET /index.html HTTP/1.1
        # _ to ignore the version of HTTP since we do not need that
        request_line = request_text.splitlines()[0]
        method, path, _ = request_line.split()

        # Method other than GET
        if method != "GET":
            self.send_response(
                client_socket,
                501,
                "Not Implemented",
                b"Method not implemented")
            return

        # If there is no path, or /, go to the home path index.html
        if path == '/':
            path = '/index.html'

        # os.path.join uses the correct separator
        file_path = os.path.join(self.web_root, path.lstrip('/'))

        # Check file existence
        if not os.path.isfile(file_path):
            self.send_response(
                client_socket,
                404,
                "Not Found",
                b"File not found.")
            return

        # Handle cookies (A2)
        page_count = self.cookie_count(request_text)
        if page_count is None:
            page_count = 1
        else:
            page_count = int(page_count) + 1
        cookie_header = f"page-counter={page_count}; Max-Age=31536000"

        # Get the file, read it as bytes and store it in content
        with open(file_path, 'rb') as f:
            content = f.read()

        content_type = mimetypes.guess_type(
            file_path)[0] or 'application/octet-stream'

        # Send response to send_response method
        self.send_response(
            client_socket,
            200,
            "OK",
            content,
            content_type,
            cookie_header)

    def cookie_count(self, request_text):
        """
        This method returns the number of pages that a client has been to.
        It does this by extracting the page-count value from the client's
        request.
        """
        for line in request_text.splitlines():
            if line.startswith('Cookie:'):
                cookies = line[len('Cookie:'):].strip().split(';')
                for cookie in cookies:
                    k, _, v = cookie.strip().partition('=')
                    if k == "page-counter":
                        return v
        return None

    def send_response(
            self,
            client_socket,
            status_code,
            status_message,
            body,
            content_type='text/html',
            cookies=None):
        """
        This method sends an HTTP response to the client. It first formats
        the date adequately with HTTP response format, and then it constructs
        the headers with f strings to respond to the client.
        """
        # Use placeholders to have the correct format RFC for UTC time
        date_str = datetime.datetime.utcnow().strftime(
            '%a, %d %b %Y %H:%M:%S GMT'
        )

        headers = [
            f"HTTP/1.1 {status_code} {status_message}",
            f"Date: {date_str}",
            f"Server: {self.server_name}",
            f"Content-Length: {len(body)}",
            f"Content-Type: {content_type}",
            "Connection: close"
        ]

        # Add cookie header only if cookies exist
        if cookies:
            headers.append(f"Set-Cookie: {cookies}")

        # End of headers and response line
        headers.append("")
        headers.append("")

        response = "\r\n".join(headers).encode('utf-8') + body
        client_socket.sendall(response)


def serve(port, public_html):
    server = HTTPServer(port, public_html)
    server.serve()


# This the entry point of the script
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", help="port to bind to", default=8080, type=int)
    p.add_argument(
        "--public_html",
        help="home directory",
        default="./public_html")
    args = p.parse_args(sys.argv[1:])
    public_html = os.path.abspath(args.public_html)
    serve(args.port, public_html)
