import threading
import time
from _thread import start_new_thread
from socket import *
from struct import *
from scapy.all import get_if_addr

#UDP server
class Server():
    def __init__(self,serverPort,udp_port):
        self.serverIP= get_if_addr("eth1")
        self.serverPort = serverPort
        self.UdpPort=udp_port
        self.Game=False
        self.bufferSize = 2048
        self.group_number=0
        self.all_teams={}

    def udp_broadcast(self):
        """
        Creating a udp socket and sending offers message for Cliens.
        The offer message contains: Magic cookie,Message type and Server port
        """
        UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
        UDPServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        message= bytes.fromhex("feedbeef")
        message+= bytes.fromhex("02")
        message+=self.serverPort.to_bytes(2,byteorder='big')
        threading.Timer(1.0, self.udp_broadcast).start() # every second we create the a new message
        UDPServerSocket.sendto(message, ('<broadcast>',self.UdpPort)) # send the message
        print("Server started,listening on IP address "+str(self.serverIP)+"\n")

    def create_Socket_TCP(self):
        """
        Responsible for managing communications from the Server side:
        Creating a TCP socket and accept the Client requests.
        After a request is received calls the function that start the game
        """
        self.Game=True
        self.group_number=0
        self.all_teams={}
        TCPServerSocket = socket(AF_INET,SOCK_STREAM)
        TCPServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        TCPServerSocket.settimeout(10)
        TCPServerSocket.bind(('', self.serverPort))
        TCPServerSocket.listen(1)
        while True:
            try:
                connection, address = TCPServerSocket.accept()
                self.all_teams[connection] =["",0,0]
                start_new_thread(self.get_client_name, (connection,))# Calling to the function that responsible for receiving new cliens
            except:
                break
        self.start_game(TCPServerSocket)


    def get_client_name(self, connection):
        """
        Receiving the clients names and dividing them into groups at random
        (each client is treated separately)
        :param connection socket :
        :return:
        """
        try:
            data = connection.recv(self.bufferSize)
            if data:
                if self.group_number%2==0:
                  self.all_teams[connection][0]=data.decode('UTF-8')
                  self.all_teams[connection][1]=1
                else:
                    self.all_teams[connection][0]=data.decode('UTF-8')
                    self.all_teams[connection][1] =2
                self.group_number+=1
            else:
                raise error('Client disconnected')
        except:
            pass


    def start_game(self,TCPServerSocket):
        """
        Responsible for managing the game:
        creating a start game message
        Calling to the function that responsible for running the game
        Calling to the function that responsible for ending the game
        :param TCP Server Socket:
        :return:
        """
        message="Welcome to Keyboard Spamming Battle Royale.\n "
        message+="Group 1:\n==\n "
        for val in self.all_teams.values():
            if val[1]==1:
                message+=val[0]+'\n'
        message+="Group 2:\n==\n"
        for val in self.all_teams.values():
            if val[1] == 2:
                message+=str(val[0])+'\n\n'
        message+='Start pressing keys on your keyboard as fast as you can!!\n'
        for connection in self.all_teams.keys():
            start_new_thread(self.run_game, (connection,message,)) # Calling to the function that responsible for running the game with threads
        time.sleep(10)
        self.Game=False
        for connection in self.all_teams.keys():
            self.resultsGame(connection)
            connection.shutdown(SHUT_RDWR)
            connection.close()
        TCPServerSocket.shutdown(SHUT_RDWR)
        TCPServerSocket.close()
        print("Game over, sending out offer requests...")

    def run_game(self,connection,message):
        """
        sending the start game message for a client
        Gets the client last typing and add it
        :param connection socket :
        :param message:
        """
        connection.send(message.encode('utf-8'))
        while self.Game:
            try:
                data = connection.recv(self.bufferSize)
                if data:
                    self.all_teams[connection][2]+=1
            except:
                connection.send("Game Over!".encode('utf-8'))
                break

    def resultsGame(self,connection):
        """
        Calculates the results of the game and sends it to the client
        :param connection socket :
        :return:
        """
        max_g1=0
        max_g2=0
        winner=0
        for val in self.all_teams.values():
            if val[1]==1:
                max_g1+=val[2]
            else:
                max_g2+=val[2]
        if max_g2>max_g1:
            winner=2
        elif max_g1>max_g2:
            winner=1
        message="Group 1 typed in "+ str(max_g1)+ " characters. Group 2 typed in " + str(max_g2)+" characters.\n"
        if winner==0:
            message+="It's a tie! Everybody wins!!\n"
        else:
            message+="Group "+str(winner)+" wins!\n"
            message+="Congratulations to the winners:\n ==\n"
            for val in self.all_teams.values():
                if val[1]==winner:
                    message+=val[0]+'\n'
        connection.send(message.encode('utf-8'))

    def run_server(self):
        """
         Responsible for the run of the Server
         :return:
         """
        while True:
            self.udp_broadcast()
            self.create_Socket_TCP()


s=Server(2056,13117)
s.run_server()

