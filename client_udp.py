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
https://github.com/z9z/reliable_data_transfer

sender server
receive client

"""

import socket
import sys
import os


"""
receive filename
receive file data
receive keyword
anonymizes file data and save in a new file
send message to client when done
"""


def main():

    IP = sys.argv[1]  # socket.gethostbyname(socket.gethostname())
    PORT = sys.argv[2]  # 4455
    ADDR = (IP, PORT)
    FORMAT = "utf-8"
    download_dir = os.getcwd()  # download in same folder (working directory
    SIZE = 1024

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # client.settimeout(0.5)

    while True:
        user_input = input("Enter command:")
        user_input = user_input.split()
        command = user_input[0]

        user_input = input()  # raw_input is input in python 3: https://stackoverflow.com/questions/20332320/pycharm

        """Send command"""
        client.sendto(command.encode(FORMAT), ADDR)

        if command is 'put'.casefold():
            input_filename = user_input[1]
            client.sendto(input_filename.encode(FORMAT), ADDR)

            data, ADDR = client.recvfrom(SIZE)
            data = data.decode(FORMAT)
            print(f"Server: {data}")

        elif command is 'keyword'.casefold():
            keyword = user_input[1]
            client.sendto(keyword.encode(FORMAT), ADDR)

            data, ADDR = client.recvfrom(SIZE)
            data = data.decode(FORMAT)
            print(f"Server: {data}")

        elif command is 'get'.casefold():
            output_filename = user_input[1]
            client.sendto(output_filename.encode(FORMAT), ADDR)

            with open(os.path.join(download_dir, output_filename), 'wb') as output_file:
                while data:
                    data = client.recv(SIZE)
                    output_file.write(data)
                output_file.close()

            data, ADDR = client.recvfrom(SIZE)
            data = data.decode(FORMAT)
            print(f"Server: {data}")

        elif command is 'quit'.casefold():
            print("Exiting program!")
            client.close()
            quit()


if __name__ == "__main__":
    main()
