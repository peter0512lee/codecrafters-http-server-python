import os
import socket
import threading
import sys


def handle_connection(conn, addr, directory):
    while True:
        data = conn.recv(1024)
        if not data:
            break

        request = data.decode()
        request_line, rest = request.split("\r\n", 1)
        method, target, _ = request_line.split(" ")

        if method == "GET":
            # ... (keep existing GET handling)
        elif method == "POST" and target.startswith("/files/"):
            headers, body = rest.split("\r\n\r\n", 1)
            content_length = int([h.split(": ")[1] for h in headers.split(
                "\r\n") if h.startswith("Content-Length:")][0])

            # Receive the full body
            while len(body) < content_length:
                body += conn.recv(1024).decode()

            filename = target[7:]  # Remove "/files/" prefix
            file_path = os.path.join(directory, filename)

            with open(file_path, 'w') as file:
                file.write(body)

            response = b"HTTP/1.1 201 Created\r\n\r\n"
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"

        conn.sendall(response)
    conn.close()


def main():
    directory = "."  # Default to current directory
    if len(sys.argv) >= 3 and sys.argv[1] == "--directory":
        directory = sys.argv[2]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 4221))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(
                target=handle_connection, args=(conn, addr, directory))
            thread.start()


if __name__ == "__main__":
    main()
