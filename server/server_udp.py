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
"""
import os
import socket
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])  # 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"


# download_dir = os.getcwd()  # download in same folder (working directory


def main():
    print("IP: " + socket.gethostbyname(socket.gethostname()))
    print("[STARTING] Server is starting.")

    """ Staring a TCP socket. """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """ Bind the IP and PORT to the server. """
    server.bind(ADDR)

    """ Server is listening, i.e., server is now waiting for the client to connected. """
    # server.listen()
    print("[LISTENING] Server is listening.")

    """ Server has accepted the connection from the client. """
    # server, addr = server.accept()
    # print(f"[NEW CONNECTION] {addr} connected.")

    message = None

    while True:
        """Set server timeout"""
        server.settimeout(1)  # timeout is 1 second

        """Listen to command from client"""
        user_input = server.recv(SIZE)
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

            print(f"[RECV] File uploaded.")
            message = "Server response: File uploaded."

        # Anonymize the file
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

        elif command == 'GET'.casefold():

            """Get the output file name from the command"""
            output_filename = user_input[1]

            sender(output_filename, ADDR, server)

            print(f"[RECV] File %s downloaded." % output_filename)
            message = "File %s downloaded." % output_filename

        elif command == 'quit'.casefold():
            """ Closing the connection from the client. """
            print(f"[DISCONNECTED] {ADDR} disconnected.")

        server.sendall(message.encode(FORMAT))  # send message to client
    server.close()


# https://stackoverflow.com/questions/66683630/removesuffix-returns-error-str-object-has-no-attribute-removesuffix
def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


"""
 After every send, you wait for an acknowledgement message
 to come in, and every time you receive, you send an 
 acknowledgement.
"""

"""Stop and wait functions: Sender and receiver"""

"""

    Sender:
    
    1)  ('GET') Let client/receiver know how many bytes of data to expect.
    The length message should contain the string LEN:Bytes
    
    2) The sender splits the data into equal chunks of 1000 bytes each, and
    proceeds to send the data one chunk at a time.

    After transmitting each chunk, the sender stops and waits for
    an acknowledgement from the receiver. To this end, the receiver
    has to craft and send a special message containing the string ACK.
    
    Receiver:

    3) once the receiver receives all expected bytes (as per the LEN message),
    the receiver will craft a special message containing the string FIN. This message
    will trigger connection termination.
    
    Timeout:
    
    Receiver:
    Timeout after LEN message: If no data arrives at the receiver within one
    second from the reception of a LEN message, the receiver program
    should terminate, displaying “Did not receive data.
    Terminating.”
    
    Sender
    Timeout after a data packet: If no ACK is received by the sender within
    one second from transmitting a data packet, the sender will terminate,
    displaying “Did not receive ACK. Terminating.”
    
    Receiver
    Timeout after ACK: If no data is received by the received within one
    second of issuing an ACK, the receiver will terminate, displaying “Data
    transmission terminated prematurely.”.

"""


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
    LEN = str(os.path.getsize(filename))

    """Send LEN message"""
    conn.sendto(bytes(LEN), dest_addr)

    """split the data into equal chunks of 1000 bytes each"""
    data_chunks = ([*data])  # unpack data into chars

    """Send the data packets to the server, 1000 bytes a time
    Resource: https://stackoverflow.com/questions/15909064/python-implementation-for-stop-and-wait-algorithm
    """

    """Initialize that acknowledge has not been received"""
    acknowledged = False
    ACK = None

    """Send the data one chunk at a time"""
    for data_chunk in data_chunks:
        conn.sendto(bytes(data_chunk), dest_addr)
        while not acknowledged:
            try:
                ACK, addr = conn.recvfrom(SIZE)
                acknowledged = True
            except socket.timeout:
                message = "Did not receive ACK. Terminating."
                print(message)
                # conn.sendall(message.encode(FORMAT))
                conn.close()
        print(ACK)


def receiver(filename, conn):
    """
    Data Receiver sends the acknowledgement
    :return:
    """

    """open the output file in write permission: if DNE then create a new file"""
    file = open(filename, "w+")

    """receive the filesize from the server"""
    file_size, source_addr = conn.recvfrom(SIZE)

    """receive the content if file from the server"""
    data, source_addr = conn.recv(int(file_size)).decode(FORMAT)

    """write the contents of file into the file"""
    try:
        while data:
            try:
                file.write(data)
                conn.sendto(bytes("ACK received"), source_addr)
                """Timeout after ACK"""
            except socket.timeout:
                message = "Data transmission terminated prematurely."
                print(message)
                # conn.sendall(message.encode(FORMAT))
                conn.close()
        """Timeout after LEN message"""
    except socket.timeout:
        message = "Did not receive data. Terminating."
        print(message)
        # conn.sendall(message.encode(FORMAT))
        conn.close()

    """close the file"""
    file.close()
    message = "FIN"
    print(message)
    conn.close()


if __name__ == "__main__":
    main()
