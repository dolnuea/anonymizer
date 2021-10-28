"""
References:
https://www.youtube.com/watch?v=MEcL0-3k-2c
"""
import socket
import sys
import os

IP = socket.gethostbyname(socket.gethostname())  # sys.argv[1]
PORT = int(sys.argv[1])  # 4455
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
        split_input = user_input.split()
        command = split_input[0]

        client.send(user_input.encode(FORMAT))  # send command

        if command == 'put'.casefold():
            input_filename = split_input[1]
            print("Awaiting server response.")
            print(client.recv(SIZE).decode(FORMAT))

        elif command == 'keyword'.casefold():
            print("Awaiting server response.")
            print(client.recv(SIZE).decode(FORMAT))

        elif command == 'get'.casefold():
            print("Awaiting server response.")
            print(client.recv(SIZE).decode(FORMAT))
            output_filename = split_input[1]

            # download a file created by server
            #  https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python

            output_file = open(output_filename, "w")

            file_size = os.path.getsize(input_filename)
            print(file_size)  # 14480

            data = client.recv(file_size).decode(FORMAT)

            output_file.write(data)

            output_file.close()

        elif command == 'quit'.casefold():
            print("Exiting program!")
            exit(0)
            break

    client.close()


if __name__ == "__main__":
    main()
