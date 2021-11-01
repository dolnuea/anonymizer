"""
 After every send, you wait for an acknowledgement message
 to come in, and every time you receive, you send an
 acknowledgement.
"""
import os
import socket

SIZE = 1000
FORMAT = "utf-8"


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
            return

    file.close()
    conn.sendto("FIN".encode(FORMAT), source_addr)