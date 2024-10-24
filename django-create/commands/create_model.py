import click
import os
from ..utils import render_template, save_rendered_template

@click.command(name='model')
@click.argument('app_name')
@click.argument('model_name')
def create_model(app_name, model_name):
    """
    Create a new Django model in the specified app.

    Example:
        django-create create model myapp MyModel
    """
    click.echo(f"Creating model '{model_name}' in app '{app_name}'...")

    # Define the base path for the app
    base_path = os.path.join(os.getcwd(), app_name, 'models')
    if not os.path.exists(base_path):
        click.echo(f"Error: The app '{app_name}' does not have a 'models' directory.")
        return

    # Define the path to the model template
    templates_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
    model_template_path = os.path.join(templates_path, 'model_template.txt')

    # Render the model template with the model name
    model_content = render_template(model_template_path, model_name=model_name)

    # Define the output path for the model file
    output_path = os.path.join(base_path, f'{model_name.lower()}.py')

    # Save the rendered model content
    save_rendered_template(model_content, output_path)

    click.echo(f"Model '{model_name}' created successfully in '{output_path}'.")
