import click
from pathlib import Path
import os
from ..utils import (
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    render_template
)

@click.command(name='view')
@click.argument('view_name')
@click.option('--path', default=None, help="Subdirectory path inside the views folder.")
@click.pass_context
def create_view(ctx, view_name, path):
    """
    Create a new Django view in the specified app.

    Example:
        django-create myapp create view SomeView --path products/some_other_folder
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
        
    views_py_path = app_path / 'views.py'
    views_folder_path = app_path / 'views'
    
    # Determine the path for the view file based on the optional --path flag
    if path:
        custom_view_path = views_folder_path / Path(path)
    else:
        custom_view_path = views_folder_path

    # Construct the file paths
    view_file_name = f"{snake_case(view_name)}.py"
    view_file_path = custom_view_path / view_file_name
    init_file_path = custom_view_path / '__init__.py'

    # Define the path to the view template
    templates_path = Path(__file__).parent.parent / 'templates'
    view_template_path = templates_path / 'view_template.txt'
    view_content = render_template(view_template_path, view_name=view_name)


    if views_py_path.exists() and not views_folder_path.exists():
        inject_element_into_file(views_py_path, view_content)
    elif views_folder_path.exists() and not views_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_view_path.mkdir(parents=True, exist_ok=True)

        # Create the view file inside the specified or default folder
        create_element_file(view_file_path, view_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, view_name, view_file_name)
    elif views_py_path.exists() and views_folder_path.exists():
        raise click.ClickException(
            "Both 'views.py' and 'views/' folder exist. Please remove one before proceeding."
    )
    else:
        raise click.ClickException(
            "Neither 'views.py' nor 'views/' folder exists. Please create one before proceeding."
        )

    click.echo(f"view '{view_name}' created successfully in app '{app_name}'.")
