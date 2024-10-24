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
    """
    Converts CamelCase names to snake_case.
    Handles cases with multiple consecutive uppercase letters correctly.
    """
    # Add an underscore between a lowercase and an uppercase letter
    name = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', name)
    # Add an underscore before sequences of uppercase letters followed by a lowercase letter
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    return name.lower()

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

def create_mock_django_app(
    tmp_path, 
    app_name='myapp', 
    with_models_file=True, 
    with_models_folder=False, 
    with_views_folder=False, 
    with_viewsets_folder=False, 
    with_serializers_folder=False, 
    with_tests_folder=False
):
    """
    Creates a mock Django app directory structure for testing.
    
    Parameters:
    - tmp_path: A pytest fixture for creating temporary directories.
    - app_name: The name of the mock Django app.
    - with_models_file: Whether to include a models.py file in the app.
    - with_models_folder: Whether to include a models/ folder in the app.
    - with_views_folder: Whether to include a views/ folder in the app.
    - with_viewsets_folder: Whether to include a viewsets/ folder in the app.
    - with_serializers_folder: Whether to include a serializers/ folder in the app.
    - with_tests_folder: Whether to include a tests/ folder in the app.
    
    Returns:
    - Path to the mock app.
    """
    app_path = tmp_path / app_name
    app_path.mkdir(parents=True, exist_ok=True)

    # Create models.py if requested
    if with_models_file:
        models_py = app_path / 'models.py'
        models_py.write_text("# models.py file for testing\n")

    # Create models folder if requested
    if with_models_folder:
        models_folder = app_path / 'models'
        models_folder.mkdir(parents=True, exist_ok=True)
        (models_folder / '__init__.py').write_text("# models/__init__.py for testing\n")

    # Create views folder if requested
    if with_views_folder:
        views_folder = app_path / 'views'
        views_folder.mkdir(parents=True, exist_ok=True)
        (views_folder / '__init__.py').write_text("# views/__init__.py for testing\n")

    # Create viewsets folder if requested
    if with_viewsets_folder:
        viewsets_folder = app_path / 'viewsets'
        viewsets_folder.mkdir(parents=True, exist_ok=True)
        (viewsets_folder / '__init__.py').write_text("# viewsets/__init__.py for testing\n")

    # Create serializers folder if requested
    if with_serializers_folder:
        serializers_folder = app_path / 'serializers'
        serializers_folder.mkdir(parents=True, exist_ok=True)
        (serializers_folder / '__init__.py').write_text("# serializers/__init__.py for testing\n")

    # Create tests folder if requested
    if with_tests_folder:
        tests_folder = app_path / 'tests'
        tests_folder.mkdir(parents=True, exist_ok=True)
        (tests_folder / '__init__.py').write_text("# tests/__init__.py for testing\n")
        (tests_folder / 'test_sample.py').write_text("# Sample test file for testing\n")

    return app_path