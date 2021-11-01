"""
Custom stop-and-wait reliability over UDP
References
client sends file to server, server saves the file and anonymizes it
https://github.com/preetha2711/Stop-and-Wait-Protocol
https://github.com/nikhilroxtomar/Stop-and-Wait-Protocol-Implemented-in-UDP-C
https://stackoverflow.com/questions/15909064/python-implementation-for-stop-and-wait-algorithm
https://stackoverflow.com/questions/5343358/stop-and-wait-socket-programming-with-udp#:~:text=The%20stop%20and%20wait%20protocol,before%20sending%20the%20next%20packet.
https://github.com/mj2266/stop-and-wait-protocol
https://github.com/z9z/reliable_data_transfer
https://www.isi.edu/nsnam/DIRECTED_RESEARCH/DR_HYUNAH/D-Research/stop-n-wait.html
https://stackoverflow.com/questions/15705948/python-socketserver-timeout
timeout issue
Did not receive data. Terminating.
client didnt print message bc it was not fully received
"""
import os
import socket
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])  # 4450
SIZE = 1024
FORMAT = "utf-8"

def main():
    print("IP: " + socket.gethostbyname(socket.gethostname()))

    """ Staring a UDP socket. """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """ Bind the IP and PORT to the server. """
    server.bind((IP, PORT))

    message = None

    while True:

        """get to command from client"""
        user_input, addr = server.recvfrom(SIZE)
        user_input = user_input.decode(FORMAT)
        print(user_input)

        user_input = user_input.split()
        command = user_input[0]

        """Upload the file into the server from the Client"""
        if command == 'PUT'.casefold():

            """Get the file name from the command"""
            input_filename = user_input[1]

            """Stop and wait Receiver"""
            receiver(input_filename, server)

            """Remove timeout"""
            server.settimeout(60)

            print(f"[RECV] File uploaded.")
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
            print(output_filename)

            """Open the output file with write permission"""
            output_file = open(output_filename, 'w+')

            """ Anonymizing File """
            data = data.replace(keyword, ''.join('X' * len(keyword)))
            output_file.write(data)

            print(f"[RECV] Server response: File %s anonymized. Output file is %s." % (file_name, output_filename))
            message = "Server response: File %s anonymized. Output file is %s." % (file_name, output_filename)
            output_file.close()

            file_size = os.path.getsize(output_filename)
            print(file_size)

            server.sendto(message.encode(FORMAT), addr)  # send message to client

        elif command == 'GET'.casefold():

            """Get the output file name from the command"""
            output_filename = user_input[1]

            sender(output_filename, addr, server)
            """Remove timeout"""
            server.settimeout(60)

            print(f"[RECV] File %s downloaded." % output_filename)
            message = "File %s downloaded." % output_filename

            server.sendto(message.encode(FORMAT), addr)  # send message to client

        elif command == 'quit'.casefold():
            """ Closing the connection from the client. """
            print(f"[DISCONNECTED] {addr} disconnected.")


# https://stackoverflow.com/questions/66683630/removesuffix-returns-error-str-object-has-no-attribute-removesuffix
def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string
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

    """
    no data received after length
    no data received after ack
    """

    while True:

        """write the contents of file into the file"""
        try:

            """Check if all expected bytes are received"""
            if os.path.getsize(filename) == file_size:
                file.close()
                conn.sendto("FIN".encode(FORMAT), source_addr)
                break

            """receive the content of file from the server"""
            data, source_addr = conn.recvfrom(1000)
            data = data.decode(FORMAT)

            """Set server timeout"""
            conn.settimeout(1)  # timeout is 1 second

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

            """Timeout after LEN message"""
        except socket.timeout:
            message = "Did not receive data. Terminating."
            print(message)
            file.close()
            return


if __name__ == "__main__":
    main()
