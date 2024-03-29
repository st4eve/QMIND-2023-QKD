import pickle
import selectors
import multiprocessing
import time
import socket

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.progress import Progress
import os

from encryption.aes_encryption import encrypt, decrypt
from qkd.alice import Alice
from qkd.bob import Bob
import multiprocessing

key = b'\xb2 \xb9\x0bC\xb9H\x93\xf5\x85U\x84_-\xcc%'
key = None

bob = None
alice = None

bob_bases = None


setupKeyMode = True
communicationMode = False


preamble = """
Running bob.py

You must configure a shared encryption key with Alice before sending files.
To do this, you must first recieve the quantum circuit from alice.
You will then measure these bits, and send back the basis used to measure.
You then confirm which bases encodings match and compare a portion of the key
to verify unaltered transmission.
Once the key setup is complete, you can communicate with Alice.
"""

endSetupKeyModeMethods = ['send_basis']
userExecutedMethods = []

def convert_key(key):
    # Convert binary string to an integer
    integer_value = int(key, 2)
    # Convert integer to bytes
    byte_array = integer_value.to_bytes((len(key) + 7) // 8, byteorder='big')
    return byte_array

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def socket_send(data):
    s = socket.socket()
    s.settimeout(20)
    s.connect(('localhost', 65432))
    s.sendall(pickle.dumps(data))
    s.close()

def send_basis():
    global key
    userExecutedMethods.append("send_basis")
    data = {'type': 'bases', 'bases': bob.get_bases()}
    socket_send(data)
    print("Basis sent to Alice")
    print("Waiting for alice to send correct basis...")
    data = socket_recieve(65431)
    try:
        if data['type'] == 'bases':
            print("Received correct bases from Alice")
            bob.remove_garbagebits(data['bases'])
            print("Garbage bits removed")
            print('Comparing to comparison key to verify unaltered transmission')
            time.sleep(1)
            socket_send({'type': 'key', 'key': bob.get_comparisonkey()})
            if bob.check_eve(data['key']):
                print('Unaltered transmission verified')
                key = convert_key(''.join(str(i) for i in bob.get_key()))
                print('Key successfully created')
                time.sleep(5)
            else:
                print('Key comparison failed, someone is listening to this channel')
                print('Restarting key generation protocol')
                time.sleep(5)
                reset()
                return
    except KeyError:
        print("Invalid data received")

def reset():
    global userExecutedMethods
    global key
    global setupKeyMode
    global communicationMode
    global thread
    userExecutedMethods = []
    cls()
    print(preamble)
    print(menu)
    key = None
    setupKeyMode = True
    communicationMode = False
    if thread != None:
        thread.kill()
        thread = multiprocessing.Process(target=check_com)
        sel.close()

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
                 'reset',
                 'quit']
# Description for each command
menu_description = ['Send basis to Alice',
                    'Restart program',
                    'Exits the program']

# Method to run when each command is called
menu_methods = [send_basis,
                reset,
                exit]

menu_keyword_to_method = dict(zip(menu_keywords, menu_methods))

menu = f"Menu\n"
for keyword, description in zip(menu_keywords, menu_description):
    menu += f"[{keyword}] {description}\n"

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
    conn.close()
    return pickle.loads(data)

"""
Setup coms menu. 
All three lists must be same length and in same order.
"""
# Keywords are commands
coms_menu_keywords = ['send_string',
                     'send_file',
                     'reset',
                     'quit']
# Description for each command
coms_menu_description = ['Send an encrypted text string to Bob',
                        'Send an encrypted file to Bob',
                        'Restart program',
                        'Exits the program']

# Method to run when each command is called
coms_menu_methods = [send_string,
                    send_file,
                    reset,
                    quit]

coms_menu_keyword_to_method = dict(zip(coms_menu_keywords, coms_menu_methods))

coms_menu = f"Communications Menu\n"
for keyword, description in zip(coms_menu_keywords, coms_menu_description):
    coms_menu += f"[{keyword}] {description}\n"

def wait_for_qc():
    print("Waiting for quantum circuit from Alice")
    data = socket_recieve(65431)
    if data["type"] == "qc":
        alice_circuit = data["circuit"]
        bob = Bob(alice_circuit, verbose=0)
        print("Quantum circuit received")
        return bob

def quit():
    thread.kill()
    sel.close()
    exit()

def accept(sock, mask):
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)
    
def read(conn, mask):
    raw_data = []
    try:
        while True:
            d = conn.recv(1024)
            if not d:
                break
            raw_data.append(d)
        if raw_data  == []:
            sel.unregister(conn)
            conn.close()
            return
        data = pickle.loads(b"".join(raw_data))
        print('\n')
        if data['type'] == 'qc':
            print("Received quantum circuit from Alice")
            print(data['circuit'])
        elif data['type'] == 'bases':
            print("Received bases")
            print(''.join(str(i) for i in data['bases']))
        elif data['type'] == 'string':
            print("Received string")
            print(decrypt(data['cypher_text'], data['tag'], data['nonce'], key))
        elif (data['type'] == 'key') | (data['type'] == 'comp_key'):
            print("Received key")
            print(data['key'])
        elif data['type'] == 'file':
            print("Received file")
            print(decrypt(data['cypher_text'], data['tag'], data['nonce'], key))
        print('\n')
    except KeyboardInterrupt:
        print("Exiting...")
        return
     
def check_com():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', recieve_port))
    s.listen()
    
    sel.register(s, selectors.EVENT_READ, accept)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)   


sel = selectors.DefaultSelector()
bob_port = 65433
recieve_port = 65431
thread = multiprocessing.Process(target=check_com)



def main():
    global bob
    global key
    global setupKeyMode
    global communicationMode
    while True:
        if setupKeyMode:
            cls()
            print(preamble)


            bob = wait_for_qc() 


            print(menu)

            # Configure autocomplete for keywords
            auto_completer = WordCompleter(menu_keywords, ignore_case=True)
            session = PromptSession(completer=auto_completer)
            while setupKeyMode:
                try:
                    text = session.prompt('> ')
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    break

                try:
                    if text == '':
                        continue
                    menu_keyword_to_method[text]()
                    if key != None:
                        setupKeyMode = False
                except KeyError:
                    print("Invalid Input!")
        
        if not setupKeyMode:
            cls()
            print('Now setup for communication')
            print(coms_menu)
            communicationMode = True
            auto_completer = WordCompleter(coms_menu_keywords, ignore_case=True)
            session = PromptSession(completer=auto_completer)
            thread.start()
            while communicationMode:
                try:
                    text = session.prompt('> ')
                except KeyboardInterrupt:
                    continue
                except EOFError:
                    break
                try:
                    if text == '':
                        continue
                    coms_menu_keyword_to_method[text]()
                except KeyError:
                    print("Invalid Input!")

    print('GoodBye!')

if __name__ == '__main__':
    main()