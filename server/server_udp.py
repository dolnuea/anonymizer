"""
Custom stop-and-wait reliability over UDP
References
client sends file to server, server saves the file and anonymizes it
https://github.com/preetha2711/Stop-and-Wait-Protocol
https://github.com/nikhilroxtomar/Stop-and-Wait-Protocol-Implemented-in-UDP-C
"""
import os
import socket
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])  # 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
download_dir = os.getcwd()  # download in same folder (working directory


# should I send the input file from client to server too? or is it ok to assume the file already exists theer?
def main():
    print("ip is " + socket.gethostbyname(socket.gethostname()))
    print("[STARTING] Server is starting.")
    """ Staring a TCP socket. """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """ Bind the IP and PORT to the server. """
    server.bind(ADDR)

    """ Server is listening, i.e., server is now waiting for the client to connected. """
    server.listen()
    print("[LISTENING] Server is listening.")

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
            message = "Server response: File uploaded."
            input_file.close()

        elif command == 'keyword'.casefold():

            """ Receiving Keyword """
            keyword = user_input[1]

            output_filename = remove_suffix(input_filename, '.txt') + '_anon.txt'
            print(output_filename)

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

            output_filename = user_input[1]

            # https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python

            output_file = open(output_filename, "r")  # open file in read format

            file_size = os.path.getsize(output_filename)

            print(file_size)

            server.sendall(str(file_size).encode(FORMAT))  # send the file size

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


def send_ack(user_input, addr, socket):
    global ACK

    while user_input:
        socket.sendto(bytes(user_input), addr)
        acknowledged = False
        while not acknowledged:
            try:
                ACK, address = socket.recvfrom(SIZE)
                acknowledged = True
            except socket.timeout:
                socket.sendto(bytes(user_input), addr)
        print(ACK)
        user_input = input()


def receive_ack():
    pass


if __name__ == "__main__":
    main()
