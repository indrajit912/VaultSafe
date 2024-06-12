# This script handles the init command.
# Author: Indrajit Ghosh
# Created On: Jun 12, 2024
# 
import click
from password_manager.db.models import init_db

@click.command()
def init():
    """Initialize the database."""
    init_db()