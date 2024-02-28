import click
import socket
from encryption.aes_encryption import *
import pickle

key = b'\xb2 \xb9\x0bC\xb9H\x93\xf5\x85U\x84_-\xcc%' # Global key, to be updated by QKD methods

@click.group()
def app():
    """QMIND QKD BB84 Bob Node"""


@app.command()
@click.option("--seed", default=1, help="Basis seed")
@click.option("--basis_override", default="-1", help="Basis to send bits in")
def monitor(seed, basis_override):
    if basis_override == "-1":
        print(f"Monitoring for bits from Alice in basis randomly generated using {seed}")
    else:
        print(f"Monitoring for bits from Alice in basis {basis_override}")

@app.command()
def monitor_for_qc():
    pass


@app.command()
def send_basis_used():
    pass
    #bob = Bob()

@app.command()
def monitor_for_encrypted():
    # TODO:  Need to verify that key has been established (bits and basis have already been received from Alice)
    print("Monitoring for AES encrypted data from Alice")
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
            encrypt_data = pickle.loads(b"".join(raw_data))
            unencrypt_data = decrypt(encrypt_data["cypher_text"], encrypt_data["tag"], encrypt_data["nonce"], key)
            if encrypt_data["type"] == 'file':
                file = open(f'./{encrypt_data["filename"]}', "w")
                file.write(unencrypt_data.decode("ascii"))
                file.close()
                print(f"File received and saved to ./{encrypt_data['filename']}")
            elif encrypt_data["type"] == 'string':
                print(f"String received: {unencrypt_data.decode('ascii')}")
        except KeyboardInterrupt:
            print("Exiting...")

if __name__ == "__main__":
    app()