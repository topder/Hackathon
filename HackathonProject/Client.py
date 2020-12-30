import socket
import threading
import time
import getch
from _thread import *

import sys
import select
import tty
import termios


class Client():
    def __init__(self):
        self.clientPort = 13119
        self.bufferSize = 2048
        self.serverIP = ""
        self.serverPort = ""
        self.connected = False
        self.name = "AA"
        self.stop_game = False
        self.clientSocket = None

    def receive_message(self):
        while True:
            client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client.bind(("", self.clientPort))
            try:
                data, addr = client.recvfrom(self.bufferSize)
            except:
                pass
            client.close()
            received = data.hex()
            if received[:8] == 'feedbeef' and received[8:10] == '02':
                self.serverIP = addr[0]
                self.serverPort = int(received[10:], 16)
                self.ConnectingToAServer()
                break
            else:
                print("")

    def ConnectingToAServer(self):
        print("Received offer from: " + str(self.serverIP) + " ,attempting to connect... ")
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.clientSocket.connect((self.serverIP,int(self.serverPort)))
            self.clientSocket.send(self.name.encode('utf-8'))
            data = self.clientSocket.recv(self.bufferSize)
            print(data.decode('UTF-8'))
            self.GameMode(self.clientSocket)
            self.End_Game(self.clientSocket)
        except:
            print("")

    def End_Game(self, client):
        data = client.recv(self.bufferSize)
        data = data.decode('UTF-8')
        print(data)
        print("Server disconnected, listening for offer requests...")



    def isData(self):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def GameMode(self, client):
        start_time=time.time()
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while True:
                if time.time()-start_time<=10:
                    if self.isData():
                        char = sys.stdin.read(1)
                        client.send(char.encode('utf-8'))
                else:
                    break
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


    def startClient(self):
        while True:
            print("Client started, listening for offer requests...")
            self.receive_message()


c=Client()
c.startClient()



