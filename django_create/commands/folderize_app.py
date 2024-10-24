import click
import os
import re

@click.command()
@click.pass_context
def folderize(ctx):
    """
    Organize a Django app by creating folders for models, views, and tests.
    Removes models.py, views.py, and tests.py if they exist.
    If any of these files contain class definitions, a warning is shown and the operation is aborted.
    """
    app_name = ctx.obj['app_name']
    click.echo(f"Folderizing app '{app_name}'...")

    base_path = os.path.join(os.getcwd(), app_name)
    if not os.path.exists(base_path):
        click.echo(f"Error: The app '{app_name}' does not exist.")
        return

    files_to_remove = ['models.py', 'views.py', 'tests.py']
    folders_to_create = ['models', 'views', 'tests']

    # Check if any of the files contain class definitions before proceeding
    for file_name in files_to_remove:
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            if contains_class_definition(file_path):
                click.echo(
                    f"Warning: '{file_name}' contains class definitions. "
                    f"Aborting to prevent data loss."
                )
                return

    # Remove files and create folders
    for file_name in files_to_remove:
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            click.echo(f"Removed '{file_name}'.")

    for folder_name in folders_to_create:
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        init_file = os.path.join(folder_path, '__init__.py')
        with open(init_file, 'w') as f:
            f.write("# This file allows the directory to be treated as a Python module.\n")
        click.echo(f"Created folder '{folder_name}' with __init__.py.")

    click.echo(f"App '{app_name}' has been folderized successfully.")

def contains_class_definition(file_path):
    """
    Check if a file contains any class definitions.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Look for any class definitions using a regex pattern
        return re.search(r'^\s*class\s+\w+', content, re.MULTILINE) is not None
