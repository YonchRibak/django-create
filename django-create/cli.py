import click
from .commands import folderize_app

@click.group()
def cli():
    """Django Create: A CLI tool for organizing Django apps."""
    pass

# Register commands to the CLI group
cli.add_command(folderize_app)

if __name__ == '__main__':
    cli()
