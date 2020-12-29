import socket
import threading
import time
#import getch


class Client():
    def __init__(self, name):
        self.clientIP = "127.0.0.1"
        self.clientPort = 13117
        self.bufferSize = 2048
        self.serverIP=""
        self.severPort=""
        self.connected=False
        self.name=name
        self.stop_game=False

    def receive_message(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # UDP
        try:
            client.bind(("", self.clientPort))
        except:
            pass
        print("Client started, listening for offer requests...")
        while not self.connected:
            data, addr = client.recvfrom(self.bufferSize)
            self.serverIP=addr[0]
            print("Received offer from: "+str(addr[0])+ " ,attempting to connect... ")
            received=data.hex()
            if received[:8]=='feedbeef' and received[8:10]=='02':
                #int.from_bytes(b'\xfc\x00', byteorder='big', signed=False)
                self.severPort=int(received[10:],16)
                self.connected=True
                self.ConnectingToAServer()

    def ConnectingToAServer(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.serverIP, self.severPort))
        client.send(bytes(self.name+'\n','UTF-8'))
        data = client.recv(self.bufferSize)
        print(data.decode('UTF-8'))
        thread_listener=threading.Thread(target=self.tcp_listener,args=(client,)).start()
        thread_game = threading.Thread(target=self.GameMode,args=(client,)).start()


    def tcp_listener(self,client):
        while True:
            data = client.recv(self.bufferSize)
            data=data.decode('UTF-8')
            print(data)
            if data == 'Game over!':
                self.stop_game=True
                data = client.recv(self.bufferSize)
                data=data.decode('UTF-8')
                print(data)
                client.close()
                print("Server disconnected, listening for offer requests...")
                break

    def GameMode(self,client):
        while not self.stop_game:
            char = getch.getch()
            client.send(bytes(char,'UTF-8'))


