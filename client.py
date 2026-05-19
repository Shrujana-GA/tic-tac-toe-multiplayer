import socket

client = socket.socket()
client.connect(("localhost", 5555))

while True:
    msg = client.recv(1024)

    if not msg:
        break

    msg = msg.decode()
    print(msg)

    if "Your move" in msg:
        move = input("Enter position (0-8): ")
        client.send(move.encode())