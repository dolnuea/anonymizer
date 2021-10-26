"""
Custom stop-and-wait reliability over UDP
References
client sends file to server, server saves the file and anonymizes it
https://github.com/preetha2711/Stop-and-Wait-Protocol
https://github.com/nikhilroxtomar/Stop-and-Wait-Protocol-Implemented-in-UDP-C
"""
import socket
import sys

IP = socket.gethostbyname(socket.gethostname())  # "127.0.0.1"
PORT = sys.argv[1]  # 4455
SIZE = 1024
FORMAT = "utf-8"

""" Creating the UDP socket """
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

"""
receive filename
receive file data
receive keyword
anonymizes file data and save in a new file
send message to client when done
"""


def main():
    """ Bind the host address with the port """
    server.bind((IP, PORT))
    server.settimeout(0.5)

    file = ''
    data = None

    while True:

        command, addr = server.recvfrom(SIZE)
        command = command.decode(FORMAT)
        print(command)

        if command is 'put'.casefold():
            filename, addr = server.recvfrom(SIZE)
            filename = filename.decode(FORMAT)
            output_filename = filename.removesuffix('.txt') + '_anon.txt'

            file = open(output_filename, "wb")
            server.send("Filename received.".encode(FORMAT))

            """ Receiving the file data from the client. """
            data, addr = server.recvfrom(SIZE)
            data = data.decode(FORMAT)
            print(f"[RECV] Receiving the file data.")
            server.send("File data received".encode(FORMAT))

        elif command is 'keyword'.casefold():
            keyword, addr = server.recvfrom(SIZE)
            keyword = keyword.decode(FORMAT)

            data = data.replace(keyword, ''.join('X' * len(keyword)))
            file.write(data)
            server.send("File is anonymized".encode(FORMAT))

        elif command is 'get'.casefold():
            """Send output data to client"""
            for data in file:
                server.sendall(data)

            """ Closing the file. """
            file.close()

        elif command is 'exit'.casefold():
            print("Client disconnected.")
            server.close()
            exit(0)


def send_ack(user_input, addr):
    global ACK

    while user_input:
        server.sendto(bytes(user_input), addr)
        acknowledged = False
        while not acknowledged:
            try:
                ACK, address = server.recvfrom(SIZE)
                acknowledged = True
            except socket.timeout:
                server.sendto(bytes(user_input), addr)
        print(ACK)
        user_input = input()


def receive_ack():
    pass


if __name__ == "__main__":
    main()
