import click
from rich.progress import Progress
import time

@click.group()
def app():
    """QMIND QKD BB84 Alice Node"""


@app.command()
@click.option("--seed", default=1, help="Basis seed")
@click.option("--basis_override", default="-1", help="Basis to send bits in")
@click.argument("bits")
def send_bits(bits, seed, basis_override):
    if basis_override == "-1":
        print(f"Sending {bits} to Bob in basis randomly generated using {seed}")
    else:
        print(f"Sending {bits} to Bob in basis {basis_override}")

    with Progress() as progress:
        task1 = progress.add_task("[red]Sending bits to Bob...", total=50)
        while not progress.finished:
            progress.update(task1, advance=0.5)
            time.sleep(0.02)

@app.command()
def send_basis():
    print(f"Sending basis to Bob")

@app.command()
@click.option("--string", default="Test String", help="String to send to Alice using AES")
def send_encrypted_string(string):
    # TODO: Need to verify that key has been established using send_bits, send_basis.
    print(f"Sending {string} to Bob using AES encryption")

@app.command()
@click.option("--file_path", help="Path to file to send to Alice using AES")
def send_encrypted_file(file_path):
    # TODO: Need to verify that key has been established using send_bits, send_basis.
    print(f"Sending {file_path} to Bob using AES encryption")

if __name__ == "__main__":
    app()