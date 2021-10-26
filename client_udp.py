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

sender server
receive client

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
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

"""
receive filename
receive file data
receive keyword
anonymizes file data and save in a new file
send message to client when done
"""


def main():

    while True:
        user_input = input("Enter command:")
        user_input = user_input.split()
        command = user_input[0]

        client.settimeout(0.5)

        user_input = input()  # raw_input is input in python 3: https://stackoverflow.com/questions/20332320/pycharm
        # -builtin-unresolved-reference

        client.send(command.encode(FORMAT))  # send command

        if command is 'put':
            input_file = user_input[1]
        elif command is 'get':
            output_file = user_input[1]
        elif command is 'keyword':
            keyword = user_input[1]
        elif command is 'quit':
            print("Exiting program!")
            client.close()
            quit()


def receive_ack():
    pass


if __name__ == "__main__":
    main()
