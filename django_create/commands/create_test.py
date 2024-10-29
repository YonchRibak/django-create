import click
from pathlib import Path
import os
from ..utils import (
    Utils,
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    render_template,
    is_import_in_file,
    modify_import_statement_to_double_dot
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
    class_dict = ctx.obj.get('class_dict', None)

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
        
    tests_py_path = app_path / 'tests.py'
    tests_folder_path = app_path / 'tests'
    
    # Determine the path for the test file based on the optional --path flag
    if path:
        custom_test_path = tests_folder_path / Path(path)
    else:
        custom_test_path = tests_folder_path

    # Construct the file paths - note the test_ prefix
    test_file_name = f"test_{snake_case(test_name)}.py"
    test_file_path = custom_test_path / test_file_name
    init_file_path = custom_test_path / '__init__.py'

    # Handle class_dict case
    if class_dict:
        if tests_py_path.exists():
            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            test_content = class_dict.get(test_name, "")
            full_content = imports + "\n\n" + test_content
            inject_element_into_file(tests_py_path, full_content)
        else:
            # Create tests folder if needed
            tests_folder_path.mkdir(parents=True, exist_ok=True)
            
            # Set up paths
            if path:
                custom_test_path.mkdir(parents=True, exist_ok=True)

            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            test_content = class_dict.get(test_name, "")
            full_content = imports + "\n\n" + test_content
            create_element_file(test_file_path, full_content)
            add_import_to_file(init_file_path, test_name, test_file_name)

        click.echo(f"test '{test_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    test_template_path = templates_path / 'test_template.txt'
    test_template_no_import_path = templates_path / 'test_template_no_import.txt'
    test_content = render_template(test_template_path, test_name=test_name)
    test_content_no_import = render_template(test_template_no_import_path, test_name=test_name)
    
    if tests_py_path.exists() and not tests_folder_path.exists():
        if Utils.is_default_content(tests_py_path, 'tests'):
            # If only default content exists, overwrite the file
            with open(tests_py_path, 'w') as f:
                f.write(test_content)
        else:
            # File has actual tests, check for import
            if is_import_in_file(tests_py_path, Utils.DJANGO_IMPORTS['tests']):
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
    return 0