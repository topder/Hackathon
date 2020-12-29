import threading
from Server import Server
from Client import Client

s=Server()
s.startServer()
c = Client("AA")
client_thread = threading.Thread(target=c.receive_message).start()

