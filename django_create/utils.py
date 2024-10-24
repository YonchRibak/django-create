import os
import re
import click

def render_template(template_path, **kwargs):
    """
    Reads a template file and replaces placeholders with provided values.
    """
    with open(template_path, 'r') as file:
        content = file.read()

    # Replace placeholders in the content with the provided keyword arguments
    for key, value in kwargs.items():
        placeholder = f"{{{{ {key} }}}}"
        content = content.replace(placeholder, value)

    return content

def save_rendered_template(content, output_path):
    """
    Saves rendered template content to the specified output path.
    """
    with open(output_path, 'w') as file:
        file.write(content)

def snake_case(name):
    """Converts CamelCase names to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

def inject_element_into_file(file_path, element_content):
    """
    Injects the given element content into an existing file without altering other content.
    
    Used for adding a new model, view, or serializer to an existing file like models.py.
    """
    with open(file_path, 'a') as f:
        f.write("\n\n" + element_content)

    click.echo(f"Injected content into '{file_path}'.")

def create_element_file(element_file_path, element_content):
    """
    Creates a new file with the given element content.
    
    Used for creating a model, view, or serializer file in a specified directory.
    """
    save_rendered_template(element_content, element_file_path)
    click.echo(f"File created at '{element_file_path}'.")

def add_import_to_file(init_file_path, element_name, element_file_name):
    """
    Adds an import statement to a specified file (e.g., models/__init__.py) for the new element.
    
    Can be used to add imports for models, views, serializers, etc.
    """
    import_statement = f"from .{element_file_name[:-3]} import {element_name}\n"
    
    # Ensure __init__.py exists
    os.makedirs(os.path.dirname(init_file_path), exist_ok=True)
    if not os.path.exists(init_file_path):
        with open(init_file_path, 'w') as f:
            f.write("# Imports for Django elements\n")

    # Check if the import already exists
    with open(init_file_path, 'r') as f:
        init_content = f.read()

    if import_statement not in init_content:
        with open(init_file_path, 'a') as f:
            f.write(import_statement)
        click.echo(f"Added import to '{init_file_path}': {import_statement.strip()}")