#!/usr/bin/env python3

#**************************************************************
#* smtp.py - Ethan Anderson (etmander)
#* CREATED: 12/11/19
#* 
#* Sends email via SMTP
#* Takes args mail_server, from_addr, to_addr, message, subject, and priority
#**************************************************************

import os
import time
import smtplib
import email
import argparse

# Entry function for sending mail via SMTP.  The input arguments allow you to
# contruct a well-formed email message and send it a specific server.
def send_mail(server, faddr, taddr, msg):
    #print message contents
    print (server, faddr, taddr, msg)
    #connect to smtp server
    smtp = smtplib.SMTP(server, 25)
    #send the email
    smtp.sendmail(faddr, taddr, msg.as_string())
    #disconnect from smtp server and exit
    smtp.quit()
    exit(0)

def main():
    #arguments, include args for headers such as subject and message priority
    parser = argparse.ArgumentParser(description="SICE Network SMTP Client")
    parser.add_argument('mail_server', type=str,
                        help='Server hostname or IP')
    parser.add_argument('from_address', type=str,
                        help='My email address')
    parser.add_argument('to_address', type=str,
                        help='Receiver address')
    parser.add_argument('message', type=str,
                        help='Message text to send')
    parser.add_argument('subject', type=str,
                        help='Message subject')
    parser.add_argument('priority', type=str, default=5,
                        help='Integer ranging from 1 to 5, 1 being the highest and 5 being the lowest')
    
    args = parser.parse_args()

    #create message object
    m = email.message.EmailMessage()
    #set message headers from args
    m['From'] = args.from_address
    m['To'] = args.to_address
    m['X-Priority'] = args.priority
    m['Subject'] = args.subject
    m.set_payload(args.message)
    #go to helper function
    send_mail(args.mail_server, args.from_address,
              args.to_address, m)
    
if __name__ == "__main__":
    main()
    
