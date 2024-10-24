import click
import os
from ..utils import (
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    render_template
)

@click.command(name='model')
@click.argument('app_name')
@click.argument('model_name')
def create_model(app_name, model_name):
    """
    Create a new Django model in the specified app.

    Example:
        django-create create model myapp ProductCustomFields
    """
    click.echo(f"Creating model '{model_name}' in app '{app_name}'...")

    # Define paths
    app_path = os.path.join(os.getcwd(), app_name)
    models_py_path = os.path.join(app_path, 'models.py')
    models_folder_path = os.path.join(app_path, 'models')
    model_file_name = f"{snake_case(model_name)}_model.py"
    model_file_path = os.path.join(models_folder_path, model_file_name)
    init_file_path = os.path.join(models_folder_path, '__init__.py')

    # Define the path to the model template
    templates_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
    model_template_path = os.path.join(templates_path, 'model_template.txt')
    model_content = render_template(model_template_path, model_name=model_name)

    # Check if models.py exists and models folder does not exist
    if os.path.exists(models_py_path) and not os.path.exists(models_folder_path):
        click.echo("Injecting model into 'models.py'...")
        inject_element_into_file(models_py_path, model_content)
    else:
        # Ensure the models folder exists
        os.makedirs(models_folder_path, exist_ok=True)
        
        # Create the model file inside the models folder
        click.echo(f"Creating model file '{model_file_name}' inside the 'models' folder...")
        create_element_file(model_file_path, model_content)

        # Add import to __init__.py
        add_import_to_file(init_file_path, model_name, model_file_name)

    click.echo(f"Model '{model_name}' created successfully in app '{app_name}'.")
