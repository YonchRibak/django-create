import click
from .commands import create_model, create_view, create_serializer, create_viewset, create_test, folderize


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

# Register commands under the 'create' group.
create.add_command(create_model)
create.add_command(create_view)
create.add_command(create_viewset)
create.add_command(create_serializer)
create.add_command(create_test)

# Register  folderize command under the 'cli' group.
cli.add_command(folderize, 'folderize')


if __name__ == '__main__':
    cli()
