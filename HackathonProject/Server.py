
import time
from socket import *
import threading
from struct import *
#UDP server
class Server():
    def __init__(self):
        self.serverIP = "127.0.0.1"
        self.serverPort = 20001
        self.bufferSize = 1024
        self.group1={}
        self.group2={}
        self.group_number=1
        self.all_teams={}

    def udp_broadcast_thread(self):
        broadcast_thread=threading.Thread(target=self.udp_broadcast)
        broadcast_thread.start()

    # def tcp_thread(self):
    #     tcp_thread=threading.Thread(target=self.)
    #     tcp_thread.start()

    def udp_broadcast(self):
        UDPServerSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        #UDPServerSocket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        UDPServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        #TODO......
        UDPServerSocket.settimeout(0.2)

        message= bytes.fromhex("feedbeef")
        message+= bytes.fromhex("02")
        message+=self.serverPort.to_bytes(2,byteorder='big')
        print("Server started,listening on IP address 172.1.0.4 ")
        while True:
            UDPServerSocket.sendto(message, ('<broadcast>',13117))
            time.sleep(1)

    def tcp_listener(self):
        TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPServerSocket.bind((self.serverIP, self.serverPort))
        # TODO 10 seconds after the server was starte?
        #TODO 5?
        TCPServerSocket.listen(5)
        while True:
            connection, address = TCPServerSocket.accept()
            #self.all_teams[address]=connection
            self.all_teams[connection.fileno()] = connection
            #TODO: settimeout(60)?
            #connection.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (connection,address)).start()


    def listenToClient(self, connection, address):
        while True:
            try:
                data = connection.recv(self.bufferSize)
                if data:
                    # Set the response to echo back the recieved data
                    if self.group_number%2==0:
                      self.group1[address]=data.strip()
                    else:
                        self.group2[address]=data.strip()
                    self.group_number+=1
                else:
                    raise error('Client disconnected')
            except:
                connection.close()
                return False

    def startGame(self):
        message="Welcome to Keyboard Spamming Battle Royale./n "
        message+="Group 1:/n==/n "
        for val in self.group1.values():
            message+=val+'/n'
        message+="Group 2:/n==/n"
        for val in self.group2.values():
            message+=val+'/n/n'
        message='Start pressing keys on your keyboard as fast as you can!!/n'
        for connection in self.all_teams.values():
            connection.sendall(bytes(message,'UTF-8'))





