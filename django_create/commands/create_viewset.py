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
    class_dict = ctx.obj.get('class_dict', None)  # Retrieve class_dict from ctx.obj

    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name
    if not app_path.exists():
        # If not, check in each subfolder of base_path
        possible_paths = [folder / app_name for folder in base_path.iterdir() if folder.is_dir()]
        app_path = next((p for p in possible_paths if p.exists()), None)
        
        if not app_path:
            click.echo(f"Error: Could not find app '{app_name}' in {base_path} or any subfolder.")
            return 1
    
    viewsets_py_path = app_path / 'viewsets.py'
    viewsets_folder_path = app_path / 'viewsets'

    # Check for conflicting files/folders first
    if viewsets_py_path.exists() and viewsets_folder_path.exists():
        raise click.ClickException(
            "Both 'viewsets.py' and 'viewsets/' folder exist. Please remove one before proceeding."
        )
    
    # Handle class_dict case
    if class_dict:
        if viewsets_py_path.exists():
            imports = class_dict.get("imports", "")
            viewset_content = class_dict.get(viewset_name, "")
            full_content = imports + "\n\n" + viewset_content
            inject_element_into_file(viewsets_py_path, full_content)
        else:
            # Create viewsets folder if needed
            viewsets_folder_path.mkdir(parents=True, exist_ok=True)
            
            # Set up paths
            if path:
                custom_viewset_path = viewsets_folder_path / Path(path)
                custom_viewset_path.mkdir(parents=True, exist_ok=True)
            else:
                custom_viewset_path = viewsets_folder_path

            viewset_file_name = f"{snake_case(viewset_name)}.py"
            viewset_file_path = custom_viewset_path / viewset_file_name
            init_file_path = custom_viewset_path / '__init__.py'

            imports = class_dict.get("imports", "")
            viewset_content = class_dict.get(viewset_name, "")
            full_content = imports + "\n\n" + viewset_content
            create_element_file(viewset_file_path, full_content)
            add_import_to_file(init_file_path, viewset_name, viewset_file_name)

        click.echo(f"Viewset '{viewset_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    viewset_template_path = templates_path / 'viewset_template.txt'
    viewset_content = render_template(viewset_template_path, viewset_name=viewset_name)
    viewset_template_path_no_import = templates_path / 'viewset_template_no_import.txt'
    viewset_content_no_import = render_template(viewset_template_path_no_import, viewset_name=viewset_name)

    if viewsets_py_path.exists():
        if is_import_in_file(viewsets_py_path, 'from rest_framework import viewsets'):
            inject_element_into_file(viewsets_py_path, viewset_content_no_import)
        else:
            inject_element_into_file(viewsets_py_path, viewset_content)
    else:
        # Create viewsets folder and files
        viewsets_folder_path.mkdir(parents=True, exist_ok=True)

        if path:
            custom_viewset_path = viewsets_folder_path / Path(path)
            custom_viewset_path.mkdir(parents=True, exist_ok=True)
        else:
            custom_viewset_path = viewsets_folder_path

        viewset_file_name = f"{snake_case(viewset_name)}.py"
        viewset_file_path = custom_viewset_path / viewset_file_name
        init_file_path = custom_viewset_path / '__init__.py'

        create_element_file(viewset_file_path, viewset_content)
        add_import_to_file(init_file_path, viewset_name, viewset_file_name)

    click.echo(f"Viewset '{viewset_name}' created successfully in app '{app_name}'.")
    return 0