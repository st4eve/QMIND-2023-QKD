from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit
from numpy.random import randint
from alice import Alice
import copy

class Bob():
    def __init__(self, 
                 qc_alice, 
                 minComparisonLen):
        # Creates copy of Alice quantum circuit
        self.qc = copy.deepcopy(qc_alice)
        
        # Determines the number of qubits in quantum circuit
        self.num_qubits = len(self.qc) 
        
        # Checks if the comparison length is more than amount of qubits
        if self.num_qubits//4 < minComparisonLen:
            # Throws execption
            raise Exception("Comparison length must be shorter than the message.")  
        else:
            self.minComparisonLen = minComparisonLen
        
        # Create bases for bob
        self.bases = ['X' if randint(0, 2) else 'H' for i in range(self.num_qubits)]
        self.measure_message(self.qc)
        
    def measure_message(self, message):
        # Creates simulator
        simulator = AerSimulator(method='statevector')
        
        # measurement array and number of qubits created
        measurements = []
        n = self.num_qubits
        
        for q in range(n):
            # If the base is 0, measure in the Z-basis
            if self.bases[q] == 'X':
                message[q].measure(0,0)
             # If the base is 1, measure in the X-basis
            if self.bases[q] == 'H':
                # Applies a Hadamard gate to the qubit to change the basis to the Z-basis
                message[q].h(0)
                message[q].measure(0,0)

            # Runs simulation of the  quantum circuit
            results = simulator.run(message[q], shots=10, memory=True).result()
            
            # Gets the results from the simulation and converts it to an integer
            measured_bit = int(results.get_memory()[0])
            
            # Adds measured bit to measurement array
            measurements.append(measured_bit) 

        self.bobMeasurement = measurements
    
    def remove_garbagebits(self, aliceBases):

        kept_bits = [self.bobMeasurement[i] for i in aliceBases]
        print('Bobs measurements: ', self.bobMeasurement)
        print("Bobs Kept bits: ", kept_bits)
        self.comparisonLength = len(kept_bits) - self.num_qubits//4
        if self.comparisonLength < self.minComparisonLen:
            raise Exception("Insufficient comparison bits")
        # Stores the key 
        self.key = kept_bits[self.comparisonLength:]
        
        # Stores the qubits to be compared
        self.comparisonKey = kept_bits[:self.comparisonLength]
        
    def check_eve(self, aliceCompareKey):
        # Compare length of alice comparison key to bob comparison key
        if len(aliceCompareKey) != len(self.comparisonKey):
            raise Exception("Comparsion keys are not the same length")
        
        # Counter for number of same bases
        sameBases = 0.0
        
        for i in range(len(aliceCompareKey)):
            # Check is in same bases
            if aliceCompareKey[i] == self.comparisonKey[i]:
                sameBases = sameBases + 1
        
        # Calculate percent of same bases
        percentageSame = (sameBases / len(aliceCompareKey)) * 100
        print(percentageSame)
        
        # Print message
        if percentageSame < 75.0:
            print("More than 25% of the qubits did not match. Eve has tampered with the message.")    
            print("Key is not secured")
        else:
            print("Key is secured")
        
    def get_bases(self):
        return self.bases
        
    def get_measurements(self):
        return self.bobMeasurement
    
    def get_key(self):
        return self.key
    
    def get_comparisonkey(self):
        return self.comparisonKey
    
if __name__ == '__main__':
    print('Bob class file')
    # Create Alice object
    alice = Alice(32, verbose=0)
    # Create Bob object
    bob = Bob(alice.get_circuit(), 4)
    print(alice.get_circuit()[0].draw())
    print(bob.qc[0].draw())
    same_bases = alice.process_bases(bob.get_bases())
    bob.remove_garbagebits(same_bases)
    compare_key = alice.get_comparison_key(bob.comparisonLength)
    bob.check_eve(compare_key)