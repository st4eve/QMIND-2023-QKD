import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import copy


class Alice:
    def __init__(self, 
                 n,
                 verbose=0):
        self.n = n
        self.circuit = [QuantumCircuit(1,1) for i in range(n)]
        self.key = np.random.randint(0, 2, size=n)
        self.bases = []
        self.verbose = verbose
        
        
        self.encode_key()
        self.switch_bases()

    def encode_key(self):
        for i, digit in enumerate(self.key):
            if digit:
                self.circuit[i].x(0)
        if self.verbose:
            print("Encoded key:", self.key)

    def switch_bases(self):
        for i, _ in enumerate(self.circuit):
            if 0.5 < np.random.random():
                self.circuit[i].h(0)
                self.bases.append('H')
            else:
                self.bases.append('X')
        if self.verbose:
            print("Bases:", self.bases)

    def get_circuit(self):
        return copy.deepcopy(self.circuit)

    def process_bases(self, bob_bases):
        matching_bases = [i for i, (alice_base, bob_base) in enumerate(zip(self.bases, bob_bases)) if alice_base == bob_base]
        self.bob_matching_bases = matching_bases
        if self.verbose:
            print("Matching bases index:", matching_bases)
            print('Matching bases values:', [self.bases[i] for i in matching_bases])
        self.generate_key()
        return matching_bases

    def generate_key(self):
        generated_key = ''.join([str(self.key[i]) for i in self.bob_matching_bases])
        if self.verbose:
            print("Length of Generated key:", len(generated_key))
            print('Generated key:', generated_key)
        return generated_key

    def get_comparison_key(self, comparisonLength):
        self.comparison_key = self.key[:comparisonLength]
        self.key = self.key[comparisonLength:]
        if self.verbose:
            print("Key part:", self.comparison_key)
        return self.comparison_key


if __name__ == '__main__':
    n = 300
    alice = Alice(n)
    alice.encode_key()
    alice.switch_bases()

    circuit = alice.bases

    with open('alice_bases.txt', 'w') as file:
        for value in circuit:
            file.write(value + '\n')

    #Random bob circuit for testing
    bob_bases = ['X' if 0.5 < np.random.random() else 'H' for i in range(n)]
    matching_bases = alice.process_bases(bob_bases)
    generated_key = alice.generate_key(matching_bases)
    key_part = alice.get_key_part(np.abs(len(generated_key)-128))

