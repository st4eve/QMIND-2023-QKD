from qiskit import Aer, QuantumCircuit
from numpy.random import randint

class Bob():
    def __init__(self, qc_alice, comparisonLen):
        # Creates copy of Alice quantum circuit
        self.qc = qc_alice.copy()   
        
        # Determines the number of qubits in quantum circuit
        self.num_qubits = self.qc.num_qubits()  
        
        # Checks if the comparison length is more than amount of qubits
        if self.num_qubits < comparisonLen:
            # Throws execption
            raise Exception("Comparison length must be shorter than the message.")  
        
        # Create bases for bob
        self.bases = randint(2, size=self.num_qubits)   
        
    def measure_message(self, message):
        # Creates simulator
        backend = Aer.get_backend('aer_simulator')
        
        # measurement array and number of qubits created
        measurements = []
        n = message.len()
        
        for q in range(n):
            # If the base is 0, measure in the Z-basis
            if self.bases[q] == 0:
                message[q].measure(0,0)
             # If the base is 1, measure in the X-basis
            if self.bases[q] == 1:
                # Applies a Hadamard gate to the qubit to change the basis to the X-basis
                message[q].h(0)
                message[q].measure(0,0)

            # Runs simulation of the  quantum circuit
            results = backend.run(message[q], shots=1, memory=True).result()
            
            # Gets the results from the simulation and converts it to an integer
            measured_bit = int(results.get_memory()[0])
            
            # Adds measured bit to measurement array
            measurements.append(measured_bit) 

        self.bobMeasurement = measurements
    
    def remove_garbagebits(self, aliceBases, comparisonLen):
        kept_bits = []
        
        # Checks if the bases used by alice and bob are the same
        for i in range(self.bobMeasurement.len()):
            if aliceBases[i] == self.bases[i]:
                kept_bits.append(self.bobMeasurement[i])
        
        # Stores the key 
        self.key = kept_bits[comparisonLen:]
        
        # Stores the qubits to be compared
        self.comparisonKey = kept_bits[:comparisonLen]
        
    def check_eve(self, aliceCompareKey):
        # Compare length of alice comparison key to bob comparison key
        if aliceCompareKey != self.comparisonKey:
            raise Exception("Comparsion keys are not the same length")
        
        # Counter for number of same bases
        sameBases = 0.0
        
        for i in range(aliceCompareKey.len()):
            # Check is in same bases
            if aliceCompareKey[i] == self.get_comparisonkey[i]:
                sameBases = sameBases + 1
        
        # Calculate percent of same bases
        percentageSame = (sameBases / aliceCompareKey.len()) * 100
        
        # Print message
        if percentageSame < 75.0:
            print("less than 75% of bases were wrong")    
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
    
        