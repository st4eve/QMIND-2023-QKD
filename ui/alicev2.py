import pickle
import time
import socket

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.progress import Progress
import os

from encryption.aes_encryption import encrypt, decrypt
from qkd.alice import Alice
import multiprocessing

from selectors import DefaultSelector
import selectors

key = b'\xb2 \xb9\x0bC\xb9H\x93\xf5\x85U\x84_-\xcc%'
key = None

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

sel = DefaultSelector()

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
            bob_answer = socket_recieve(recieve_port)
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
    global key
    userExecutedMethods.append("send_basis")
    data = {'type': 'bases', 'bases': alice.process_bases(bob_bases), 'key': alice.get_comparison_key()}
    socket_send(data, bob_port)
    print("Basis sent to Bob")
    data = socket_recieve(recieve_port)
    if alice.comparison_key == data['key']:
        key = convert_key(alice.get_key())
        return True
    else:
        print("Key comparison failed, someone is listening to this channel")
        print("Restarting key generation protocol")
        time.sleep(5)
        reset()
        return False

def reset():
    global key
    global setupKeyMode
    global communicationMode
    global userExecutedMethods
    global thread
    userExecutedMethods = []
    cls()
    print(preamble)
    print(key_menu)
    key = None
    setupKeyMode = True
    communicationMode = False
    thread.kill()
    thread = multiprocessing.Process(target=check_com)

def send_string():
    str_session = PromptSession()
    try:
        string = str_session.prompt('Enter string to send\n>> ')
    except KeyboardInterrupt or EOFError:
        return
    cypher_text, tag, nonce = encrypt(string.encode("ascii"), key)
    data = {'type': 'string', "cypher_text" : cypher_text, "tag" : tag, "nonce" : nonce}
    socket_send(data, bob_port)
    print(f"Successfully sent message: {string}")

def send_file():
    file_session = PromptSession()
    try:
        file_path = file_session.prompt('Enter path to file\n>> ')
    except KeyboardInterrupt or EOFError:
        return
    while True:
        try:
            file = open(file_path, "r")
            break
        except FileNotFoundError:
            print("File not found")
            file_path = file_session.prompt('Enter path to file\n>> ')
    file_text = file.read()
    cypher_text, tag, nonce = encrypt(file_text.encode("ascii"), key)
    data = {"type": 'file', 'filename': f'{os.path.split(file_path)[-1]}', "cypher_text": cypher_text, "tag": tag,
            "nonce": nonce}
    socket_send(data, bob_port)
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
                     'reset',
                     'quit']
# Description for each command
coms_menu_description = ['Send an encrypted text string to Bob',
                        'Send an encrypted file to Bob',
                        'Restart program',
                        'Exits the program']

def quit():
    thread.kill()
    sel.close()
    exit()


# Method to run when each command is called
coms_menu_methods = [send_string,
                    send_file,
                    reset,
                    quit]

coms_menu_keyword_to_method = dict(zip(coms_menu_keywords, coms_menu_methods))

coms_menu = f"Communications Menu\n"
for keyword, description in zip(coms_menu_keywords, coms_menu_description):
    coms_menu += f"[{keyword}] {description}\n"


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

bob_port = 65433
recieve_port = 65430
thread = multiprocessing.Process(target=check_com)

def main():
    global key
    global communicationMode
    global setupKeyMode
    cls()

    setupKeyMode = True
    while True:
        if setupKeyMode:
            print(preamble)
            print(key_menu)
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
                    if text == '':
                        continue
                    key_menu_keyword_to_method[text]()
                    if key != None:
                        setupKeyMode = False
                except KeyError:
                    print("Invalid Input!")

            print("Key setup completed successfully!")
            with Progress() as progress:
                task1 = progress.add_task("[green]Loading communication mode...", total=50)
                while not progress.finished:
                    progress.update(task1, advance=0.5)
                    time.sleep(0.04)
        if not setupKeyMode:
            cls()
            print(preamble)
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
                except KeyError as e:
                    print("Invalid Input!")

    print('GoodBye!')

if __name__ == '__main__':
    main()