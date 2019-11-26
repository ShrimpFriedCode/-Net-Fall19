# **************************************************************
# * a2.py - Ethan Anderson (etmander)
# * UPDATED: 11/25/2019
# * 
# **************************************************************
import Queue
import socket
import sys


# serverTCP manages calls to server, dispatching the appropriate function to handle requests
def serverTCP(HOST, PORT, FILE=None):
    # if we're sending a file, launch file handler
    if (FILE):
        print("server file-TCP")
        serverTCPfile(HOST, PORT, FILE)
    else:
        # else it's call and response
        serverTCPconvo(HOST, PORT)


# function to manage TCP file transfer
def serverTCPfile(HOST, PORT, FILE):
    ACK = "0"  # alternating bit
    buf = Queue.Queue(maxsize=0)  # buffer to store recc'd data in

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create connection
    server.bind((HOST, PORT))

    server.listen(10)
    conn, addr = server.accept()  # accept connection

    while True:  # while we're getting data
        # print("server " + ACK) # print debug
        resp = conn.recv(255)  # get response
        cACK = resp[-1:]  # Alternating bit will be at end of packet

        if (cACK == "2"):  # if bit is set to 2, end of file has been reached
            conn.send("!")  # send ack of EOF
            while (not buf.empty()):  # write contents of buffer to file
                FILE.write(buf.get())
            FILE.close()
            conn.shutdown(2)  # terminate connection
            conn.close()
            sys.exit()

        if (cACK == ACK):  # If response is expected
            buf.put(resp[:-1])  # add data to buffer
            conn.send(ACK)  # send ack of data
            if ACK == "0":  # flip bit
                ACK = "1"
            else:
                ACK = "0"
        else:  # if unexpected response
            conn.send(ACK)  # send request for proper data
            # print("server not equal")  # print debug
            continue  # reset loop

# handler function for call and response operation on TCP
def serverTCPconvo(HOST, PORT):
    # create the socket, bind it to our host IP and port number
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    # listen for any connection attempts, and accept them
    server.listen(10)
    conn, addr = server.accept()

    # loop for input
    while True:
        # rec our data and store it (255 bytes)
        data = conn.recv(255)
        # print out data server side for analysis
        print(data)
        # if 'hello', reply 'world'
        if (data == "hello"):
            conn.send("world\n")
        # if 'goodbye', send 'farewell', shutdown and end the active connection, and listen for new attempts to accept
        elif (data == "goodbye"):
            conn.send("farewell\n")
            conn.shutdown(2)
            conn.close()
            print("closed looking for connections\n")
            server.listen(10)
            conn, addr = server.accept()
            print("new connection detected\n")
        # if 'exit', shutdown program with sys call
        elif (data == "exit"):
            conn.send("ok\n")
            sys.exit(0)
        # else, reply with the rec'd data
        else:
            data = data + "\n"
            conn.send(data)


# Client handler for TCP. Determines which helper function to launch
def clientTCP(HOST, PORT, FILE=None):
    if (FILE):  # if we are sending a file, launch appropriate function
        print("Client file-TCP")
        clientTCPfile(HOST, PORT, FILE)
    else:  # else, it's call and response
        clientTCPconvo(HOST, PORT)

# handler function for TCP file transfer client side
def clientTCPfile(HOST, PORT, FILE):
    ACK = "0"  # alternating bit
    PACK = 0  # iterator for buffer containing file data
    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # connect to server
    cli.connect((HOST, PORT))

    buf = []  # data buffer for file
    f = FILE.read(200)
    while (f):  # read all contents of file to buffer
        buf.append(f)
        f = FILE.read(200)

    cli.settimeout(.1)  # set timeout for response ACK
    while True:  # while handling data
        try:  # if no timeout:
            # print("client " + ACK)  # print debug
            if (PACK >= len(buf)):  # if EOF has been reached
                cli.send("2")  # send termination bit
                resp = cli.recv(255)  # confirm receipt of termination
                if (resp == "!"):  # if termination confirmed:
                    FILE.close()
                    cli.shutdown(2)  # terminate
                    cli.close()
                    sys.exit()
                else:  # else, termination not received and resend
                    continue

            cli.send(buf[PACK] + ACK)  # send data from correct data index, and bit ACK
            resp = cli.recv(255)  # get response
            if resp == ACK:  # if expected:
                PACK = PACK + 1  # set next data to be sent
                if ACK == "0":  # flip bit
                    ACK = "1"
                else:
                    ACK = "0"
            else:  # else, unexpected
                # print("not good")  # print debug
                if ACK == "0":  # flip bit
                    ACK = "1"
                else:
                    ACK = "0"

                PACK = PACK - 1  # set last data to be resent
                continue  # return to top of loop
        except socket.timeout:  # else, timed out, reset loop
            continue


# handler function for TCP call and response
def clientTCPconvo(HOST, PORT):
    print("Client echo-TCP")
    # create the socket, and attempt to connect to the host IP and port #
    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli.connect((HOST, PORT))
    # loop for input
    while True:
        # try-catch statement to catch any disconnections from server to prevent errors.
        try:
            # capture input
            send = str(raw_input())
            # do not permit blank input, for sanity's sake
            while (len(send) == 0):
                send = str(raw_input("Input must not be empty!\n"))
            # send input to server
            cli.send(send)
            # rec response from server and print (255 bytes)
            data = cli.recv(255)
            print(data)
        # catch disconnections and handle
        except(socket.error):
            print("Connection has been closed by server. Goodbye.")
            break


# handler function for UDP operation. Dispatched correct helper functions
def serverUDP(HOST, PORT, FILE=None):
    if (FILE):  # if we are sending a file, launch appropriate helper
        print("server file-UDP")
        serverUDPfile(HOST, PORT, FILE)
    else:  # else, we are using call and response
        print("server echo-UDP")
        serverUDPconvo(HOST, PORT)


# helper function for UDP server file transfer
def serverUDPfile(HOST, PORT, FILE):
    buf = Queue.Queue(maxsize=0)  # create data buffer for file
    # create the UDP socket, and bind it to our host IP and port #
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    # loop
    while True:
        data, addr = server.recvfrom(255)  # get data from client
        cACK = data[-1:]  # alternation bit not used in UDP
        buf.put(data[:-1])  # add data to buffer

        if (cACK == "2"):  # if termination signal:
            while (not buf.empty()):  # write contents of buffer to file
                FILE.write(buf.get())
            FILE.close()
            server.close()  # terminate
            sys.exit()


# server function for UDP echo, handles connections and recc data and creates an appropriate response
def serverUDPconvo(HOST, PORT):
    # create the UDP socket, and bind it to our host IP and port #
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    # loop for input
    while True:
        # get data from a UDP client (255 bytes), store its appropriate information
        data, addr = server.recvfrom(255)
        # print data server side
        print(data)
        # if/then statement functions exact same as serverTCP, except in noted areas
        if (data == "hello"):
            # send response to stored address, instead of an active connection
            server.sendto("world\n", addr)
        elif (data == "goodbye"):
            server.sendto("farewell\n", addr)
            # close the current session
            server.close()
            print("Closed, looking for new connections\n")
            # restart the socket and look for new UDP connections
            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.bind((HOST, PORT))
        elif (data == "exit"):
            server.sendto("ok\n", addr)
            sys.exit(0)
        else:
            data = data + "\n"
            server.sendto(data, addr)


# helper function for RUDP server. Dispatches appropriate helper functions.
def serverRUDP(HOST, PORT, ARG, FILE=None):
    # print(ARG)  # print debug
    if ARG == 1:  # If stop and wait protocol, launch appropriate functions
        # print("stop n wait")
        if (FILE):  # if file transfer, launch appropriate function
            serverRUDPfileWait(HOST, PORT, FILE)
        else:
            serverRUDPconvoWait(HOST, PORT)
    elif ARG == 2:  # if using go back N, launch appropriate functions
        # print("go back N")
        if (FILE):  # if file transfer, launch appropriate function
            serverRUDPfileGo(HOST, PORT, FILE)
        else:
            serverRUDPconvoGo(HOST, PORT)
    else:  # else, its an invalid arg and we exit with errored status
        print("Invalid Arg!")
        sys.exit(1)


# helper function for RUDP file transfer with go-back-N implementation
def serverRUDPfileGo(HOST, PORT, FILE):
    print("server file-RUDP Go")
    buf = Queue.Queue(maxsize=0)  # buffer for file data
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create connection
    server.bind((HOST, PORT))
    nextPack = 0  # index for expected packet

    while True:  # loop
        data, addr = server.recvfrom(255)  # get data from client

        if data == "//EOF//":  # if EOF flag received
            server.sendto("//EOF//", addr)  # send confirmation of termination
            while (not buf.empty()):  # write contents of buffer to file
                FILE.write(buf.get())
            FILE.close()
            server.close()  # terminate
            sys.exit()

        curr = data.split("ACK=")[1]  # get ACK number from received packet
        if int(curr) == nextPack:  # if it is what we expected
            # print("got " + str(curr))  # print debug
            buf.put(data.split("ACK=")[0])  # write data to buffer
            server.sendto(str(nextPack), addr)  # send confirmation of receipt
            nextPack = nextPack + 1  # increase next expected packet
        else:  # else, we are out of order
            # print("bad, requesting " + str(nextPack))  # print debug
            server.sendto(str(nextPack - 1), addr)  # send requested packet to client


# helper function for server file transfer on RUDP with stop and wait implementation
def serverRUDPfileWait(HOST, PORT, FILE):
    print("server file-RUDP wait")
    ACK = "1" # alternating bit
    buf = Queue.Queue(maxsize=0)  # buffer for file data
    # create the UDP socket, and bind it to our host IP and port #
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    # loop
    while True:
        data, addr = server.recvfrom(255)
        # print("server " + ACK)
        cACK = data[-1:]  # bit is at end of data

        if (cACK == "2"):  # if termination signal
            server.sendto("!", addr)  # send confirmation of termination
            while (not buf.empty()):  # write buffer contents to file
                FILE.write(buf.get())
            FILE.close()
            server.close()  # terminate
            sys.exit()

        if (cACK == ACK):  # if expected
            buf.put(data[:-1])  # write data to buffer
            # print("got " + str(ACK))  # print debug
            server.sendto(ACK, addr)  # send ACK of data received
            if ACK == "0":  # flip bit
                ACK = "1"
            else:
                ACK = "0"
        else:  # else, unexpected packet
            server.sendto(ACK, addr)  # request correct data
            # print("server not equal")  # print debug
            continue  # reset loop


# server function for RUDP echo, not implemented with go-back-N. Placeholder
def serverRUDPconvoGo(HOST, PORT):
    # create the UDP socket, and bind it to our host IP and port #
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    # loop for input
    while True:
        # get data from a UDP client (255 bytes), store its appropriate information
        data, addr = server.recvfrom(255)
        # print data server side
        print(data)
        # if/then statement functions exact same as serverTCP, except in noted areas
        if (data == "hello"):
            # send response to stored address, instead of an active connection
            server.sendto("world\n", addr)
        elif (data == "goodbye"):
            server.sendto("farewell\n", addr)
            # close the current session
            server.close()
            print("Closed, looking for new connections\n")
            # restart the socket and look for new UDP connections
            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.bind((HOST, PORT))
        elif (data == "exit"):
            server.sendto("ok\n", addr)
            sys.exit(0)
        else:
            data = data + "\n"
            server.sendto(data, addr)


# server function for RUDP echo. Not implemented with stop-N-wait. Placeholder.
def serverRUDPconvoWait(HOST, PORT):
    # create the UDP socket, and bind it to our host IP and port #
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    # loop for input
    while True:
        # get data from a UDP client (255 bytes), store its appropriate information
        data, addr = server.recvfrom(255)
        # print data server side
        print(data)
        # if/then statement functions exact same as serverTCP, except in noted areas
        if (data == "hello"):
            # send response to stored address, instead of an active connection
            server.sendto("world\n", addr)
        elif (data == "goodbye"):
            server.sendto("farewell\n", addr)
            # close the current session
            server.close()
            print("Closed, looking for new connections\n")
            # restart the socket and look for new UDP connections
            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.bind((HOST, PORT))
        elif (data == "exit"):
            server.sendto("ok\n", addr)
            sys.exit(0)
        else:
            data = data + "\n"
            server.sendto(data, addr)


# client helper for RUDP. Dispatched appropriate helper functions
def clientRUDP(HOST, PORT, ARG, FILE=None):
    # print(ARG)  # print debug
    if ARG == 1:  # if using stop and wait
        # print("Stop n wait")
        if (FILE):  # if sending a file
            clientRUDPfileWait(HOST, PORT, FILE)  # launch appropriate function
        else:  # else, echo
            clientRUDPconvoWait(HOST, PORT)
    elif ARG == 2:  # if using go back N
        # print("Go back N")
        if (FILE): # if sending a file
            clientRUDPfileGo(HOST, PORT, FILE)  # launch appropriate function
        else:  # else, echo
            clientRUDPconvoGo(HOST, PORT)
    else:  # else, invalid argument received. Exit with error.
        print("Invalid Arg!")
        sys.exit(1)

# helper function for RUDP client file transfer implementing go-back-N
def clientRUDPfileGo(HOST, PORT, FILE):
    print("client file-RUDP Go")
    window = 5  # set our data window
    base = 0  # set our base increment for adding data to window
    pack = 0  # set our current data packet
    lastPack = 0  # set our last confirmed data packet
    i = 0  # iterator for file size
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create connection
    cli.settimeout(.1)  # set timeout
    buf = []  # data buffer for file
    win = [] # window for data
    f = FILE.read(200)
    while (f):  # read contents of file to buffer
        buf.append(f + "ACK=" + str(i))  # add packet number to end of data
        f = FILE.read(200)
        i = i + 1

    while True:  # loop
        if pack < base + window:  # if packet is within window
            if pack >= len(buf):  # if EOF
                # print("EOF")  # print debug
                cli.sendto("//EOF//", ((HOST, PORT)))  # send EOF notice
                try:  # get confirmation of EOF from server
                    resp, serv = cli.recvfrom(255)
                    if resp == "//EOF//":  # if confirmed
                        # print("Ending")  # print debug
                        FILE.close()
                        sys.exit(0)  # exit
                    else:  # else, resend
                        continue
                except socket.timeout:  # if timeout, resend
                    continue

            # print("sending " + str(pack))  # print debug
            cli.sendto(buf[pack], ((HOST, PORT)))  # send data to server
            win.append(buf[pack])  # add data to window
            pack = pack + 1  # increase current data packet to send

        try:  # attempt to get confirmation
            lastPack, serv = cli.recvfrom(255)  # get data

            while int(lastPack) > base:  # if data is within window
                # print("got " + lastPack)  # print debug
                base = base + 1  # slide window
                if win:  # pop data from window
                    del win[0]

        except socket.timeout:  # if timeout
            # print("timeout " + str(lastPack))  # print debug
            # resend all win
            for item in win:
                cli.sendto(item, ((HOST, PORT)))


# helper function for RUDP file trasnfet client side implementing stop and wait
def clientRUDPfileWait(HOST, PORT, FILE):
    ACK = "0"  # alternating bit
    PACK = 1  # current data packet
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create connection
    buf = []  # file data buffer
    f = FILE.read(200)
    while (f):  # read contents of file into buffer
        buf.append(f)
        f = FILE.read(200)

    cli.settimeout(.1)  # set timeout
    while True:  # loop
        try:
            # print("client " + ACK)  # print debug
            if (PACK >= len(buf)):  # if EOF
                cli.sendto("2", ((HOST, PORT)))  # send termination bit
                resp, serv = cli.recvfrom(255)  # get response
                if (resp == "!"):  # if termination confirmed
                    FILE.close()
                    cli.close()  # exit
                    sys.exit()
                else:  # else resend
                    continue

            cli.sendto(buf[PACK] + ACK, ((HOST, PORT)))  # send data and bit to server
            resp, serv = cli.recvfrom(255)  # get response
            if resp == ACK:  # if response is expected
                # print("got " + str(ACK))  # print debug
                PACK = PACK + 1  # set next packet to send
                if ACK == "0":  # flip bit
                    ACK = "1"
                else:
                    ACK = "0"
            else:  # if unexpected
                # print("not good")  # print debug
                if ACK == "0":  # flip bit
                    ACK = "1"
                else:
                    ACK = "0"

                PACK = PACK - 1  # set next packet to send as last sent
                continue  # go to top of loop
        except socket.timeout:  # if timeout, go to top of loop
            continue


# helper function for echo RUDP. Go back N not implemented. Placeholder
def clientRUDPconvoGo(HOST, PORT):
    # create UDP socket, no need to create a connection since UDP
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # try-catch for errors in transmission, while loop for input
    while True:
        try:
            # functions exactly the same as clientTCP, except data is sent to an address rather than an active connection
            send = str(raw_input())
            while (len(send) == 0):
                send = str(raw_input("Input must not be empty!\n"))
            cli.sendto(send, ((HOST, PORT)))
            data, serv = cli.recvfrom(255)
            print(data)
        except(socket.error):
            print("Connection has been closed by server. Goodbye.")
            break


# client for RUDP echo. Stop and wait not implemented. Placeholder
def clientRUDPconvoWait(HOST, PORT):
    # create UDP socket, no need to create a connection since UDP
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # try-catch for errors in transmission, while loop for input
    while True:
        try:
            # functions exactly the same as clientTCP, except data is sent to an address rather than an active connection
            send = str(raw_input())
            while (len(send) == 0):
                send = str(raw_input("Input must not be empty!\n"))
            cli.sendto(send, ((HOST, PORT)))
            data, serv = cli.recvfrom(255)
            print(data)
        except(socket.error):
            print("Connection has been closed by server. Goodbye.")
            break


# helper function for UDP. Dispatches appropriate functions
def clientUDP(HOST, PORT, FILE=None):
    if (FILE):  # if sending a file, use appropriate function
        print("client file-UDP")
        clientUDPfile(HOST, PORT, FILE)
    else:  # else, launch echo function
        print("client echo-UDP")
        clientUDPconvo(HOST, PORT)


# helper function for UDP file transfer
def clientUDPfile(HOST, PORT, FILE):
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create connection
    buf = []  # data buffer for file
    f = FILE.read(200)
    while (f):  # read contents of file into buffer
        buf.append(f)
        f = FILE.read(200)

    for item in buf:  # send all data in buffer to server, with a dummy ack
        cli.sendto(item + "0", ((HOST, PORT)))

    FILE.close()
    cli.sendto("2", ((HOST, PORT)))  # send termination notice
    cli.close()  # exit
    sys.exit()


# client for UDP echo, handles user input and connections to UDP server
def clientUDPconvo(HOST, PORT):
    # create UDP socket, no need to create a connection since UDP
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # try-catch for errors in transmission, while loop for input
    while True:
        try:
            # functions exactly the same as clientTCP, except data is sent to an address rather than an active connection
            send = str(raw_input())
            while (len(send) == 0):
                send = str(raw_input("Input must not be empty!\n"))
            cli.sendto(send, ((HOST, PORT)))
            data, serv = cli.recvfrom(255)
            print(data)
        except(socket.error):
            print("Connection has been closed by server. Goodbye.")
            break
