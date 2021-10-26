"""
References:
https://www.youtube.com/watch?v=MEcL0-3k-2c
"""
import socket
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = sys.argv[1]  # 4455
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"


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

    # should i close file and reopen at each command?
    while True:

        """ Server has accepted the connection from the client. """
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")

        """Listen to command from client"""
        command = conn.recv(SIZE).decode(FORMAT)

        if command is 'PUT'.casefold():

            """ Receiving the filename from the client. """
            filename = conn.recv(SIZE).decode(FORMAT)
            print(f"[RECV] Receiving the filename.")

            output_filename = filename.removesuffix('.txt') + '_anon.txt' # open/create anon text file
            # https://stackoverflow.com/questions/6224052/what-is-the-difference-between-a-string-and-a-byte-string
            file = open(output_filename, "wb")
            conn.send("Filename received.".encode(FORMAT))

            """ Receiving the file data from the client. """
            data = conn.recv(SIZE).decode(FORMAT)
            print(f"[RECV] Receiving the file data.")
            conn.send("File data received".encode(FORMAT))

        elif command is 'keyword'.casefold():

            """ Receiving Keyword """
            keyword = conn.recv(SIZE).decode(FORMAT)
            print(f"[RECV] Receiving the keyword.")
            conn.send("Keyword received".encode(FORMAT))

            """ Anonymizing File """
            data = data.replace(keyword, ''.join('X' * len(keyword)))
            file.write(data)
            conn.send("File is anonymized".encode(FORMAT))

        elif command is 'GET'.casefold():

            #  https://stackoverflow.com/questions/29110620/how-to-download-file-from-local-server-in-python
            """Send output data to client"""
            for data in file:
                conn.sendall(data)

            """ Closing the file. """
            file.close()

        elif command is 'exit'.casefold():
            """ Closing the connection from the client. """
            conn.close()
            print(f"[DISCONNECTED] {addr} disconnected.")


if __name__ == "__main__":
    main()
