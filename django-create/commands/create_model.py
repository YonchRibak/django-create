import click
import os
from ..utils import render_template, save_rendered_template

@click.command()
@click.argument('app_name')
@click.argument('model_name')
@click.option('--fields', '-f', multiple=True, help="Specify model fields (e.g., name=CharField max_length=100).")
def create_model(app_name, model_name, fields):
    """
    Create a new Django model in the specified app.

    Example:
        django-create create_model myapp MyModel --fields name=CharField max_length=100 age=IntegerField
    """
    click.echo(f"Creating model '{model_name}' in app '{app_name}'...")

    # Define the base path for the app
    base_path = os.path.join(os.getcwd(), app_name, 'models')
    if not os.path.exists(base_path):
        click.echo(f"Error: The app '{app_name}' does not have a 'models' directory.")
        return

    # Parse the fields provided by the user
    fields_content = ""
    for field in fields:
        # Split the field definition (e.g., "name=CharField max_length=100")
        parts = field.split(' ')
        field_name, field_type = parts[0].split('=')
        field_args = ' '.join(parts[1:]) if len(parts) > 1 else ""
        fields_content += f"    {field_name} = models.{field_type}({field_args})\n"

    # Default field content if no fields are provided
    if not fields_content:
        fields_content = "    # Add your fields here\n    name = models.CharField(max_length=100)\n"

    # Define the path to the model template
    templates_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
    model_template_path = os.path.join(templates_path, 'model_template.txt')

    # Render the model template with the model name and fields
    model_content = render_template(model_template_path, model_name=model_name, fields=fields_content)

    # Define the output path for the model file
    output_path = os.path.join(base_path, f'{model_name.lower()}.py')

    # Save the rendered model content
    save_rendered_template(model_content, output_path)

    click.echo(f"Model '{model_name}' created successfully in '{output_path}'.")
