# This script handles the get command.
# Author: Indrajit Ghosh
# Created On: Jun 13, 2024
#
import click
import webbrowser
import os

from vaultsafe.config import RUN_FLASK_PY, DEFAULT_SERVER_PORT, VENV_PYTHON

@click.command()
@click.option('--port', default=DEFAULT_SERVER_PORT, help=f'Port for the Flask server (default is {DEFAULT_SERVER_PORT})')
def server(port):
    """
    Run the server for VaultSafe, providing a GUI interface.

    To utilize the GUI, ensure you have initialized the app with:
    $ vaultsafe init

    Options:
    --port : Specifies the port for the server. Defaults to 8000.
             Use --port to specify a different port.

    Examples:
    $ vaultsafe server
    Starts the server on the default port.

    $ vaultsafe server --port 9000
    Starts the server on port 9000.
    """
    webbrowser.open(f"http://localhost:{port}")

    os.system(f"{VENV_PYTHON} {RUN_FLASK_PY} {port}")
