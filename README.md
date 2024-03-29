# QMIND-2023-QKD
A simulated quantum key generation system for use with network communication. Keys will be generated by passing quantum circuit objects from user to user. The generated keys will then be used as an encryption key to send files, text, and run a command line interface. All commands and output will be encrypted before sending.

# Using the system
QSSH works by running a simulated BB84 QKD protocol to generate a completely secure key over two machines. A man-in-the-middle attack can be conducted, at which point the key generation algorithm will fail, signaling to the client and server that their communication channel is not secure. Once the key is generated it is used to encrypt all communication between the client and server including the file transfer, messaging, and an an ssh-like command line interface.
