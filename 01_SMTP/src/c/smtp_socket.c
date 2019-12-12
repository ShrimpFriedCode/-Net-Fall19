//*************************************************************
//  smtp_socket.c - Ethan Anderson (etmander)
//  CREATED: 12/11/19
//
//  Connect to smtp mail server using c sockets
//  takes args server, from_addr, to_addr, and message
//  Does not actually send email, just connects to server via socket
//**************************************************************

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>

typedef struct cfg {
    char *server;
    char *from_address;
    char *to_address;
    char *message;
} cfg_t;

/*
 * Entry function for sending mail via SMTP.
 * The input argument is a configuration structure
 * with the necessary data to form an email message
 * and send it to a specific server.
*/
void send_mail(cfg_t *cfg) {
    printf("Arguments: %s %s %s %s\n", cfg->server,
           cfg->from_address, cfg->to_address, cfg->message);
}

int main(int argc, char **argv) {
    //initialize vars and socket data buffer
    int c, s;
    char buf[255];
    //malloc onjects for results, result parser, hints, and server for ntoa functionality
    struct sockaddr_in *server = malloc(sizeof(struct sockaddr_in));   
    struct addrinfo *r = malloc(sizeof(struct addrinfo));
    struct addrinfo *res = malloc(sizeof(struct addrinfo));
    struct addrinfo *hints = malloc(sizeof(struct addrinfo));
    //set hints accordingly
    hints->ai_flags = NULL;
    hints->ai_family = AF_UNSPEC;
    hints->ai_socktype = 0;
    hints->ai_protocol = 0;
    //parse args
    cfg_t cfg = {
            .server = NULL,
            .from_address = NULL,
            .to_address = NULL,
            .message = NULL
    };

    if (argc < 5) {
        fprintf(stderr,
                "Usage: %s <server> <from> <to> <message>\n",
                argv[0]);
        exit(1);
    }

    cfg.server = strdup(argv[1]);
    cfg.from_address = strdup(argv[2]);
    cfg.to_address = strdup(argv[3]);
    cfg.message = strdup(argv[4]);
    //if we cannot getaddrinfo on supplied server, exit with error
    if((c = getaddrinfo(cfg.server, "25", hints, &res)) != 0)
	exit(1);
    //iterate through returned address objects from getaddr   
    for (r = res; r != NULL; r = r->ai_next) {
	//add current addr to sockaddr object
        server=r->ai_addr;
	//print address
	printf("IP is %s\n", inet_ntoa(server->sin_addr));
	//initialize sockey with hints
	s = socket(r->ai_family, r->ai_socktype, r->ai_protocol);
	//if failed to initialize, return to top of loop
	if(s == -1)
		continue;
	//attempt to create connection, and exit loop if successful
	if(connect(s, r->ai_addr, r->ai_addrlen) != -1)
		break;
	//close socket for reattempt
	close(s);
    }
    //if we ran out of addresses to try, exit with error
    if(r == NULL) {
	fprintf(stderr, "\nCould not connect\n");
	exit(1);
    }

    //get data from socket connection, print, then close the connection and exit prog.
    recv(s, buf, 255, 0);
    printf("%s", buf);
    close(s); 

    //no need to run mail function, since it is remainder skeletion code
    //send_mail(&cfg);

    return 0;
}
