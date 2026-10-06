import socket

HOST = "127.0.0.1"
PORT = 5003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print(f"Node C is running on {HOST}:{PORT}")

while True:
    client_socket, client_address = server.accept()

    print(f"Connection received from {client_address}")

    message = client_socket.recv(1024).decode()

    if message:
        print(f"Message received: {message}")

        response = "ACK from Node C"
        client_socket.send(response.encode())

    client_socket.close()