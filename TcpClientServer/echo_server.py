import socket
import sys

"""
  This sample program, based on the one in the standard library documentation, receives incoming messages
  and echos them back to the sender. It starts by creating a TCP/IP socket.

  Usage:
  Start the server in the background (using "&"). Once the server side is started and waiting for connections, run the client

  $ python3 echo_server.py &
  $ python3 echo_client.py

"""

host = "localhost"
port = 10008

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
# bind() is used to associate the socket with the server address (ip, port) with ip=localhost (current server) in this case
server_address = (host, port)
print(f"SVR>> starting up on host={host} port={port}")
sock.bind(server_address)

# Listen for incoming connections.
# listen() puts the socket into server mode, and accept() waits for an incoming connection.
sock.listen(1)

while True:
    # Wait for a connection
    # accept() returns an open connection between the server and client, along with the (remote) address of the client.
    # The connection is actually a different socket on another port (assigned by the kernel). Data is read from the
    # connection with recv() and transmitted back to the sender with sendall().
    print("SVR>> waiting for a connection")
    connection, client_address = sock.accept()


    try:
        print(f"SVR>> connection from {client_address}")

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print(f"SVR>> received data: {data}")
            if data:
                print("SVR>> sending data back to the client")
                connection.sendall(data)
            else:
                print(f"SVR>> no more data from client: {client_address}")
                break

    finally:
        # Clean up the connection
        print(f"SVR>> closing connection")
        connection.close()
