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
ADDR = (IP, PORT)
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

    while True:
        data, addr = server.recvfrom(SIZE)
        data = data.decode("utf-8")
        print(data)

        if data == "!EXIT":
            print("Client disconnected.")
            break

        print(f"Client: {data}")

        data = data.upper()
        data = data.encode("utf-8")
        server.sendto(data, addr)


def send_ack(user_input):
    global ACK

    while user_input:
        server.sendto(bytes(user_input), ADDR)
        acknowledged = False
        # spam dest until they acknowledge me (sounds like my kids)
        while not acknowledged:
            try:
                ACK, address = server.recvfrom(SIZE)
                acknowledged = True
            except socket.timeout:
                server.sendto(bytes(user_input), ADDR)
        print(ACK)
        user_input = input()


if __name__ == "__main__":
    main()
