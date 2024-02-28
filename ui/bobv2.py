import pickle
import time
import socket

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.progress import Progress
import os

from encryption.aes_encryption import encrypt
from qkd.alice import Alice
from qkd.bob import Bob

key = b'\xb2 \xb9\x0bC\xb9H\x93\xf5\x85U\x84_-\xcc%'

bob = None

bob_bases = None


preamble = """
Running bob.py

You must configure a shared encryption key with Bob before sending files.
To do this, you must first send a series of quantum bits (as a quantum circuit)
to Bob. He will then measure these bits, and send back the basis used to measure.
You then must send Bob the basis you used to generate the bits.
Once the key setup is complete, you can communicate with Bob.
"""

endSetupKeyModeMethods = ['send_basis']
userExecutedMethods = []

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def socket_send(data):
    s = socket.socket()
    s.connect(('localhost', 65432))
    s.sendall(pickle.dumps(data))
    s.close()

def send_basis():
    userExecutedMethods.append("send_basis")
    data = {'type': 'bases_and_key', 'bases': alice.process_bases(bob_bases), 'comp_key': alice.get_comparison_key()}
    socket_send(data)
    print("Basis sent to Bob")

def reset():
    global userExecutedMethods
    userExecutedMethods = []
    cls()
    print(preamble)
    print(menu)

def send_string():
    str_session = PromptSession()
    try:
        string = str_session.prompt('Enter string to send\n>> ')
    except KeyboardInterrupt or EOFError:
        return
    cypher_text, tag, nonce = encrypt(string.encode("ascii"), key)
    data = {'type': 'string', "cypher_text" : cypher_text, "tag" : tag, "nonce" : nonce}
    socket_send(data)
    print(f"Successfully sent message: {string}")

def send_file():
    file_session = PromptSession()
    try:
        file_path = file_session.prompt('Enter path to file\n>> ')
    except KeyboardInterrupt or EOFError:
        return
    file = open(file_path, "r")
    file_text = file.read()
    cypher_text, tag, nonce = encrypt(file_text.encode("ascii"), key)
    data = {"type": 'file', 'filename': f'{os.path.split(file_path)[-1]}', "cypher_text": cypher_text, "tag": tag,
            "nonce": nonce}
    socket_send(data)
    print(f"Successfully sent file: {file_path}")


"""
Setup menu. 
All three lists must be same length and in same order.
"""
# Keywords are commands
menu_keywords = ['send_basis',
                 'reset']
# Description for each command
menu_description = ['Send basis to Alice',
                    'Restart program']

# Method to run when each command is called
menu_methods = [send_basis,
                reset]

menu_keyword_to_method = dict(zip(menu_keywords, menu_methods))

menu = f"Menu\n"
for keyword, description in zip(menu_keywords, menu_description):
    menu += f"[{keyword}] {description}\n"



def main():
    global bob
    cls()
    print(preamble)

    print("Waiting for circuit from Alice")
    s = socket.socket()
    s.bind(('localhost', 65432))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        raw_data = []
        try:
            while True:
                d = conn.recv(1024)
                if not d:
                    break
                raw_data.append(d)
            alice_answer = pickle.loads(b"".join(raw_data))
            if alice_answer["type"] == "qc":
                alice_circuit = alice_answer["circuit"]
                bob = Bob(alice_circuit, verbose=0)
        except KeyboardInterrupt:
            print("Exiting...")

    print(menu)

    # Configure autocomplete for keywords
    auto_completer = WordCompleter(menu_keywords, ignore_case=True)
    session = PromptSession(completer=auto_completer)
    setupKeyMode = True
    while setupKeyMode:
        try:
            text = session.prompt('> ')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        try:
            menu_keyword_to_method[text]()
            if len(userExecutedMethods) == 1:
                if userExecutedMethods[0] == endSetupKeyModeMethods[0]:
                    setupKeyMode = False
        except KeyError:
            print("Invalid Input!")

    print('GoodBye!')

if __name__ == '__main__':
    main()