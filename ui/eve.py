import click
import socket
import pickle
from numpy.random import randint
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def measure_message(self, message, bases):
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


def unpickle_data(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        raw_data = []
        try:
            while True:
                d = conn.recv(1024)
                if not d:
                    break
                raw_data.append(d)
            data = pickle.loads(b"".join(raw_data))
            if data["type"] == 'qc':
                print("Received quantum circuit from Alice")
                return data
            elif data['type'] == 'bases':
                print("Received bases")
                print(data['bases'])
                return data
            elif data['type'] == 'string':
                print("Received encrypted string")
                print(data['cypher_text'])
                return None
            
        except KeyboardInterrupt:
            print("Exiting...")





@click.group()
def app():
    """QMIND QKD BB84 Eve Node"""

@app.command()
@click.option("--listening", default="0", help="whether eve will measure the qc")
def monitor(listening):
    while True:
        print(f"Monitoring communication between Alice and Bob")
        alice = socket.socket()
        bob = socket.socket()
        alice.bind(('localhost', 65433))
        alice.listen()
        print("Listening for Alice")
        conn1, addr1 = alice.accept()
        data = unpickle_data(conn1, addr1)
        if data is None:
            pass
        if data['type'] == 'qc':
            qc = data['qc']
            if listening: 
                eve_bases = ['X' if randint(0, 2) else 'H' for i in range(len(qc))]
                measurements, qc = measure_message(qc, eve_bases)
                data['qc'] = qc
                print(measurements)
            
            bob.connect()
            bob.sendall(pickle.dumps(data))    
    
     


if __name__ == "__main__":
    app()