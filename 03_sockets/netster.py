#!/usr/bin/env python3

#**************************************************************
#* netster.py - Ethan Anderson (etmander)
#* UPDATED: 11/25/2019
#**************************************************************
import argparse
import logging as log

# Import the assignment modules.
# These imports can be specialized as necessary.
from a2 import *

#set defaults for ease of use in future statements
DEFAULT_PORT = 12345
DEFAULT_HOST = "127.0.0.1"

def main():
    parser = argparse.ArgumentParser(description="SICE Network netster")
    parser.add_argument('-p', '--port', type=str, default=DEFAULT_PORT,
                        help='listen on/connect to port <port> (default={}'
                        .format(DEFAULT_PORT))
    parser.add_argument('-ip', '--address', type=str, default=DEFAULT_HOST,
                        help='listen on/connect to ip <ip> (default={}'
                        .format(DEFAULT_HOST))  # Add argument for setting connection destination
    parser.add_argument('-i', '--iface', type=str, default='0.0.0.0',
                        help='listen on interface <dev>')
    parser.add_argument('-f', '--file', type=str,
                        help='file to read/write')
    parser.add_argument('-u', '--udp', action='store_true',
                        help='use UDP (default TCP)')
    parser.add_argument('-r', '--rudp', type=int, default=0,
                        help='use RUDP (1=stopwait, 2=gobackN)')
    parser.add_argument('-m', '--mcast', type=str, default='226.0.0.1',
                        help='use multicast with specified group address')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Produce verbose output')
    parser.add_argument('host', metavar='host', type=str, nargs='?',
                        help='connect to server at <host>')

    args = parser.parse_args()

    # configure logging level based on verbose arg
    level = log.DEBUG if args.verbose else log.INFO

    f = None
    # open the file if specified
    if args.file:
        try:
            mode = "wb" if args.host else "rb"  # set appropriate flags for reading
            f = open(args.file, mode)
        except Exception as e:
            print("Could not open file: {}".format(e))
            exit(1)

    # Here we determine if we are a client or a server depending
    # on the presence of a "host" argument.
    if args.host:
	#check if we are starting a udp server, or RUDP server. else start TCP server
        if args.udp:
            print("Host UDP")
            log.basicConfig(format='%(levelname)s:client: %(message)s',
                            level=level)
            serverUDP(args.address, int(args.port), f)
        elif args.rudp:
            print("Host RUDP")
            log.basicConfig(format='%(levelname)s:client: %(message)s',
                            level=level)
            serverRUDP(args.address, int(args.port), args.rudp, f)
        else:
            print(args.host)
            log.basicConfig(format='%(levelname)s:client: %(message)s',
                            level=level)
            serverTCP(args.address, int(args.port), f)
    else:
	#check if udp client, or RUDP client. else start a tcp client
        if args.udp:
            log.basicConfig(format='%(levelname)s:server: %(message)s',
                            level=level)
            print("client UDP")
            clientUDP(args.address, int(args.port), f)
        elif args.rudp == 1 or args.rudp == 2:
            log.basicConfig(format='%(levelname)s:server: %(message)s',
                            level=level)
            print("client RUDP")
            clientRUDP(args.address, int(args.port), args.rudp, f)
        else:
            log.basicConfig(format='%(levelname)s:server: %(message)s',
                            level=level)
            print("client")
            clientTCP(args.address, int(args.port), f)

    if args.file:
        f.close()


if __name__ == "__main__":
    main()
