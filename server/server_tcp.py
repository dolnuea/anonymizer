"""
For the base of TCP implementation for both server and client,
I have used the reference, https://www.youtube.com/watch?v=MEcL0-3k-2c,
which is an example of sending and receiving a file in TCP connection.
https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
"""
import os
import socket
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
ADDR = (IP, PORT)
SIZE = 1000
FORMAT = "utf-8"


def main():
    """This will tell the IP address (I put it for easiness)"""
    print("IP: " + socket.gethostbyname(socket.gethostname()))

    message = None

    while True:
        print("[STARTING] Server is starting.")

        """ Staring a TCP socket. """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        """ Bind the IP and PORT to the server. """
        server.bind(ADDR)

        """ Server is listening, i.e., server is now waiting for the client to connected. """
        server.listen()
        print("[LISTENING] Server is listening.")

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

            """Upload the file into the server from the Client"""
            if command == 'PUT'.casefold():

                """Get the file name from the command"""
                input_filename = user_input[1]

                """open the output file in write permission: if DNE then create a new file"""
                file = open(input_filename, "w+")

                """Check if all expected bytes are received"""
                while True:

                    """receive the content if file from the server"""
                    data = server.recv(SIZE).decode(FORMAT)
                    if not data or data == '' or data == '\n' or data == '\t' or data == '\n' or data == '\r' or data == 'help pls':
                        break
                    """write the contents of file into the file"""
                    file.write(data)

                """close the file"""
                file.close()

                print(f"[RECV] File uploaded.")
                message = "Server response: File uploaded."

                """send message to client"""
                server.send(message.encode(FORMAT))

            # Anonymize the file
            elif command == 'keyword'.casefold():

                """ Receiving Keyword and target file"""
                keyword = user_input[1]
                file_name = user_input[2]

                """Read file"""
                file = open(file_name, 'r')
                data = file.read()

                """Generate the output file name"""
                output_filename = remove_suffix(file_name, '.txt') + '_anon.txt'
                print(output_filename)

                """Open the output file with write permission"""
                output_file = open(output_filename, 'w+')

                """ Anonymizing File """
                data = data.replace(keyword, ''.join('X' * len(keyword)))
                output_file.write(data)

                print(f"[RECV] Server response: File %s anonymized. Output file is %s." % (file_name, output_filename))
                message = "Server response: File %s anonymized. Output file is %s." % (file_name, output_filename)
                output_file.close()

                file_size = os.path.getsize(output_filename)
                print(file_size)

                """send message to client"""
                server.send(message.encode(FORMAT))

            elif command == 'GET'.casefold():

                """Get the output file name from the command"""
                output_filename = user_input[1]

                """open file in read permission"""
                file = open(output_filename, "r")

                """read the contents in the original file"""
                data = file.read()

                """ Closing the file. """
                file.close()

                """Get the File size"""
                LEN = str(os.path.getsize(output_filename))

                """send the file size over to the server"""
                server.send(LEN.encode(FORMAT))

                """split the data into equal chunks of 1000 bytes each
                    Resource: https://www.codegrepper.com/code-examples/python/python+split+array+into+chunks+of+size+n
                    """
                byte_chunks = ([*data])
                data_chunks = [byte_chunks[x:x + SIZE] for x in range(0, len(byte_chunks), SIZE)]

                """send the contents of the input file to the server"""
                for data_chunk in data_chunks:
                    server.send(''.join(data_chunk).encode(FORMAT))

                print(f"[RECV] File %s downloaded." % output_filename)

            elif command == 'quit'.casefold():
                """ Closing the connection from the client. """
                print(f"[DISCONNECTED] {addr} disconnected.")
                break

        server.close()


"""
This is a helper function to rename an output file after anonymization. 
The reason why I implemented this function is because remove_suffix function
does not exist in early versions of python (available in 3.9+). Therefore, I have used this source,
https://stackoverflow.com/questions/66683630/removesuffix-returns-error-str-object-has-no-attribute-removesuffix
to name output files.
"""


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


if __name__ == "__main__":
    main()
