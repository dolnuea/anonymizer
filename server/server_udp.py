"""
Luna Dagci
ICSI 516
11/03/2021
Project 1

UDP Server using stop and wait algorithm for data transport
reliability.
"""

import os
import socket
import sys
import re

IP = ''
PORT = int(sys.argv[1])
SIZE = 1000  # Size is 1000 bytes
FORMAT = "utf-8"


def main():
    """ Staring a UDP socket. """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """ Bind the IP and PORT to the server. """
    server.bind((IP, PORT))

    while True:

        """get to command from client"""
        user_input, addr = server.recvfrom(SIZE)
        user_input = user_input.decode(FORMAT)

        print(f"[RECV]" + user_input)

        user_input = user_input.split()
        command = user_input[0].lower()

        """Upload the file into the server from the Client"""
        if command == 'PUT'.casefold():

            """Get the file name from the command"""
            input_filename = user_input[1]

            """Stop and wait Receiver"""
            try:
                receiver(input_filename, server)
            except socket.timeout:
                server.close()

            """Remove timeout"""
            server.settimeout(None)

            print(f"[SUCCESS] File uploaded.")
            message = "Server response: File uploaded."
            server.sendto(message.encode(FORMAT), addr)  # send message to client

            """Anonymize the file"""
        elif command == 'keyword'.casefold():

            """ Receiving Keyword and target file"""
            keyword = user_input[1]
            file_name = user_input[2]

            """Read file"""
            file = open(file_name, 'r')
            data = file.read()

            """Generate the output file name"""
            output_filename = remove_suffix(file_name, '.txt') + '_anon.txt'

            """Open the output file with write permission"""
            output_file = open(output_filename, 'w+')

            """ Anonymizing File """
            compiled_data = re.compile(keyword, re.IGNORECASE)
            anonymized_data = compiled_data.sub(''.join('X' * len(keyword)), data)
            output_file.write(anonymized_data)

            print(f"[SUCCESS] File %s anonymized. Output file is %s." % (file_name, output_filename))
            message = "Server response: File %s anonymized. Output file is %s." % (file_name, output_filename)
            output_file.close()

            server.sendto(message.encode(FORMAT), addr)  # send message to client

        elif command == 'GET'.casefold():

            """Get the output file name from the command"""
            output_filename = user_input[1]

            """Stop and wait sender"""
            try:
                sender(output_filename, addr, server)
            except socket.timeout:
                server.close()

            """Remove timeout"""
            server.settimeout(None)

        elif command == 'quit'.casefold():
            """ Closing the connection from the client. """
            print(f"[DISCONNECTED] {addr} disconnected.")


"""
This is a helper function to rename an output file after anonymization. 
The reason why I implemented this function is because remove_suffix function
does not exist in early versions of python (available in 3.9+). Therefore, I have used this source,
https://stackoverflow.com/questions/66683630/removesuffix-returns-error-str-object-has-no-attribute-removesuffix
to name output files.
"""


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


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
    LEN = str(os.path.getsize(filename)).encode(FORMAT)

    """Send LEN message"""
    conn.sendto(LEN, dest_addr)

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

                elif message == "FIN":
                    return acknowledged

                """Timeout after a data packet"""
            except socket.timeout:
                message = "Did not receive ACK. Terminating."
                print(message)
                return acknowledged


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
        if int(LEN) == received_size:
            file.close()
            conn.sendto("FIN".encode(FORMAT), source_addr)
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
            return

        try:
            """Set server timeout"""
            file.write(data)
            conn.sendto("ACK".encode(FORMAT), source_addr)
            """Set server timeout"""
            conn.settimeout(1)  # timeout is 1 second

            """Timeout after ACK"""
        except socket.timeout:
            message = "Data transmission terminated prematurely."
            print(message)
            file.close()
            return


if __name__ == "__main__":
    main()
