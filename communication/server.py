import socket
import pickle

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.2.97', 1024))
serialized_data = client.recv(1024)

received_data = pickle.loads(serialized_data)

print('Received Data: ', received_data)
client.close()