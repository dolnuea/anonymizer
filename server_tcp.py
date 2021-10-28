"""
References:
https://www.youtube.com/watch?v=MEcL0-3k-2c
Enter command: put test.txt
 Awaiting server response.
 Server response: File uploaded.
 Enter command: keyword Fall test.txt
 Awaiting server response.
 Server response: File test.txt anonymized. Output file is
test_anon.txt
 Enter command: get test_anon.txt
 File test_anon.txt downloaded.
 Enter command: quit
 Exiting program!
"""
import os
import socket
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])  # 45668
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
download_dir = os.getcwd()  # download in same folder (working directory

def main():
    print("[STARTING] Server is starting.")
    """ Staring a TCP socket. """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Bind the IP and PORT to the server. """
    server.bind(ADDR)

    """ Server is listening, i.e., server is now waiting for the client to connected. """
    server.listen()
    print("[LISTENING] Server is listening.")

    file = ''
    data = None

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

        if command == 'PUT'.casefold():
            input_filename = user_input[1]

            """ Opening and reading the file data. """
            input_file = open(input_filename, "r")
            data = input_file.read()
            print(f"[RECV] File uploaded.")
            server.send("Server response: File uploaded.".encode(FORMAT))
            input_file.close()

        elif command == 'keyword'.casefold():

            """ Receiving Keyword """
            keyword = user_input[1]

            output_filename = remove_suffix(input_filename,'.txt') + '_anon.txt'
            print(output_filename)

            output_file = open(output_filename, "w")

            """ Anonymizing File """
            data = data.replace(keyword, ''.join('X' * len(keyword)))
            output_file.write(data)

            print(f"[RECV] Server response: File %s anonymized. Output file is %s." % (input_filename, output_filename))
            message = "Server response: File %s anonymized. Output file is %s." % (input_filename, output_filename)
            server.send(message.encode(FORMAT))
            output_file.close()

        elif command == 'GET'.casefold():

            #  https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python
            file = open(output_filename, "r")

            print(f"[RECV] File %s downloaded." % output_filename)
            message = "File %s downloaded." % output_filename
            server.send(message.encode(FORMAT))

            file_size = os.path.getsize(output_filename)
            print(file_size)
            print(output_filename)

            content = ''

            """Send output data to client"""
            for data in file:
                content += data

            server.send(content.encode(FORMAT))

            """ Closing the file. """
            file.close()

            file_size = os.path.getsize(output_filename)
            print(file_size)
            print(output_filename)

        elif command == 'quit'.casefold():
            """ Closing the connection from the client. """
            print(f"[DISCONNECTED] {addr} disconnected.")
            server.send("Exiting program!".encode(FORMAT))
            break

    server.close()


# https://stackoverflow.com/questions/66683630/removesuffix-returns-error-str-object-has-no-attribute-removesuffix
def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


if __name__ == "__main__":
    main()
