import socket
import pickle

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('192.168.2.97'), 1024)
server.listen(1)
print('Server Listening...')
conn, addr = server.accept()
print('Connection from: ', addr)
data = {'key', 'value'}
serialized_data = pickle.dumps(data)
conn.send(serialized_data)
conn.close()
