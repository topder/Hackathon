import threading
import time
from socket import *
from threading import  Lock
from struct import *
#UDP server
class Server():
    def __init__(self):
        self.serverIP = "192.168.80.1"
        self.serverPort = 12345
        self.bufferSize = 2048
        self.group_number=1
        self.all_teams={}
        self.results={}
        self.mutex=Lock()


    def udp_broadcast_thread(self):
        broadcast_thread=threading.Thread(target=self.udp_broadcast)
        broadcast_thread.start()

    def tcp_thread(self):
        tcp_thread=threading.Thread(target=self.tcp_listener)
        tcp_thread.start()

    def udp_broadcast(self):
        start_time =time.time()
        UDPServerSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        UDPServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        #TODO......
        UDPServerSocket.settimeout(0.2)
        message= bytes.fromhex("feedbeef")
        message+= bytes.fromhex("02")
        message+=self.serverPort.to_bytes(2,byteorder='big')
        print("Server started,listening on IP address 172.1.0.4\n")
        while True:
            end_time=time.time()
            if end_time-start_time<=10:
                UDPServerSocket.sendto(message, ('<broadcast>',13117))
                time.sleep(1)
            else:
                UDPServerSocket.close()
                break

    def tcp_listener(self):
        TCPServerSocket = socket(AF_INET,SOCK_STREAM)
        TCPServerSocket.bind((self.serverIP, self.serverPort))
        # TODO 10 seconds after the server was starte?
        #TODO 5?
        TCPServerSocket.listen(4)
        TCPServerSocket.settimeout(10)
        try:
            while True:
                connection, address = TCPServerSocket.accept()
                #self.all_teams[address]=connection
                self.all_teams[connection] =["",0,0]
                threading.Thread(target = self.listenToClient,args = (connection,address)).start()
        except:
            print("time out")
        self.startGame()


    def listenToClient(self, connection, address):
        while True:
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
                    break
                else:
                    raise error('Client disconnected')
            except:
                connection.close()

    def startGame(self):
        list_thread=[]
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
            t=threading.Thread(target=self.runGame,args=(connection,message,))
            list_thread.append(t)
            t.start()
        for t in list_thread:
            t.join()
        for connection in self.all_teams.keys():
             threading.Thread(target=self.resultsGame,args=(connection,)).start()

    def startServer(self):
        threading.Thread(target=self.tcp_thread).start()
        threading.Thread(target=self.udp_broadcast_thread).start()

    def runGame(self,connection,message):
        connection.send(bytes(message, 'UTF-8'))
        start_time = time.time()
        while True:
            new_time = time.time()
            if new_time-start_time>=10:
                    connection.send(bytes("Game over!", 'UTF-8'))
                    break
            else:
                connection.settimeout(10)
                try:
                    data = connection.recv(self.bufferSize)
                    if data:
                        self.all_teams[connection][2]+=1
                except:
                    print("time out")

    def resultsGame(self,connection):
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
        message="Group 1 typed in "+ str(max_g1)+ " characters. Group 2 typed in " + str(max_g1)+" characters.\n"
        if winner==0:
            message+="It's a tie! Everybody wins!!\n"
        else:
            message+="Group "+str(winner)+" wins!\n"
            message+="Congratulations to the winners:\n ==\n"
            for val in self.all_teams.values():
                if val[1]==winner:
                    message+=val[0]+'\n'

        connection.send(bytes(message, 'UTF-8'))
        connection.close()
        print("Game over, sending out offer requests...")

