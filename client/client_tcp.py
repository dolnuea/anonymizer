"""
References:
https://www.youtube.com/watch?v=MEcL0-3k-2c
https://stackoverflow.com/questions/34252273/what-is-the-difference-between-socket-send-and-socket-sendall/34252690
https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python
https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
"""
import socket
import sys
import os

IP = sys.argv[1]  # 127.0.1.1
PORT = int(sys.argv[2])  # 4455
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024


def main():
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # https://stackoverflow.com/questions/31826762/python-socket-send-immediately
    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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

        print("Awaiting server response.")

        """Upload the file into the server"""
        if command == 'PUT'.casefold():

            """get the file name from the command line argument"""
            input_filename = split_input[1]

            """open file in read permission"""
            file = open(input_filename, "r")
            """read the contents in the original file"""
            content = file.read()
            file_size = os.path.getsize(input_filename)

            """send the file size over to the server"""
            client.send(str(file_size).encode(FORMAT))
            # print(str(file_size))

            """send the contents of the input file to the server"""
            client.send(content.encode(FORMAT))
            """ Closing the file. """
            file.close()

            # stays hanging
            # for data in file:
            #     print(data)
            #     client.sendall(bytes(data))
            # file.close()

        # Download the file from the Server
        elif command == 'GET'.casefold():

            """extract the output file name from the command line arguments"""
            output_filename = split_input[1]

            """open the output file in write permission: if DNE then create a new file"""
            output_file = open(output_filename, "w+")

            """receive the filesize from the server"""
            file_size = client.recv(SIZE).decode(FORMAT)
            # print(file_size)

            """receive the content if file from the server"""
            data = client.recv(int(file_size)).decode(FORMAT)
            """write the contents of file into the file"""
            output_file.write(data)
            """close the file"""
            output_file.close()

        # quit the program and close connection
        elif command == 'quit'.casefold():
            print("Exiting program!")
            # exit(0)
            break

        """receive the message from the server"""
        print(client.recv(SIZE).decode(FORMAT))

    client.close()


if __name__ == "__main__":
    main()
