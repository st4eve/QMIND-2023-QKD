from qiskit import QuantumCircuit, Aer, transpile
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from numpy.random import randint
import numpy as np

'''
#   Generates a random array of bases that bob will use to measure the qubits
#   Input: n - the number of qubits in the message
#   Output: bases - an array of random bases
'''
def bobs_Bases(n):
    bases = randint(2, size=n)  # Generates an array of random 0s and 1s, which represent the bases bob will use to measure the qubits
    print(bases)
    return bases

'''
#   Measures the qubits in the message using the bases that bob generated
#   Input: message - the qubits that alice sent to bob
#          bases - the bases that bob generated
#   Output: measurements - the bits that bob measured
'''
def bob_Measure_Message(message, bases, n):
    # Gets the simulator and creates an empty array to store the measurements
    backend = Aer.get_backend('aer_simulator')
    measurements = []
    
    # loops through each qubit in the message and measures the value in the bases that bob generated
    for q in range(n):
        # If the base is 0, measure in the Z-basis
        if bases[q] == 0:
            message[q].measure(0,0)
        # If the base is 1, measure in the X-basis
        if bases[q] == 1:
            message[q].h(0) # Applies a Hadamard gate to the qubit to change the basis to the X-basis
            message[q].measure(0,0)
            
        # Runs simulation of the circuit
        aer_sim = Aer.get_backend('aer_simulator')  
        results = aer_sim.run(message[q], shots=1, memory=True).result()    # Runs the simulation and stores the results
        measured_bit = int(results.get_memory()[0]) # Gets the results from the simulation and converts it to an integer
        measurements.append(measured_bit)   # Adds measured bit to measurement array
        
    # Returns the measured bits from message
    return measurements
    
    
    # qc.measesureall is a function that measures all the qubits in the circuit
    
'''
#  Removes the bits that were measured in the wrong basis
#  Input: alice_bases - the bases that alice used to encode the message
#         bob_bases - the bases that bob used to measure the message
#         message - the qubits that alice sent to bob
#  Output: kept_bits - the bits that were measured in the correct basis
'''
def remove_garbage_bits(alice_bases, bob_bases, message, n):
    # Creates an empty array to store the bits that will be kept
    kept_bits = []
    
    # Checks if the bases used by alice and bob are the same
    for q in range(n):
        if alice_bases[q] == bob_bases[q]:
            kept_bits.append(message[q])
            
    # Returns the bits that are kept
    return kept_bits
    

np.random.seed(seed=0)
n = 100 # n changes depending on the message size

# Elements which are received from Alice using Python Sockets Library
message = []    # Message received from Alice using Python Sockets
a_bases = []    # Bases used by Alice to encode the message

# Calls function to create the bases that bob will use to measure the qubits
b_bases = bobs_Bases(n)

# Calls function to measure the qubits in the message
b_results = bob_Measure_Message(message, b_bases, n)

# Removes the bits that were measured in the wrong basis and stores the kept bits in a variable
serect_key = remove_garbage_bits(a_bases, b_bases, b_results, n)


# Make file that imports all peoples function