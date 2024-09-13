import os
import socket
import threading


def handle_connection(conn, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        request, headers = data.decode().split("\r\n", 1)
        method, target = request.split(" ")[:2]
        if target == "/":
            response = b"HTTP/1.1 200 OK\r\n\r\n"
        elif target.startswith("/echo/"):
            value = target.split("/echo/")[1]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}".encode(
            )
        elif target.startswith("/user-agent"):
            user_agent = headers.split("User-Agent: ")[1].split("\r\n")[0]
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode(
            )
        elif target.startswith("/files/"):
            file_path = os.path.join("/tmp", target[7:])
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    content = file.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(content)}\r\n\r\n".encode(
                ) + content
            else:
                response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        else:
            response = b"HTTP/1.1 404 Not Found\r\n\r\n"
        conn.sendall(response)
    conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 4221))
        s.listen()
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(
                target=handle_connection, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    main()
