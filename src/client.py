'''
Created on Jan 30, 2016

@author: Quinn
'''
#import socket

from socket import *

serverPort = 12333
serverAddress = 'localhost'

clientSocket = socket(AF_INET, SOCK_STREAM)
print 'Bound to: (after socket call)', clientSocket.getsockname
#print clientSocket.getsockname

sentence = raw_input('Input lowercase sentence:')
clientSocket.send(sentence)

modifiedSentence = clientSocket.recv(1024)
print 'From Server:', modifiedSentence

sentence = raw_input('enter to finish')

clientSocket.close()
