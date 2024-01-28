import click

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


if __name__ == "__main__":
    app()