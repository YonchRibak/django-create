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

@click.command(name='model')
@click.argument('model_name')
@click.option('--path', default=None, help="Subdirectory path inside the models folder.")
@click.pass_context
def create_model(ctx, model_name, path):
    """
    Create a new Django model in the specified app.

    Example:
        django-create myapp create model SomeModel --path products/some_other_folder
    """
    app_name = ctx.obj['app_name']
    click.echo(f"Creating model '{model_name}' in app '{app_name}'...")

    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name
    models_py_path = app_path / 'models.py'
    models_folder_path = app_path / 'models'
    
    # Determine the path for the model file based on the optional --path flag
    if path:
        custom_model_path = models_folder_path / Path(path)
    else:
        custom_model_path = models_folder_path

    # Construct the file paths
    model_file_name = f"{snake_case(model_name)}.py"
    model_file_path = custom_model_path / model_file_name
    init_file_path = custom_model_path / '__init__.py'

    # Define the path to the model template
    templates_path = Path(__file__).parent.parent / 'templates'
    model_template_path = templates_path / 'model_template.txt'
    model_content = render_template(model_template_path, model_name=model_name)

    # Check for existence of models.py and the models folder
    click.echo(f"Checking existence of 'models.py': {models_py_path.exists()}")
    click.echo(f"Checking existence of 'models/' folder: {models_folder_path.exists()}")

    if models_py_path.exists() and not models_folder_path.exists():
        click.echo("Injecting model into 'models.py'...")
        inject_element_into_file(models_py_path, model_content)
    elif models_folder_path.exists() and not models_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_model_path.mkdir(parents=True, exist_ok=True)

        # Create the model file inside the specified or default folder
        click.echo(f"Creating model file '{model_file_name}' inside the specified path...")
        create_element_file(model_file_path, model_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, model_name, model_file_name)
    elif models_py_path.exists() and models_folder_path.exists():
        click.echo(f"Checking existence of 'models.py': {models_py_path.exists()}")
        click.echo(f"Checking existence of 'models/' folder: {models_folder_path.exists()}")
        raise click.ClickException(
            "Both 'models.py' and 'models/' folder exist. Please remove one before proceeding."
    )
    else:
        raise click.ClickException(
            "Neither 'models.py' nor 'models/' folder exists. Please create one before proceeding."
        )

    click.echo(f"Model '{model_name}' created successfully in app '{app_name}'.")
