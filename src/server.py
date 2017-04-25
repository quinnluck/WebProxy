'''
Created on Jan 30, 2016
Finished 2/21, 2016

@author: Quinn Luck
For CS 4150
PA-1
'''

import socket
import os
import select
import sys
import hashlib
import re
import errno
import urllib2
import subprocess

flag = False
serverAddress = 'localhost'

while flag == False:
    # Gets a socket number as input from the command line
    socketNum = raw_input('Enter a socket number:')
    try:
        serverPort = int(socketNum)
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'Got a socket: ', serverSocket.fileno()
        serverSocket.bind((serverAddress,serverPort))
        print 'Bound to: ', serverSocket.getsockname()
        flag = True
    except:
        print 'Invalid socket number!  Please enter a NUMBER'

serverSocket.listen(3)
input = [serverSocket]

while 1:
    
    inputready, outputready, exceptready = select.select(input, [], [])
    print 'Listening for requests'
    
    for s in inputready:
        # handles multiple sockets at the same time.
        if s == serverSocket:
            print 'Handling server socket'
            connectionSocket, addr = serverSocket.accept()
            print 'Accepted connection from: ', connectionSocket.getpeername(), ' fd: ', connectionSocket.fileno()
            input.append(connectionSocket)   
        else:
            print 'Handling client socket for: ', s.getpeername()
            
            # here is where we receive input from our connected socket.  We stop receiving when 2 enters are
            # sent over our connection, one right after another.
            sentence = ''
            continuerecv = True
            while continuerecv == True:
                try:
                    sentence += s.recv(1024)
                    print 'Got: ', sentence
                    oneEnter = re.search('\r\n', sentence)
                    if oneEnter:
                        # If we're given a relative URL, we know there will be an enter before the Host: line. grab it.
                        content = re.findall('/(?:[a-zA-Z]|[0-9]|[$-_@.&+~]|[!*\(\),]|(?:%[0-9a-zA-Z][0-9a-zA-Z]))+', sentence)
                    # Looks for a double return which means we're done with our URL input    
                    match = re.search('\r\n\r\n', sentence)
                    if match:
                        continuerecv = False
                except socket.error, e:
                        print 'Error: ' , e
                        continue_recv = False
            
            # We get the input in the form of a string, then parse the string looking for information
            # URL, HTTP version, Request Method.
            print 'Got: ', sentence
            urlMethod = sentence[:3]
            http = re.findall('HTTP/(?:[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9]))+', sentence)
            url = re.findall('http://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', sentence)
            print 'content: ', content       
            print 'method: ', urlMethod
            print 'http version: ', http
            print 'url: ', url
            if urlMethod == 'GET':
                # tries a request using an absolute URL from input
                absoluteFlag = False
                try:
                    request = 'http:' + content[0]
                    response = urllib2.urlopen(request)
                    print 'CODE: ', response.getcode()
                    absoluteFlag = True
                    print 'URL: ', response.geturl()
                    print 'INFO: ', response.info()
                    print '-----------------------'
                    
                except:
                    # If errors were thrown, it might be a Relative URL that was input
                    {}
                # tries a request using a relative URL from input
                if absoluteFlag == False:
                    try:
                        request = url[0] + content[0]
                        response = urllib2.urlopen(request)
                        print 'CODE: ', response.getcode()
                        print 'URL: ', response.geturl()
                        print 'INFO: ', response.info()
                        print '-----------------------'
                    except:
                        s.send('ERROR 004: bad URL, connection failed.')
                    
                try:
                    # here is where we hash the file from our response, then check it against the Team Cymru database
                    response = response.read().split('\r\n\r\n')
                    print 'response: ', response
                    
                    hashedFile = hashlib.md5(response[0]).hexdigest()
                    print 'hashedFile: ', hashedFile
                    # run a command through a shell and get the output from it.
                    command = 'whois -h hash.cymru.com ' + hashedFile + '\n'
                    print 'command: ', command
                    malResponse = subprocess.check_output(command, shell=True)
                    print 'malResponse: ', malResponse
                    
                    # check to see if there is no data on the file, if not we know its malware free!
                    cymruCheck = re.search('NO_DATA', malResponse)
                    print 'cymruCheck: ', cymruCheck
                    if cymruCheck:
                        s.send(response[0])
                    else:
                        # If malware is detected, dont send the payload, send our replacement
                        replaceHtml = '<!DOCTYPE html>\n<html>\n<body>\n\n<h1>Content was blocked because it is suspected of containing malware.</h1>\n\n</body>\n</html>\n\n'
                        s.send(replaceHtml)
                    
                except:
                    s.send('ERROR 502: Bad Gateway, connection failed.')
                    s.close()
                    input.remove(s)
            else:
                # This is for anything other than a GET request.
                print 'ERROR 501: Not Implemented'
                s.close()
                input.remove(s)
            print 'Done with this socket:'

