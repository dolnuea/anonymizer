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

        print("Awaiting server response.")
        print(client.recv(SIZE).decode(FORMAT))

        # if command is 'put'.casefold():
        #     input_filename = split_input[1]
        #
        #     """ Opening and reading the file data. """
        #     file = open(input_filename, "r")
        #     data = file.read()
        #
        #     """ Sending the filename to the server. """
        #     client.send(input_filename.encode(FORMAT))
        #     msg = client.recv(SIZE).decode(FORMAT)
        #     print(f"[SERVER]: {msg}")
        #
        #     """ Sending the file data to the server. """
        #     client.send(data.encode(FORMAT))
        #     msg = client.recv(SIZE).decode(FORMAT)
        #     print(f"[SERVER]: {msg}")
        #
        #     """ Closing the file. """
        #     file.close()

        # elif command is 'keyword'.casefold():
        #     keyword = split_input[1]
        #     # sent keyword to server
        #     client.send(keyword.encode(FORMAT))
        #     msg = client.recv(SIZE).decode(FORMAT)
        #     print(f"[SERVER]: {msg}")

        if command == 'get'.casefold():
            output_filename = split_input[1]
            data = client.recv(SIZE)
            # download a file created by server
            #  https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python
            with open(os.path.join(download_dir, output_filename), 'wb') as output_file:
                if not data:
                    break
                output_file.write(data)
                output_file.close()

        elif command == 'quit'.casefold():
            print("Exiting program!")
            exit(0)
            break

    client.close()


if __name__ == "__main__":
    main()
