"""
Luna Dagci
ICSI 516
11/03/2021
Project 1

UDP Client using stop and wait algorithm for data transport
reliability.
"""

import os
import socket
import sys

IP = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1000  # Size is 1000 bytes


def main():
    """ Staring a UDP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """Continue getting input from the user until user quits"""
    while True:

        user_input = input("Enter command:")
        """split the command into parts"""
        command_args = user_input.split()
        """get the command"""
        command = command_args[0]

        """send the commands to the Server"""
        client.sendto(user_input.encode(FORMAT), ADDR)

        """Upload the file into the server"""
        if command == 'PUT'.casefold():
            print("Awaiting server response.")

            """get the file name from the command line argument"""
            input_filename = command_args[1]

            """Stop and wait Sender"""
            sender(input_filename, ADDR, client)

            """ 'Remove' timeout"""
            client.settimeout(None)

            """receive the message from the server"""
            message, addr = client.recvfrom(SIZE)
            if message.decode(FORMAT) == 'FIN':
                message, addr = client.recvfrom(SIZE)
                print(message.decode(FORMAT))

        elif command == 'keyword'.casefold():
            print("Awaiting server response.")

            """receive the message from the server"""
            message, addr = client.recvfrom(SIZE)
            print(message.decode(FORMAT))

            """Download the file from the Server"""
        elif command == 'GET'.casefold():

            """Get the output file name from the command line arguments"""
            output_filename = command_args[1]

            """Stop and wait receiver"""
            receiver(output_filename, client)

            """Remove timeout"""
            client.settimeout(None)

            print("File %s downloaded." % output_filename)

            """quit the program and close connection"""
        elif command == 'quit'.casefold():
            print("Exiting program!")
            client.close()
            break
        else:
            print("Unknown Command")

    client.close()


"""Stop-and-wait Helper Functions : Receiver and Sender"""


def sender(filename, dest_addr, conn):
    """
    :param filename: file name entered by user
    :param dest_addr: address to send data chunks to
    :param conn: socket connection
    :return: boolean indicating acknowledged or not

    Data Sender receives the acknowledgement.
    'GET' in server and 'PUT' in client
    """

    """Open file in read permission"""
    file = open(filename, 'r')

    """Read the contents in the file"""
    data = file.read()

    """Close File"""
    file.close()

    """Get the file size, LEN, in string"""
    LEN = str(get_size(filename))

    """Send LEN message"""
    conn.sendto(LEN.encode(FORMAT), dest_addr)

    """split the data into equal chunks of 1000 bytes each
    Resource: https://www.codegrepper.com/code-examples/python/python+split+array+into+chunks+of+size+n
    """
    byte_chunks = ([*data])
    data_chunks = [byte_chunks[x:x + SIZE] for x in range(0, len(byte_chunks), SIZE)]

    """Send the data packets to the server, 1000 bytes a time
    Resource: https://stackoverflow.com/questions/15909064/python-implementation-for-stop-and-wait-algorithm
    """

    """Send the data one chunk at a time"""
    for data_chunk in data_chunks:
        """Initialize that acknowledge has not been received"""
        acknowledged = False
        while not acknowledged:
            try:
                """Send data chunk to receiver"""
                conn.sendto(''.join(data_chunk).encode(FORMAT), dest_addr)
                """Set server timeout"""
                conn.settimeout(1)  # timeout is 1 second
                """Receive message containing ACK or FIN"""
                message, addr = conn.recvfrom(SIZE)
                message = message.decode(FORMAT)

                if message == "ACK":
                    acknowledged = True

                """Timeout after a data packet"""
            except socket.timeout:
                message = "Did not receive ACK. Terminating."
                print(message)
                conn.close()


def receiver(filename, conn):
    """

    :param filename: file name entered by the user
    :param conn: socket connection
    :return: void

    Data Receiver sends the acknowledgement
    """

    """open the output file in write permission: if DNE then create a new file"""
    file = open(filename, "w+")

    """receive the filesize from the server"""
    LEN, source_addr = conn.recvfrom(SIZE)

    LEN = LEN.decode(FORMAT)

    """Initial received size is 0 bytes"""
    received_size = 0
    """Check if all expected bytes are received"""
    while True:

        """
        Check if all expected bytes are received
        Comments: converted to string due to a bug
        """
        if str(LEN) == str(received_size):
            break

        """write the contents of file into the file"""
        try:
            """receive the content of file from the server"""
            data, source_addr = conn.recvfrom(SIZE)
            data = data.decode(FORMAT)
            """Recalculate received bytes"""
            received_size += len(data)
            """Set server timeout"""
            conn.settimeout(1)  # timeout is 1 second

            """Timeout after LEN message"""
        except socket.timeout:
            message = "Did not receive data. Terminating."
            print(message)
            file.close()
            conn.close()
            return

        try:
            """Set server timeout"""
            file.write(data)
            conn.sendto("ACK".encode(FORMAT), source_addr)
            conn.settimeout(1)  # timeout is 1 second

            """Timeout after ACK"""
        except socket.timeout:
            message = "Data transmission terminated prematurely."
            print(message)
            file.close()
            conn.close()
            return

    file.close()
    conn.sendto("FIN".encode(FORMAT), source_addr)


def get_size(filename):
    file = open(filename, 'r')
    LEN = 0
    while True:
        data = file.read(SIZE)
        if not data:
            break
        LEN += len(data)
    return LEN


if __name__ == "__main__":
    main()
