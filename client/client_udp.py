"""
Command line arguments:
Enter command:
PUT "filename" client uploads text file to server - client
GET "filename" server anonymizes file from client - client downloads anonymized version of file
Keyword "keyword" specifies keyword to be anonymized with keyword length of X's - client
Quit quits the program "Exiting program!"

"Awaiting server response."
"Server response: file uploaded, file file.txt anonymized. Output file is file_anon.txt

announce number of bytes to be sent - client
keep track of how many bytes are received -server
stop after each datagram sent, and wait for an ack from the receiver

Custom stop-and-wait reliability over UDP
References
client sends file to server, server saves the file and anonymizes it
https://github.com/preetha2711/Stop-and-Wait-Protocol
https://github.com/nikhilroxtomar/Stop-and-Wait-Protocol-Implemented-in-UDP-C
https://stackoverflow.com/questions/15909064/python-implementation-for-stop-and-wait-algorithm
https://stackoverflow.com/questions/5343358/stop-and-wait-socket-programming-with-udp#:~:text=The%20stop%20and%20wait%20protocol,before%20sending%20the%20next%20packet.
https://github.com/mj2266/stop-and-wait-protocol
https://github.com/z9z/reliable_data_transfer
https://github.com/z9z/reliable_data_transfer

sender server
receive client

"""
import os
import socket
import sys

IP = sys.argv[1]  # 127.0.1.1
PORT = int(sys.argv[2])  # 4455
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024


def main():
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """Set server timeout"""
    client.settimeout(1)  # timeout is 1 second

    """Continue getting input from the user until user quits"""
    while True:

        user_input = input("Enter command:")
        """split the command into parts"""
        split_input = user_input.split()
        """get the command"""
        command = split_input[0]

        """send the commands to the Server"""
        client.sendto(user_input.encode(FORMAT), ADDR)

        print("Awaiting server response.")

        """Upload the file into the server"""
        if command == 'PUT'.casefold():

            """get the file name from the command line argument"""
            input_filename = split_input[1]

            sender(input_filename, ADDR, client)

            """Remove timeout"""
            client.settimeout(60)

        # Download the file from the Server
        elif command == 'GET'.casefold():

            """extract the output file name from the command line arguments"""
            output_filename = split_input[1]

            receiver(output_filename, client)

            """Remove timeout"""
            client.settimeout(60)

        # quit the program and close connection
        elif command == 'quit'.casefold():
            print("Exiting program!")
            exit(0)
            break

        """receive the message from the server"""
        message, addr = client.recvfrom(SIZE)
        print(message.decode(FORMAT))

    client.close()


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

    """Check if all expected bytes are received"""
    while os.path.getsize(filename) != file_size:

        """write the contents of file into the file"""
        try:
            """receive the content of file from the server"""
            data, source_addr = conn.recvfrom(1000)
            data = data.decode(FORMAT)

            """Set server timeout"""
            conn.settimeout(1)  # timeout is 1 second

            """Timeout after LEN message: need fix"""
        except socket.timeout:
            message = "Did not receive data. Terminating."
            print(message)
            file.close()
            return

        # reset timeout
        conn.settimeout(60)

        try:
            """Set server timeout: received message is written to file fix is stop once size is reached"""
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


if __name__ == "__main__":
    main()
