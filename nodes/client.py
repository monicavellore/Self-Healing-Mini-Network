import socket

HOST = "127.0.0.1"
PORT = 5001

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

message = "Hello Node A"
client.send(message.encode())

response = client.recv(1024).decode()

print(f"Server response: {response}")

client.close()