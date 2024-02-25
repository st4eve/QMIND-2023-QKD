import click
import socket

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
def monitor_for_encrypted():
    # TODO:  Need to verify that key has been established (bits and basis have already been received from Alice)
    print("Monitoring for AES encrypted data from Alice")
    s = socket.socket()
    s.bind(('localhost', 65432))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)

if __name__ == "__main__":
    app()