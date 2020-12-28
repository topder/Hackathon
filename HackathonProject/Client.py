import socket
import threading


class Client():
    def __init__(self, name):
        self.clientIP = "127.0.0.1"
        self.clientPort = 13117
        self.bufferSize = 1024
        self.serverIP=""
        self.severPort=""
        self.connected=False
        self.name=name
        self.stop_game=False

    def receive_message(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        client.bind(("", self.clientPort))
        print("Client started, listening for offer requests...")
        while not self.connected:
            data, addr = client.recvfrom(self.bufferSize)
            self.serverIP=addr[0]
            print("Received offer from: "+str(addr)+ " ,attempting to connect... ")
            received=data.hex()
            if received[:8]=='feedbeef' and received[8:10]=='02':
                #int.from_bytes(b'\xfc\x00', byteorder='big', signed=False)
                self.severPort=int(received[10:],16)
                self.connected=True
                self.ConnectingToAServer()

    def ConnectingToAServer(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self.serverIP)
        print(self.severPort)
        client.connect((self.serverIP, self.severPort))
        client.sendall(bytes(self.name+'/n','UTP-8'))
        data = client.recv(self.bufferSize)
        print(data)
        thread_listener=threading.Thread(target=self.tcp_listener,args=(client,)).start()
        thread_game = threading.Thread(target=self.GameMode, args=(lambda: self.stop_game,)).start()

    #client.close()

    def tcp_listener(self,client):
        while True:
            data = client.recv(self.bufferSize)
            if data == 'Game over!':
                self.stop_game=True
                break

    def GameMode(self):
        pass
