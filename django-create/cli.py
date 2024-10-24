import click
from .commands.create_model import create_model
from .commands.folderize_app import folderize

@click.group()
def cli():
    """Django Create: A CLI tool for organizing Django apps."""
    pass

@cli.group()
def create():
    """Create various Django components like models, views, etc."""
    pass

# Register subcommands under the 'create' command
create.add_command(create_model)

# Register other commands at the top level
cli.add_command(folderize)

if __name__ == '__main__':
    cli()
