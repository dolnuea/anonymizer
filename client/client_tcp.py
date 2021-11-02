"""
Luna Dagci
ICSI 516
11/03/2021
Project 1

References:
https://www.youtube.com/watch?v=MEcL0-3k-2c
https://stackoverflow.com/questions/34252273/what-is-the-difference-between-socket-send-and-socket-sendall/34252690
https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python
https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
"""
import socket
import sys
import os

IP = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1000


def main():
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Connecting to the server. """
    client.connect(ADDR)

    """Continue getting input from the user until user quits"""
    while True:

        user_input = input("Enter command:")
        """split the command into parts"""
        split_input = user_input.split()
        """get the command"""
        command = split_input[0]

        """send the commands to the Server"""
        client.send(user_input.encode(FORMAT))

        """Upload the file into the server"""
        if command == 'PUT'.casefold():
            print("Awaiting server response.")

            """get the file name from the command line argument"""
            filename = split_input[1]

            """open file in read permission"""
            file = open(filename, "r")

            data = file.read(SIZE)

            """Read and send the contents in the file"""
            while data:
                client.send(data.encode(FORMAT))
                data = file.read(SIZE)

            """ Closing the file. """
            file.close()

            """receive the message from the server"""
            print(client.recv(SIZE).decode(FORMAT))

        elif command == 'keyword'.casefold():
            print("Awaiting server response.")

            """receive the message from the server"""
            print(client.recv(SIZE).decode(FORMAT))

            """Download the file from the Server"""
        elif command == 'GET'.casefold():

            """extract the output file name from the command line arguments"""
            filename = split_input[1]

            """open the output file in write permission: if DNE then create a new file"""
            file = open(filename, "w+")

            """receive the filesize from the server"""
            LEN = client.recv(SIZE).decode(FORMAT)

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

                """receive the content if file from the server"""
                data = client.recv(SIZE).decode(FORMAT)

                """Recalculate received bytes"""
                received_size += len(data)

                """write the contents of file into the file"""
                file.write(data)

            """close the file"""
            file.close()

            print(f"[RECV] File %s downloaded." % filename)

            """quit the program and close connection"""
        elif command == 'quit'.casefold():
            print("Exiting program!")
            break

    client.close()


def get_size(filename):
    """open file in read permission"""
    file = open(filename, "r")

    LEN = 0

    """
    read the contents in the original file and save the length
    Comments: os.path.getsize was reading the file size incorrectly
    """
    while True:
        data = file.read(SIZE)
        if not data:
            break
        LEN += len(data)

    """ Closing the file. """
    file.close()
    return LEN


if __name__ == "__main__":
    main()
