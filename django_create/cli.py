import click
from .commands.create_model import create_model
from .commands.folderize_app import folderize

@click.group()
@click.argument('app_name')
@click.pass_context
def cli(ctx, app_name):
    """Django Create: A CLI tool for organizing Django apps."""
    ctx.ensure_object(dict)
    ctx.obj['app_name'] = app_name

# Create the 'create' group as a sub-command under the main command.
@cli.group()
@click.pass_context
def create(ctx):
    """Commands for creating elements in the Django app."""
    pass

# Register the 'model' command under the 'create' group.
create.add_command(create_model)
cli.add_command(folderize, 'folderize')


if __name__ == '__main__':
    cli()
