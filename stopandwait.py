"""
 After every send, you wait for an acknowledgement message
 to come in, and every time you receive, you send an
 acknowledgement.
"""

import os
import socket

SIZE = 1024
FORMAT = "utf-8"


def sender(filename, dest_addr, conn):
    """
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
    byte_size = 1000
    data_chunks = [byte_chunks[x:x + byte_size] for x in range(0, len(byte_chunks), byte_size)]

    """Send the data packets to the server, 1000 bytes a time
    Resource: https://stackoverflow.com/questions/15909064/python-implementation-for-stop-and-wait-algorithm
    """

    """Send the data one chunk at a time"""
    for data_chunk in data_chunks:
        """Initialize that acknowledge has not been received"""
        acknowledged = False
        while not acknowledged:
            try:
                """Set server timeout"""
                conn.sendto(''.join(data_chunk).encode(FORMAT), dest_addr)
                conn.settimeout(1)  # timeout is 1 second
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
    Data Receiver sends the acknowledgement
    :return:
    """

    """open the output file in write permission: if DNE then create a new file"""
    file = open(filename, "w+")

    """receive the filesize from the server"""
    file_size, source_addr = conn.recvfrom(SIZE)

    file_size = file_size.decode(FORMAT)

    while True:

        """write the contents of file into the file"""
        try:

            """Check if all expected bytes are received"""
            if os.path.getsize(filename) == file_size:
                file.close()
                conn.sendto("FIN".encode(FORMAT), source_addr)
                break

            """Set server timeout"""
            conn.settimeout(1)  # timeout is 1 second

            """receive the content of file from the server"""
            data, source_addr = conn.recvfrom(1000)
            data = data.decode(FORMAT)

            try:
                """Set server timeout"""
                conn.settimeout(1)  # timeout is 1 second
                file.write(data)
                conn.sendto("ACK".encode(FORMAT), source_addr)

                """Timeout after ACK"""
            except socket.timeout:
                message = "Data transmission terminated prematurely."
                print(message)
                file.close()
                return

            """Timeout after LEN message"""
        except socket.timeout:
            message = "Did not receive data. Terminating."
            print(message)
            file.close()
            return
