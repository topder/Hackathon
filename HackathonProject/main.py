import threading

from Server import Server
from Client import Client


s = Server()
c = Client("AA")
server_thread = threading.Thread(target=s.udp_broadcast_thread).start()
client_thread = threading.Thread(target=c.receive_message).start()
#func1.result()
#func2.result()