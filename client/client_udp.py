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
https://stackoverflow.com/questions/5343358/stop-and-wait-socket-programming-with-udp#:~:text=The%20stop%20and%20wait%20protocol,before%20sending%20the%20next%20packet.
https://github.com/mj2266/stop-and-wait-protocol
https://github.com/z9z/reliable_data_transfer
https://github.com/z9z/reliable_data_transfer

sender server
receive client

"""
import socket
import sys
import os

IP = sys.argv[1]  # 127.0.1.1
PORT = int(sys.argv[2])  # 4455
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
download_dir = os.getcwd()  # download in working dir


def main():
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    """ Connecting to the server. """
    client.connect(ADDR)

    while True:

        user_input = input("Enter command:")
        split_input = user_input.split()
        command = split_input[0]

        client.sendall(user_input.encode(FORMAT))  # send command

        print("Awaiting server response.")

        if command == 'get'.casefold():

            output_filename = split_input[1]  # extract the output file name from the command

            # download a file created by server:
            #  https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python

            output_file = open(output_filename, "w+")

            file_size = client.recv(SIZE).decode(FORMAT)

            print(file_size)

            data = client.recv(int(file_size)).decode(FORMAT)

            output_file.write(data)
            output_file.close()

        elif command == 'quit'.casefold():
            print("Exiting program!")
            exit(0)
            break

        print(client.recv(SIZE).decode(FORMAT))  # receive the message from the server

    client.close()


if __name__ == "__main__":
    main()
