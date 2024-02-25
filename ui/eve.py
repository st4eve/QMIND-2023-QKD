import click


@click.group()
def app():
    """QMIND QKD BB84 Eve Node"""

@app.command()
def monitor():
    print(f"Monitoring communication between Alice and Bob")


if __name__ == "__main__":
    app()