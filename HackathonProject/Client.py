import socket
import threading
import time
import getch
from _thread import *

import sys
import select
import tty
import termios

class color:
    Red = '\u001b[31;1m'
    RESET = '\033[0m'



class Client():
    def __init__(self,team_name, client_port):
        self.clientPort = client_port
        self.bufferSize = 2048
        self.serverIP = ""
        self.serverPort = ""
        self.name = team_name
        self.stop_game = False
        self.clientSocket = None

    def receive_message(self):
        """
        Creating a udp socket and waiting for server broadcast message.
        Checks whether the received message is in the correct format.
        """
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
        """
        Responsible for managing communications from the client side:
        Creating a TCP socket and Trying to connect to the server.
        If the connection is successful, the client sends a message containing his name
        There is a call to a function that starts the game and at the end of the game there is a call to a function that ends the game
        """
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
        """
        Gets the results of the game and prints them
        :param client socket :
        """
        data = client.recv(self.bufferSize)
        data = data.decode('UTF-8')
        print(data)
        print("Server disconnected, listening for offer requests...")


    def isData(self):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def GameMode(self, client):
        """
        The course of the game:
        After each press on the keyboard a message is sent to the server.
        :param client socket :
        :return:
        """
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
        """
        Responsible for the run of the Client
        :return:
        """
        while True:
            print(f"{color.Red}Client started, listening for offer requests...{color.RESET}")
            self.receive_message()


c=Client("AA",13117)
c.startClient()



