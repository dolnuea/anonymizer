"""
References:
https://www.youtube.com/watch?v=MEcL0-3k-2c
"""
import socket
import sys
import os

IP = sys.argv[1]  # socket.gethostbyname(socket.gethostname())
PORT = sys.argv[2]  # 4455
ADDR = (IP, PORT)
FORMAT = "utf-8"
download_dir = os.getcwd()  # download in same folder (working directory
SIZE = 1024


def main():
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Connecting to the server. """
    client.connect(ADDR)

    while True:

        user_input = input("Enter command:")
        user_input = user_input.split()
        command = user_input[0]

        client.send(command.encode(FORMAT))  # send command

        if command is 'put'.casefold():
            input_filename = user_input[1]

            """ Opening and reading the file data. """
            file = open(input_filename, "r")
            data = file.read()

            """ Sending the filename to the server. """
            client.send(input_filename.encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")

            """ Sending the file data to the server. """
            client.send(data.encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")

            """ Closing the file. """
            file.close()

        elif command is 'keyword'.casefold():
            keyword = user_input[1]
            # sent keyword to server
            client.send(keyword.encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER]: {msg}")

        elif command is 'get'.casefold():
            output_filename = user_input[1]
            # download a file created by server
            #  https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python
            with open(os.path.join(download_dir, output_filename), 'wb') as output_file:
                while data:
                    data = client.recv(SIZE)
                    output_file.write(data)
                output_file.close()

        elif command is 'quit'.casefold():
            print("Exiting program!")

            """ Closing the connection from the server. """
            client.close()
            quit()


if __name__ == "__main__":
    main()
