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
  

    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name
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

    # Define the path to the serializer template
    templates_path = Path(__file__).parent.parent / 'templates'
    serializer_template_path = templates_path / 'serializer_template.txt'
    serializer_content = render_template(serializer_template_path, serializer_name=serializer_name)


    if serializers_py_path.exists() and not serializers_folder_path.exists():
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
