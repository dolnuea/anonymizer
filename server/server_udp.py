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

    """Set server timeout"""
    server.settimeout(0.5)

    """ Server is listening, i.e., server is now waiting for the client to connected. """
    server.listen()
    print("[LISTENING] Server is listening.")

    """ Server has accepted the connection from the client. """
    server, addr = server.accept()
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:

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
            """Open the file with write permission"""
            input_file = open(input_filename, "w+")

            """Receive the filesize from the client"""
            file_size = server.recv(SIZE).decode(FORMAT)
            # print(file_size)

            """Receive the contents of the original file from the server"""
            data = server.recv(int(file_size)).decode(FORMAT)
            """Write the contents of the original file into input file"""
            input_file.write(data)
            """Close the file"""
            input_file.close()

            # """ Opening and reading the file data. """
            # input_file = open(input_filename, "r")
            # data = input_file.read()
            print(f"[RECV] File uploaded.")
            message = "Server response: File uploaded."
            # input_file.close()

        # Anonymize the file
        elif command == 'keyword'.casefold():

            """ Receiving Keyword """
            keyword = user_input[1]

            """Generate the output file name"""
            output_filename = remove_suffix(input_filename, '.txt') + '_anon.txt'
            print(output_filename)

            """Open the output file with write permission"""
            output_file = open(output_filename, 'w+')

            """ Anonymizing File """
            data = data.replace(keyword, ''.join('X' * len(keyword)))
            output_file.write(data)

            print(f"[RECV] Server response: File %s anonymized. Output file is %s." % (input_filename, output_filename))
            message = "Server response: File %s anonymized. Output file is %s." % (input_filename, output_filename)
            output_file.close()

            file_size = os.path.getsize(output_filename)
            print(file_size)

        elif command == 'GET'.casefold():

            """Get the output file name from the command"""
            output_filename = user_input[1]

            """Open the output file with write permission"""
            output_file = open(output_filename, "r")  # open file in read format

            """Send the file size to the Client"""
            file_size = os.path.getsize(output_filename)
            print(file_size)
            server.sendall(str(file_size).encode(FORMAT))  # send the file size

            """Send over the contents if the output file to the Client"""
            content = output_file.read()  # read the contents in the anonymized file
            server.sendall(content.encode(FORMAT))  # send the contents of the output file to the client

            """ Closing the file. """
            output_file.close()

            print(f"[RECV] File %s downloaded." % output_filename)
            message = "File %s downloaded." % output_filename

        elif command == 'quit'.casefold():
            """ Closing the connection from the client. """
            print(f"[DISCONNECTED] {addr} disconnected.")
            break

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


def receive_ack(user_input, addr, socket):
    """
    Data Sender receives the acknowledgement
    :param user_input:
    :param addr:
    :param socket:
    :return:
    References:
    https://www.isi.edu/nsnam/DIRECTED_RESEARCH/DR_HYUNAH/D-Research/stop-n-wait.html
    https://stackoverflow.com/questions/15909064/python-implementation-for-stop-and-wait-algorithm
    """

    while user_input:
        socket.sendto(bytes(user_input), addr)
        acknowledged = False
        while not acknowledged:
            try:
                """After transmitting one packet, the sender waits for an 
                acknowledgment (ACK) from the receiver before transmitting
                 the next one"""
                ACK, address = socket.recvfrom(SIZE)
                acknowledged = True
            except socket.timeout:
                """If the sender doesn't receive ACK for previous sent packet
                 after a certain period of time, the sender times out and 
                 retransmits that packet again."""
                socket.sendto(bytes(user_input), addr)
        print(ACK)
        user_input = input()


def send_ack():
    """
    Data Receiver sends the acknowledgement
    :return:
    """
    pass


if __name__ == "__main__":
    main()
