# The main entry point for the CLI.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
# Run in dev mode: `python -m password_manager.cli [command] [arguments]`
# Installation: 
#      [1] ` pip install git+https://github.com/indrajit912/PasswordManager.git`
#      [2] `password-manager --help`
# 
import click
from password_manager.commands import init, add

@click.group()
def cli():
    pass

cli.add_command(init.init)
cli.add_command(add.add)

if __name__ == '__main__':
    cli()
