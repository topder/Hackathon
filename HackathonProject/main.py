import threading
from Server import Server
from Client import Client

s=Server()
server_thread = threading.Thread(target=s.startServer).start()
c = Client()
client_thread = threading.Thread(target=c.startClient).start()
