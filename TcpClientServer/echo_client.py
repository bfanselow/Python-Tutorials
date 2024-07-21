import socket
import sys

"""
  echo client program to call the server in echo_server.py

  The client program sets up its socket differently from the way a server does. Instead of binding to a
  port and listening, it uses connect() to attach the socket directly to the remote address.

"""
host = "localhost"
port = 10009

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (host, port)
print(f"CLIENT>> connecting to {host} on port {port}")
sock.connect(server_address)

# After the connection is established, data can be sent through the socket with sendall() and received
# with recv(), just as in the server.

for b in [b'This is the message.  It will be repeated.', b'STOP']:
    try:

        # Send data
        print(f"CLIENT>> sending message: {b}")
        sock.sendall(b)

        # Look for the response
        #amount_received = 0
        #amount_expected = len(b)

        #while amount_received < amount_expected:
        #    data = sock.recv(64)
        #    amount_received += len(data)
        #    print(f"CLIENT>> received data back: {data}")

    finally:
        print("CLIENT>> closing socket")
        sock.close()
