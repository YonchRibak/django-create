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

@click.command(name='serializer')
@click.argument('serializer_name')
@click.option('--path', default=None, help="Subdirectory path inside the serializers folder.")
@click.pass_context
def create_serializer(ctx, serializer_name, path):
    """
    Create a new Django serializer in the specified app.

    Example:
        django-create myapp create serializer SomeSerializer --path products/some_other_folder
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
            return
        
    serializers_py_path = app_path / 'serializers.py'
    serializers_folder_path = app_path / 'serializers'
    
    # Determine the path for the serializer file based on the optional --path flag
    if path:
        custom_serializer_path = serializers_folder_path / Path(path)
    else:
        custom_serializer_path = serializers_folder_path

    # Construct the file paths
    serializer_file_name = f"{snake_case(serializer_name)}.py"
    serializer_file_path = custom_serializer_path / serializer_file_name
    init_file_path = custom_serializer_path / '__init__.py'

    # Write serializers from class_dict if provided
    if class_dict:
        print(f"Debug: Received class_dict: {class_dict}")  # Temporary for debug
        imports = class_dict.get("imports", "")
        serializer_content = class_dict.get(serializer_name, "")
        full_content = imports + "\n\n" + serializer_content
        create_element_file(serializer_file_path, full_content)
    
        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, serializer_name, serializer_file_name)

        return
    
    # Define the path to the serializer template
    templates_path = Path(__file__).parent.parent / 'templates'
    serializer_template_path = templates_path / 'serializer_template.txt'
    serializer_content = render_template(serializer_template_path, serializer_name=serializer_name)
    serializer_template_no_import_path = templates_path / 'serializer_template_no_import.txt'
    serializer_content_no_import = render_template(serializer_template_no_import_path, serializer_name=serializer_name)


    if serializers_py_path.exists() and not serializers_folder_path.exists():
        if is_import_in_file(serializers_py_path, 'from rest_framework import serializers'):
            inject_element_into_file(serializers_py_path, serializer_content_no_import)
        else:
            inject_element_into_file(serializers_py_path, serializer_content)
    elif serializers_folder_path.exists() and not serializers_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_serializer_path.mkdir(parents=True, exist_ok=True)

        # Create the serializer file inside the specified or default folder
        create_element_file(serializer_file_path, serializer_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, serializer_name, serializer_file_name)
    elif serializers_py_path.exists() and serializers_folder_path.exists():
        raise click.ClickException(
            "Both 'serializers.py' and 'serializers/' folder exist. Please remove one before proceeding."
    )
    else:
        raise click.ClickException(
            "Neither 'serializers.py' nor 'serializers/' folder exists. Please create one before proceeding."
        )

    click.echo(f"serializer '{serializer_name}' created successfully in app '{app_name}'.")
