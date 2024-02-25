import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import copy


class Alice:
    def __init__(self, n):
        self.n = n
        self.qr = QuantumRegister(n, name = 'qr')
        self.cr = ClassicalRegister(n, name = 'cr')
        self.circuit = QuantumCircuit(self.qr, self.cr, name = 'Alice')
        self.key = np.random.randint(0, high = 2 ** n)
        self.key = np.binary_repr(self.key, n)
        self.bases = []

    def encode_key(self):
        for index, digit in enumerate(self.key):
            if digit == '1':
                self.circuit.x(self.qr[index])
        print("Encoded key:", self.key)

    def switch_bases(self):
        for index in range(len(self.qr)):
            if 0.5 < np.random.random():
                self.circuit.h(self.qr[index])
                self.bases.append('X')
            else:
                self.bases.append('H')
        print("Bases:", self.bases)

    def get_circuit(self):
        return copy.deepcopy(self.circuit)

    def process_bases(self, bob_bases):
        matching_bases = [i for i, (alice_base, bob_base) in enumerate(zip(self.bases, bob_bases)) if alice_base == bob_base]
        print("Matching bases:", matching_bases)
        return matching_bases

    def generate_key(self, matching_bases):
        generated_key = ''.join([self.key[i] for i in matching_bases])
        print("Generated key:", generated_key)
        return generated_key

    def get_key_part(self, part_size):
        key_part = self.key[:part_size]
        print("Key part:", key_part)
        return key_part

n = 10
alice = Alice(n)
alice.encode_key()
alice.switch_bases()

circuit = alice.bases

with open('alice_bases.txt', 'w') as file:
    for value in circuit:
        file.write(value + '\n')

#Random bob circuit for testing
bob_bases = ['X', 'H', 'H', 'X', 'X', 'H', 'H', 'X', 'H', 'X']
matching_bases = alice.process_bases(bob_bases)
generated_key = alice.generate_key(matching_bases)
key_part = alice.get_key_part(2)

