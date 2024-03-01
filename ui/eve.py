import socket
import pickle
from numpy.random import randint
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import threading
import selectors


def measure_message(message, bases):
    # Creates simulator
    simulator = AerSimulator(method='statevector')
    # measurement array and number of qubits created
    measurements = []
    n = len(message)
    for q in range(n):
        # If the base is 0, measure in the Z-basis
        if bases[q] == 'X':
            message[q].measure(0,0)
            # If the base is 1, measure in the X-basis
        if bases[q] == 'H':
            # Applies a Hadamard gate to the qubit to change the basis to the Z-basis
            message[q].h(0)
            message[q].measure(0,0)
        # Runs simulation of the  quantum circuit
        results = simulator.run(message[q], shots=10, memory=True).result()
        # Gets the results from the simulation and converts it to an integer
        measured_bit = int(results.get_memory()[0])
        # Adds measured bit to measurement array
        measurements.append(measured_bit) 
    return measurements, message


def accept_alice(sock, mask, listening):
    conn, addr = sock.accept()  # Should be ready
    conn.setblocking(False)
    print("Connected to Alice", conn, "from", addr)
    sel.register(conn, selectors.EVENT_READ, process_data_alice)

def accept_bob(sock, mask, listening):
    conn, addr = sock.accept()  # Should be ready
    conn.setblocking(False)
    print("Connected to Bob", conn, "from", addr)
    sel.register(conn, selectors.EVENT_READ, process_data_bob)

def socket_send(data, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(20)
    s.connect(('localhost', port))
    s.sendall(pickle.dumps(data))
    s.close()

def process_data_bob(conn, mask, listen=0):
    raw_data = []
    try:
        while True:
            d = conn.recv(1024)
            if not d:
                break
            raw_data.append(d)
        if raw_data  == []:
            # sel.unregister(conn)
            # conn.close()
            return
        data = pickle.loads(b"".join(raw_data))
        if data['type'] == 'bases':
            print("Received bases")
            print(''.join(str(i) for i in data['bases']))
            socket_send(data, alice_port)
        elif data['type'] == 'string':
            print("Received encrypted string")
            print(data['cypher_text'])
            socket_send(data, alice_port)
        elif data['type'] == 'key':
            print("Received key")
            print(data['key'])
            socket_send(data, alice_port)
        elif data['type'] == ' file':
            print("Received file")
            print(data['file'])
            socket_send(data, alice_port)
        
    except KeyboardInterrupt:
        print("Exiting...")
        return

def process_data_alice(conn, mask, listening=0):
    raw_data = []
    try:
        while True:
            d = conn.recv(1024)
            if not d:
                break
            raw_data.append(d)
        if raw_data  == []:
            # sel.unregister(conn)
            # conn.close()
            return
        data = pickle.loads(b"".join(raw_data))
        if data["type"] == 'qc':
            print("Received quantum circuit from Alice")
            qc = data['circuit']
            if listening: 
                eve_bases = ['X' if randint(0, 2) else 'H' for i in range(len(qc))]
                measurements, qc = measure_message(qc, eve_bases)
                data['qc'] = qc
                print(measurements)
            print('Sending circuit to bob')
            socket_send(data, bob_port)
            print('Sent, waiting for bases')
        elif data['type'] == 'bases':
            print("Received bases")
            print(''.join(str(i) for i in data['bases']))
            socket_send(data, bob_port)
        elif data['type'] == 'string':
            print("Received encrypted string")
            print(data['cypher_text'])
            socket_send(data, bob_port)
        elif data['type'] == 'key':
            print("Received key")
            print(data['key'])
            socket_send(data, bob_port)
        elif data['type'] == ' file':
            print("Received file")
            print(data['file'])
            socket_send(data, bob_port)
        
    except KeyboardInterrupt:
        print("Exiting...") 
        return
    except ConnectionRefusedError:
        print("Bob is not listening")
    except BrokenPipeError:
        print("Bob has disconnected")
    

sel = selectors.DefaultSelector()

alice = socket.socket()
bob = socket.socket()
alice_port = 65430
bob_port = 65431

def monitor(listening):
    print(f"Monitoring communication between Alice and Bob")
    alice.bind(('localhost', 65433))
    bob.bind(('localhost', 65432))
    

    alice.listen()
    alice.setblocking(False)

    bob.listen()
    bob.setblocking(False)

    sel.register(alice, selectors.EVENT_READ, accept_alice) 
    sel.register(bob, selectors.EVENT_READ, accept_bob)
    print("Listening for Communication")

    while True:
        event = sel.select()
        for key, mask in event:
            callback = key.data
            callback(key.fileobj, mask, listening) 



if __name__ == "__main__":
    monitor(listening=0)