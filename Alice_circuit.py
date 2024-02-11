import qiskit
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute, BasicAer
from qiskit.tools.visualization import plot_histogram

# Assigning registors for qubits

n = 5 #max is 23 for some reason

#Assigning registors for quantum and classical circuit
qr = QuantumRegister(n, name = 'qr')
cr = ClassicalRegister(n, name = 'cr')

#Alice's Quantum circuit
alice = QuantumCircuit(qr, cr, name = 'Alice')

#Generate a random number of qubits
alice_key = np.random.randint(0, high = 2 ** n)

#Type cast key to binary for encoding
alice_key = np.binary_repr(alice_key, n)

# Encode key as alice qubits, by default, all qubits are all set to |0> 
for index, digit in enumerate(alice_key):
    if digit == '1':
        alice.x(qr[index]) # if key has a '1', change state to |1>
        
# Randomly switch half the qubits to diagonale state using x gate
        
alice_qubits = []                   # Create empty basis table
for index in range(len(qr)):       
    if 0.5 < np.random.random():  
        alice.h(qr[index])         # change to diagonal basis
        alice_qubits.append('X')    # character for diagonal basis
    else:
        alice_qubits.append('Z')    # character for computational basis


# Function that tales output of a quantum circuit (made up only of x and 
#h gates), lets say qc1, and initializes another circuit, with the same state, qc2
def SendState(qc1, qc2, qc1_name):
    
    # Quantum state is retrieved from qasm code of qc1
    quantum_state = qc1.qasm().split(sep=';')[4:-1]

    # Process the code to get the instructions
    for index, instruction in enumerate(quantum_state):
        quantum_state[index] = instruction.lstrip()

    # Parse the instructions and apply to new circuit
    for instruction in quantum_state:
        if instruction[0] == 'x':
            old_qr = int(instruction[5:-1])
            qc2.x(qr[old_qr])
        elif instruction[0] == 'h':
            old_qr = int(instruction[5:-1])
            qc2.h(qr[old_qr])
        elif instruction[0] == 'm': # exclude measuring:
            pass
        else:
            raise Exception('Unable to parse instruction')
        
# Send Alice's qubits to Bob

bob = QuantumCircuit(qr, cr, name = 'Bob')

SendState(alice, bob, 'Alice')

#TEST CASE
# Add measurement operations to the circuits
alice.measure(qr, cr)
bob.measure(qr, cr)

# Execute the circuits on a quantum simulator
simulator = BasicAer.get_backend('qasm_simulator')
alice_result = execute(alice, simulator).result()
bob_result = execute(bob, simulator).result()   

# Print the results
print("Alice's results:", alice_result.get_counts())
print("Bob's results:", bob_result.get_counts())


