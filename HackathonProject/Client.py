from socket import*
#TCP
from socket import *
serverName = ""
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = raw_input()
clientSocket.send(sentence)
modifiedSentence = clientSocket.recv(1024)
print ()
clientSocket.close()

#UDPClient
serverName = ""
serverPort = 12000
clientSocket = socket(socket.AF_INET,socket.SOCK_DGRAM)
message = raw_input()
clientSocket.sendto(message,(serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage)
clientSocket.close()
