#**************************************************************
#* a2.py - Ethan Anderson (etmander)
#* CREATED: 10/17/2019
#* 
#**************************************************************
import socket
import sys

#Server TCP acts as the server for the echo client via the TCP protocol. Reccs data from client and handles it on a case basis
def serverTCP(HOST, PORT):
    #create the socket, bind it to our host IP and port number
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    #listen for any connection attempts, and accept them
    server.listen(10)
    conn, addr = server.accept()

    #loop for input
    while True:
	#rec our data and store it (255 bytes)
        data = conn.recv(255)
	#print out data server side for analysis
        print(data)
	#if 'hello', reply 'world'
        if (data == "hello"):
            conn.send("world\n")
	#if 'goodbye', send 'farewell', shutdown and end the active connection, and listen for new attempts to accept
        elif (data == "goodbye"):
            conn.send("farewell\n")
            conn.shutdown(2)
            conn.close()
            print("closed looking for connections\n")
            server.listen(10)
            conn, addr = server.accept()
            print("new connection detected\n")
	#if 'exit', shutdown program with sys call
        elif (data == "exit"):
            conn.send("ok\n")
            sys.exit(0)
	#else, reply with the rec'd data
        else:
            data = data + "\n"
            conn.send(data)

#Client portion of the TCP echo, handles inpt and sending to server
def clientTCP(HOST, PORT):
    #create the cokcet, and attempt to connect to the host IP and port #
    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli.connect((HOST, PORT))
    #loop for input
    while True:
        #try-catch statement to catch any disconnections from server to prevent errors.
        try:
	    #capture input
            send = str(raw_input())
	    #do not permit blank input, for sanity's sake
            while (len(send) == 0):
                send = str(raw_input("Input must not be empty!\n"))
	    #send input to server
            cli.send(send)
	    #rec response from server and print (255 bytes)
            data = cli.recv(255)
            print(data)
        #catch disconnections and handle
        except(socket.error):
            print("Connection has been closed by server. Goodbye.")
            break

#server function for UDP echo, handles connections and recc data and creates an appropriate response
def serverUDP(HOST, PORT):
    #create the UDP socket, and bind it to our host IP and port #
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    #loop for input
    while True:
	#get data from a UDP client (255 bytes), store its appropriate information
        data, addr = server.recvfrom(255)
	#print data server side
        print(data)
 	#if/then statement functions exact same as serverTCP, except in noted areas
        if (data == "hello"):
            #send response to stored address, instead of an active connection
            server.sendto("world\n", addr)
        elif (data == "goodbye"):
            server.sendto("farewell\n", addr)
	    #close the current session
            server.close()
            print("Closed, looking for new connections\n")
	    #restart the socket and look for new UDP connections
            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.bind((HOST, PORT))
        elif (data == "exit"):
            server.sendto("ok\n", addr)
            sys.exit(0)
        else:
            data = data + "\n"
            server.sendto(data, addr)

#client for UDP echo, handles user input and connections to UDP server
def clientUDP(HOST, PORT):
    #create UDP socket, no need to create a connection since UDP
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #try-catch for errors in transmission, while loop for input
    while True:
        try:
	    #functions exactly the same as clientTCP, except data is sent to an address rather than an active connection
            send = str(raw_input())
            while (len(send) == 0):
                send = str(raw_input("Input must not be empty!\n"))
            cli.sendto(send, ((HOST, PORT)))
            data, serv = cli.recvfrom(255)
            print(data)
        except(socket.error):
            print("Connection has been closed by server. Goodbye.")
            break

