import qiskit
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute, BasicAer
from qiskit.tools.visualization import plot_histogram

class QuantumCircuitObject:
    def __init__(self, n, name):
        self.n = n
        self.qr = QuantumRegister(n, name = 'qr')
        self.cr = ClassicalRegister(n, name = 'cr')
        self.circuit = QuantumCircuit(self.qr, self.cr, name = name)
        self.key = np.random.randint(0, high = 2 ** n)
        self.key = np.binary_repr(self.key, n)
        self.qubits = []
        self.same_basis_bits = []
        self.measurement_result = []

    def encode_key(self):
        for index, digit in enumerate(self.key):
            if digit == '1':
                self.circuit.x(self.qr[index])

    def switch_qubits(self):
        for index in range(len(self.qr)):
            if 0.5 < np.random.random():
                self.circuit.h(self.qr[index])
                self.qubits.append('X')
            else:
                self.qubits.append('Z')

    def send_state(self, other_circuit):
        quantum_state = self.circuit.qasm().split(sep=';')[4:-1]
        for index, instruction in enumerate(quantum_state):
            quantum_state[index] = instruction.lstrip()
        for instruction in quantum_state:
            if instruction[0] == 'x':
                old_qr = int(instruction[5:-1])
                other_circuit.circuit.x(other_circuit.qr[old_qr])
            elif instruction[0] == 'h':
                old_qr = int(instruction[5:-1])
                other_circuit.circuit.h(other_circuit.qr[old_qr])
            elif instruction[0] == 'm':
                pass
            else:
                raise Exception('Unable to parse instruction')

    def compare_qubits(self, other_circuit):
        same_qubits = []
        for qubit1, qubit2 in zip(self.qubits, other_circuit.qubits):
            if qubit1 == qubit2:
                same_qubits.append(qubit1)
        return same_qubits

    def remove_garbage(self, same_qubits):
        for qubit in same_qubits:
            self.qubits.remove(qubit)

    def measure_qubits(self):
        self.circuit.measure(self.qr, self.cr)
        simulator = BasicAer.get_backend('qasm_simulator')
        result = execute(self.circuit, simulator).result()
        counts = result.get_counts(self.circuit)
        # Get the most common result
        self.measurement_result = max(counts, key=counts.get)

    def save_same_basis_bits(self, other_circuit):
        for bit1, bit2 in zip(self.qubits, other_circuit.qubits):
            if bit1 == bit2:
                self.same_basis_bits.append(bit1)

n = 20
alice = QuantumCircuitObject(n, 'Alice')
alice.encode_key()
alice.switch_qubits()

bob = QuantumCircuitObject(n, 'Bob')
alice.send_state(bob)

same_qubits = alice.compare_qubits(bob)

alice.save_same_basis_bits(bob)
bob.save_same_basis_bits(alice)

alice.remove_garbage(same_qubits)
bob.remove_garbage(same_qubits)

#TEST CASE
def test_QuantumCircuitObject_send_and_compare():
    # Initialize Alice's circuit with 10 quantum bits
    n = 10
    alice = QuantumCircuitObject(n, 'Alice')
    
    # Encode the key in Alice's circuit
    alice.encode_key()
    
    # Switch the qubits in Alice's circuit
    alice.switch_qubits()

    # Initialize Bob's circuit with 10 quantum bits
    bob = QuantumCircuitObject(n, 'Bob')

    #Swtich bob's qubits
    bob.switch_qubits()
    
    # Alice sends her state to Bob
    alice.send_state(bob)

    # Compare the qubits in Alice's and Bob's circuits
    same_qubits = alice.compare_qubits(bob)

    # Measure the qubits in Alice's and Bob's circuits
    alice.measure_qubits()
    bob.measure_qubits()

   # Print the qubits in Alice's and Bob's circuits
    print("Alice's qubits: ", alice.qubits)
    print("Bob's qubits: ", bob.qubits)

    # Save the same basis bits in Alice's and Bob's circuits
    alice.save_same_basis_bits(bob)
    bob.save_same_basis_bits(alice)

    # Remove the garbage from Alice's and Bob's circuits
    alice.remove_garbage(same_qubits)
    bob.remove_garbage(same_qubits)

    # Print the results
    print("Quantum bits that Bob got correctly: ", bob.same_basis_bits)

test_QuantumCircuitObject_send_and_compare()

