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

@click.command(name='test')
@click.argument('test_name')
@click.option('--path', default=None, help="Subdirectory path inside the tests folder.")
@click.pass_context
def create_test(ctx, test_name, path):
    """
    Create a new Django test in the specified app.

    Example:
        django-create myapp create test SomeTest --path products/some_other_folder
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
        
    tests_py_path = app_path / 'tests.py'
    tests_folder_path = app_path / 'tests'
    
    # Determine the path for the test file based on the optional --path flag
    if path:
        custom_test_path = tests_folder_path / Path(path)
    else:
        custom_test_path = tests_folder_path

    # Construct the file paths
    test_file_name = f"{snake_case(test_name)}.py"
    test_file_path = custom_test_path / test_file_name
    init_file_path = custom_test_path / '__init__.py'

    # Define the path to the test template
    templates_path = Path(__file__).parent.parent / 'templates'
    test_template_path = templates_path / 'test_template.txt'
    test_content = render_template(test_template_path, test_name=test_name)
    test_template_path_no_import = templates_path / 'test_template_no_import.txt'
    test_content_no_import = render_template(test_template_path_no_import, test_name=test_name)

    if tests_py_path.exists() and not tests_folder_path.exists():
        if is_import_in_file(tests_py_path,'from django.test import TestCase'):
            inject_element_into_file(tests_py_path, test_content_no_import)
        else:
            inject_element_into_file(tests_py_path, test_content)
    elif tests_folder_path.exists() and not tests_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_test_path.mkdir(parents=True, exist_ok=True)

        # Create the test file inside the specified or default folder
        create_element_file(test_file_path, test_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, test_name, test_file_name)
    elif tests_py_path.exists() and tests_folder_path.exists():
        raise click.ClickException(
            "Both 'tests.py' and 'tests/' folder exist. Please remove one before proceeding."
    )
    else:
        raise click.ClickException(
            "Neither 'tests.py' nor 'tests/' folder exists. Please create one before proceeding."
        )

    click.echo(f"test '{test_name}' created successfully in app '{app_name}'.")
