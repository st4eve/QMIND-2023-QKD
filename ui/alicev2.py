import pickle
import time
import socket

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.progress import Progress
import os

from encryption.aes_encryption import encrypt
from qkd.alice import Alice

key = b'\xb2 \xb9\x0bC\xb9H\x93\xf5\x85U\x84_-\xcc%'

alice = Alice(128, verbose=0)

bob_bases = None


preamble = """
Running alice.py

You must configure a shared encryption key with Bob before sending files.
To do this, you must first send a series of quantum bits (as a quantum circuit)
to Bob. He will then measure these bits, and send back the basis used to measure.
You then must send Bob the basis you used to generate the bits.
Once the key setup is complete, you can communicate with Bob.
"""

endSetupKeyModeMethods = ['send_qc',
                          'send_basis']
userExecutedMethods = []

def convert_key(key):
    # Convert binary string to an integer
    integer_value = int(key, 2)
    # Convert integer to bytes
    byte_array = integer_value.to_bytes((len(key) + 7) // 8, byteorder='big')
    return byte_array

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def socket_send(data, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(20)
    s.connect(('localhost', port))
    s.sendall(pickle.dumps(data))
    s.close()
    
def socket_recieve(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', port))
    s.listen()
    conn, addr = s.accept()
    data = []
    while True:
        d = conn.recv(1024)
        if not d:
            break
        data.append(d)
    data = b"".join(data)
    return pickle.loads(data)

def send_qc():
    global bob_bases
    userExecutedMethods.append("send_qc")
    data = {'type': 'qc', 'circuit': alice.get_circuit()}
    socket_send(data, bob_port)
    print("Waiting for Bob to return bases...")
    while True:
        try:
            bob_answer = socket_recieve(65430)
            if bob_answer["type"] == "bases":
                bob_bases = bob_answer["bases"]
                break
        except KeyboardInterrupt:
            print("Exiting...")
            return
        except OSError:
            continue
    print("Bases received from Bob")
    return bob_bases
    
def send_basis():
    userExecutedMethods.append("send_basis")
    data = {'type': 'bases', 'bases': alice.process_bases(bob_bases), 'comp_key': alice.get_comparison_key()}
    socket_send(data, bob_port)
    print("Basis sent to Bob")

def reset():
    global userExecutedMethods
    userExecutedMethods = []
    cls()
    print(preamble)
    print(key_menu)

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
Setup key menu. 
All three lists must be same length and in same order.
"""
# Keywords are commands
key_menu_keywords = ['send_qc',
                     'send_basis',
                     'reset',
                     'quit']
# Description for each command
key_menu_description = ['Send quantum circuit to Bob',
                        'Send basis to Bob',
                        'Restart program',
                        'Exits the program']

# Method to run when each command is called
key_menu_methods = [send_qc,
                    send_basis,
                    reset,
                    exit]

key_menu_keyword_to_method = dict(zip(key_menu_keywords, key_menu_methods))

key_menu = f"Key Generation Menu\n"
for keyword, description in zip(key_menu_keywords, key_menu_description):
    key_menu += f"[{keyword}] {description}\n"

"""
Setup coms menu. 
All three lists must be same length and in same order.
"""
# Keywords are commands
coms_menu_keywords = ['send_string',
                     'send_file',
                     'reset']
# Description for each command
coms_menu_description = ['Send an encrypted text string to Bob',
                        'Send an encrypted file to Bob',
                        'Restart program']

# Method to run when each command is called
coms_menu_methods = [send_string,
                    send_file,
                    reset]

coms_menu_keyword_to_method = dict(zip(coms_menu_keywords, coms_menu_methods))

coms_menu = f"Communications Menu\n"
for keyword, description in zip(coms_menu_keywords, coms_menu_description):
    coms_menu += f"[{keyword}] {description}\n"

bob_port = 65433

def main():
    cls()
    print(preamble)
    print(key_menu)
    setupKeyMode = True
    

    # Configure autocomplete for keywords
    auto_completer = WordCompleter(key_menu_keywords, ignore_case=True)
    session = PromptSession(completer=auto_completer)

    while setupKeyMode:
        try:
            text = session.prompt('> ')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        try:
            key_menu_keyword_to_method[text]()
            if len(userExecutedMethods) == 2:
                if userExecutedMethods[0] == endSetupKeyModeMethods[0] and userExecutedMethods[1] == endSetupKeyModeMethods[1]:
                    setupKeyMode = False
        except KeyError:
            print("Invalid Input!")

    print("Key setup completed successfully!")
    key = convert_key(alice.get_key())
    with Progress() as progress:
        task1 = progress.add_task("[green]Loading communication mode...", total=50)
        while not progress.finished:
            progress.update(task1, advance=0.5)
            time.sleep(0.04)

    cls()
    print(preamble)
    print(coms_menu)
    communicationMode = True
    auto_completer = WordCompleter(coms_menu_keywords, ignore_case=True)
    session = PromptSession(completer=auto_completer)
    while communicationMode:
        try:
            text = session.prompt('> ')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        try:
            coms_menu_keyword_to_method[text]()
        except KeyError:
            print("Invalid Input!")

    print('GoodBye!')

if __name__ == '__main__':
    main()