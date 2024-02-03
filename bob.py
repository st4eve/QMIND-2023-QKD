from qiskit import Aer, QuantumCircuit
from numpy.random import randint

class Bob():
    def __init__(self, qc_alice, comparisonLen):
        self.qc = qc_alice.copy()
        self.num_qubits = self.qc.num_qubits()
        if self.num_qubits < comparisonLen:
            raise Exception("Comparison length must be shorter than the message.")
        self.bases = randint(2, size=self.num_qubits)
        
        
    def measure_message(self, message):
        backend = Aer.get_backend('aer_simulator')
        measurements = []
        n = message.len()
        
        for q in range(n):
            if self.bases[q] == 0:
                message[q].measure(0,0)
            if self.bases[q] == 1:
                message[q].h(0)
                message[q].measure(0,0)

            aer_sim = Aer.get_backend('aer_simulator')  
            results = aer_sim.run(message[q], shots=1, memory=True).result()
            measured_bit = int(results.get_memory()[0])
            measurements.append(measured_bit) 

        self.bobMeasurement = measurements
    
    def remove_garbagebits(self, aliceBases, comparisonLen):
        kept_bits = []
        
        for i in range(self.bobMeasurement.len()):
            if aliceBases[i] == self.bases[i]:
                kept_bits.append(self.bobMeasurement[i])
        
        self.key = kept_bits[comparisonLen:]
        self.comparisonKey = kept_bits[:comparisonLen]
        
    def get_bases(self):
        return self.bases
        
    def get_measurements(self):
        return self.bobMeasurement
    
    def get_key(self):
        return self.key
    
    def get_comparisonkey(self):
        return self.comparisonKey
    
        