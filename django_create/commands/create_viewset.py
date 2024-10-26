import click
from pathlib import Path
import os
from ..utils import (
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    render_template,
    is_import_in_file
)

@click.command(name='viewset')
@click.argument('viewset_name')
@click.option('--path', default=None, help="Subdirectory path inside the viewsets folder.")
@click.pass_context
def create_viewset(ctx, viewset_name, path):
    """
    Create a new Django viewset in the specified app.

    Example:
        django-create myapp create viewset SomeViewset --path products/some_other_folder
    """
    app_name = ctx.obj['app_name']
  

    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name
    if not app_path.exists():
        # If not, check in each subfolder of base_path
        possible_paths = [folder / app_name for folder in base_path.iterdir() if folder.is_dir()]
        app_path = next((p for p in possible_paths if p.exists()), None)
        
        if not app_path:
            click.echo(f"Error: Could not find app '{app_name}' in {base_path} or any subfolder.")
            return
    
    viewsets_py_path = app_path / 'viewsets.py'
    viewsets_folder_path = app_path / 'viewsets'
    
    # Determine the path for the viewset file based on the optional --path flag
    if path:
        custom_viewset_path = viewsets_folder_path / Path(path)
    else:
        custom_viewset_path = viewsets_folder_path

    # Construct the file paths
    viewset_file_name = f"{snake_case(viewset_name)}.py"
    viewset_file_path = custom_viewset_path / viewset_file_name
    init_file_path = custom_viewset_path / '__init__.py'

    # Define the path to the viewset template
    templates_path = Path(__file__).parent.parent / 'templates'
    viewset_template_path = templates_path / 'viewset_template.txt'
    viewset_content = render_template(viewset_template_path, viewset_name=viewset_name)
    viewset_template_path_no_import = templates_path / 'viewset_template_no_import.txt'
    viewset_content_no_import = render_template(viewset_template_path_no_import, viewset_name=viewset_name)

    if viewsets_py_path.exists() and not viewsets_folder_path.exists():
        if is_import_in_file(viewsets_py_path, 'from rest_framework import viewsets'):
            inject_element_into_file(viewsets_py_path, viewset_content_no_import)
        else:
            inject_element_into_file(viewsets_py_path, viewset_content)
    elif viewsets_folder_path.exists() and not viewsets_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_viewset_path.mkdir(parents=True, exist_ok=True)

        # Create the viewset file inside the specified or default folder
        create_element_file(viewset_file_path, viewset_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, viewset_name, viewset_file_name)
    elif viewsets_py_path.exists() and viewsets_folder_path.exists():
        raise click.ClickException(
            "Both 'viewsets.py' and 'viewsets/' folder exist. Please remove one before proceeding."
    )
    elif not viewsets_py_path.exists() and not viewsets_folder_path.exists():
        # Create the viewsets folder and proceed with file creation
        click.echo("No 'viewsets.py' or 'viewsets/' folder found. Creating 'viewsets/' folder...")
        viewsets_folder_path.mkdir(parents=True, exist_ok=True)

        # Create the viewset file inside the new folder
        if path:
            custom_viewset_path.mkdir(parents=True, exist_ok=True)
        create_element_file(viewset_file_path, viewset_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, viewset_name, viewset_file_name)

    click.echo(f"viewset '{viewset_name}' created successfully in app '{app_name}'.")
